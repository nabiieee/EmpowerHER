from __future__ import annotations

import re
import logging
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from app.config import settings
from app.supabase_service import fetch_jobs, fetch_mentors, seed_catalog_if_empty, log_match_request

logger = logging.getLogger(__name__)


class IntentSchema(BaseModel):
    goals: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    industry_focus: str | None = None
    seniority: str | None = None


class EmpowerState(TypedDict, total=False):
    user_message: str
    parsed: dict[str, Any]
    mentors_catalog: list[dict[str, Any]]
    jobs_catalog: list[dict[str, Any]]
    mentors_ranked: list[dict[str, Any]]
    jobs_ranked: list[dict[str, Any]]
    summary: str
    next_steps: list[str]
    response: dict[str, Any]


KEYWORD_MAP = {
    "ux": ["ux", "user experience", "design", "research", "ui"],
    "product": ["product manager", "pm", "product management", "roadmap"],
    "backend": ["backend", "api", "distributed", "python", "java", "go"],
    "frontend": ["frontend", "react", "javascript", "web"],
    "data": ["data science", "analytics", "ml", "machine learning"],
    "health": ["health", "healthcare", "clinical", "medical"],
    "fintech": ["fintech", "finance", "payments", "banking"],
    "remote": ["remote", "flexible", "work from home"],
    "interview": ["interview", "prep", "leetcode", "loop"],
    "new grad": ["new grad", "graduate", "bootcamp", "intern"],
    "parental": ["parental", "returning", "leave", "caregiver"],
}


def _heuristic_intent(message: str) -> dict[str, Any]:
    lower = message.lower()
    skills: set[str] = set()
    for skill, needles in KEYWORD_MAP.items():
        if any(n in lower for n in needles):
            skills.add(skill)
    goals: list[str] = []
    if "mentor" in lower or "guide" in lower or "coach" in lower:
        goals.append("Find a supportive mentor")
    if "job" in lower or "role" in lower or "hire" in lower or "opportunit" in lower:
        goals.append("Discover aligned job opportunities")
    if "pivot" in lower or "transition" in lower or "switch" in lower:
        goals.append("Navigate a career transition")
    if not goals:
        goals = ["Clarify next career moves", "Build confidence and network"]
    industry = None
    for ind in ("health tech", "healthcare", "fintech", "saas", "enterprise"):
        if ind.replace(" ", "") in lower.replace(" ", "") or ind in lower:
            industry = ind
            break
    return {
        "goals": goals[:5],
        "skills": sorted(skills)[:12],
        "industry_focus": industry,
        "seniority": None,
    }


def _llm_parse_intent(message: str) -> dict[str, Any]:
    if not settings.openai_api_key:
        return _heuristic_intent(message)
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=0.2,
        )
        structured = llm.with_structured_output(IntentSchema)
        sys = SystemMessage(
            content=(
                "You extract structured career intent for women seeking mentorship and jobs. "
                "Infer goals, transferable skills signals, likely industry focus, and seniority if stated. "
                "Keep goals short (under 8 words each). Skills should be lowercase tokens like 'ux research', "
                "'python', 'product management'."
            )
        )
        out: IntentSchema = structured.invoke([sys, HumanMessage(content=message)])
        return {
            "goals": out.goals,
            "skills": out.skills,
            "industry_focus": out.industry_focus,
            "seniority": out.seniority,
        }
    except Exception:
        logger.exception("LLM intent parse failed; falling back to heuristic")
        return _heuristic_intent(message)


def node_understand(state: EmpowerState) -> dict[str, Any]:
    msg = state["user_message"]
    parsed = _llm_parse_intent(msg)
    return {"parsed": parsed}


def node_load_catalog(state: EmpowerState) -> dict[str, Any]:
    mentors = fetch_mentors()
    jobs = fetch_jobs()
    demo_m, demo_j = seed_catalog_if_empty()
    if not mentors and not jobs:
        mentors, jobs = demo_m, demo_j
    else:
        if not mentors:
            mentors = demo_m
        if not jobs:
            jobs = demo_j
    return {"mentors_catalog": mentors, "jobs_catalog": jobs}


def _norm_tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return set(words)


def _score_record(parsed: dict[str, Any], text_blobs: list[str], tag_lists: list[list[str]]) -> float:
    skill_tokens: set[str] = set()
    for s in parsed.get("skills") or []:
        skill_tokens.update(_norm_tokens(s))
    goal_blob = " ".join(parsed.get("goals") or [])
    skill_tokens |= _norm_tokens(goal_blob)
    if parsed.get("industry_focus"):
        skill_tokens |= _norm_tokens(parsed["industry_focus"])

    corpus = " ".join(text_blobs).lower()
    tag_flat = [t.lower() for sub in tag_lists for t in (sub or [])]

    score = 0.0
    for t in skill_tokens:
        if len(t) < 3:
            continue
        if t in corpus:
            score += 1.0
        for tag in tag_flat:
            if t in tag or tag in t:
                score += 0.75
    return score


def _mentor_reason(parsed: dict[str, Any], m: dict[str, Any], score: float) -> str:
    overlap = [s for s in (parsed.get("skills") or []) if s.lower() in json_blob(m).lower()]
    if overlap:
        return f"Strong overlap on {', '.join(overlap[:3])}."
    if parsed.get("industry_focus") and parsed["industry_focus"].lower() in json_blob(m).lower():
        return f"Experience in {parsed['industry_focus']} aligns with your direction."
    return "Background complements your stated goals and growth areas."


def _job_reason(parsed: dict[str, Any], j: dict[str, Any], score: float) -> str:
    tags = " ".join(j.get("skill_tags") or []).lower()
    hits = [s for s in (parsed.get("skills") or []) if s.lower() in tags]
    if hits:
        return f"Role emphasizes {', '.join(hits[:3])}, matching your profile."
    return "Responsibilities map well to the trajectory you described."


def json_blob(d: dict[str, Any]) -> str:
    parts = [str(v) for v in d.values() if isinstance(v, (str, int, float))]
    for k in ("expertise", "industry_tags", "skill_tags"):
        if k in d and d[k]:
            parts.append(" ".join(str(x) for x in d[k]))
    return " ".join(parts).lower()


def node_rank(state: EmpowerState) -> dict[str, Any]:
    parsed = state["parsed"]
    mentors_scored: list[tuple[float, dict[str, Any]]] = []
    for m in state.get("mentors_catalog") or []:
        text_blobs = [m.get("title") or "", m.get("bio") or "", m.get("name") or ""]
        tag_lists = [list(m.get("expertise") or []), list(m.get("industry_tags") or [])]
        s = _score_record(parsed, text_blobs, tag_lists)
        mentors_scored.append((s, m))
    mentors_scored.sort(key=lambda x: x[0], reverse=True)

    jobs_scored: list[tuple[float, dict[str, Any]]] = []
    for j in state.get("jobs_catalog") or []:
        text_blobs = [
            j.get("title") or "",
            j.get("summary") or "",
            j.get("company") or "",
            j.get("industry") or "",
        ]
        tag_lists = [list(j.get("skill_tags") or [])]
        s = _score_record(parsed, text_blobs, tag_lists)
        jobs_scored.append((s, j))
    jobs_scored.sort(key=lambda x: x[0], reverse=True)

    def norm_score(raw: float, cap: float = 8.0) -> float:
        return max(0.15, min(1.0, raw / cap))

    mentors_ranked: list[dict[str, Any]] = []
    for raw, m in mentors_scored[:5]:
        mid = str(m.get("id", ""))
        mentors_ranked.append(
            {
                "id": mid,
                "name": m.get("name") or "Guide",
                "title": m.get("title") or "",
                "expertise": list(m.get("expertise") or []),
                "bio": m.get("bio") or "",
                "match_score": norm_score(raw + 0.5),
                "match_reason": _mentor_reason(parsed, m, raw),
            }
        )

    jobs_ranked = []
    for raw, j in jobs_scored[:5]:
        jid = str(j.get("id", ""))
        jobs_ranked.append(
            {
                "id": jid,
                "title": j.get("title") or "Role",
                "company": j.get("company") or "",
                "location": j.get("location") or "",
                "type": j.get("employment_type") or "Full-time",
                "summary": j.get("summary") or "",
                "match_score": norm_score(raw + 0.5),
                "match_reason": _job_reason(parsed, j, raw),
            }
        )

    return {"mentors_ranked": mentors_ranked, "jobs_ranked": jobs_ranked}


def _llm_finalize(
    user_message: str,
    parsed: dict[str, Any],
    mentors: list[dict[str, Any]],
    jobs: list[dict[str, Any]],
) -> tuple[str, list[str]]:
    if not settings.openai_api_key:
        g = ", ".join(parsed.get("goals") or []) or "your next chapter"
        summary = (
            f"We read your message and centered on {g}. "
            f"Below are mentors and roles that line up with your skills signals and industry focus."
        )
        steps = [
            "Book a short intro chat with a mentor whose expertise matches your top skill gap.",
            "Tailor your resume bullets to mirror language from the closest job description.",
            "Send one thoughtful outreach note referencing a specific project or product area.",
        ]
        return summary, steps
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=0.4,
        )
        sys = SystemMessage(
            content=(
                "You are EmpowerHer's assistant. Write a warm, concise summary (2–3 sentences) and "
                "3 actionable next steps for a woman using a mentorship and jobs matcher. "
                "Return exactly two sections: SUMMARY: ... then STEPS: bullet lines with leading dashes."
            )
        )
        human = HumanMessage(
            content=(
                f"User message:\n{user_message}\n\n"
                f"Parsed goals: {parsed.get('goals')}\n"
                f"Skills signals: {parsed.get('skills')}\n"
                f"Industry focus: {parsed.get('industry_focus')}\n"
                f"Top mentors: {[m.get('name') for m in mentors[:3]]}\n"
                f"Top jobs: {[j.get('title') for j in jobs[:3]]}\n"
            )
        )
        text = llm.invoke([sys, human]).content
        summary_part = text
        steps: list[str] = []
        if "STEPS:" in text:
            summary_part, rest = text.split("STEPS:", 1)
            for line in rest.splitlines():
                line = line.strip()
                if line.startswith("-"):
                    steps.append(line.lstrip("- ").strip())
        summary = summary_part.replace("SUMMARY:", "").strip()
        if not steps:
            steps = [
                "Pick one mentor and propose a 20-minute intro focused on a single question.",
                "Shortlist two jobs and map your achievements to their must-have skills.",
                "Block time this week for one networking coffee or voice note outreach.",
            ]
        return summary, steps[:5]
    except Exception:
        logger.exception("LLM finalize failed; using template copy")
        g = ", ".join(parsed.get("goals") or []) or "your next chapter"
        summary = (
            f"We centered on {g}. Here are mentors and roles aligned with what you shared — "
            "review the fit notes and pick one conversation to start this week."
        )
        return summary, [
            "Reach out to your top mentor match with a specific ask.",
            "Refresh your headline and summary to reflect your target role.",
            "Apply to one role this week and ask a mentor for a referral angle.",
        ]


def node_finalize(state: EmpowerState) -> dict[str, Any]:
    parsed = state["parsed"]
    mentors = state.get("mentors_ranked") or []
    jobs = state.get("jobs_ranked") or []
    summary, next_steps = _llm_finalize(state["user_message"], parsed, mentors, jobs)
    response = {
        "summary": summary,
        "interpreted_goals": list(parsed.get("goals") or []),
        "skills": list(parsed.get("skills") or []),
        "industry_focus": parsed.get("industry_focus"),
        "mentors": mentors,
        "jobs": [{k: v for k, v in j.items() if k != "match_score"} for j in jobs],
        "next_steps": next_steps,
    }
    return {"summary": summary, "next_steps": next_steps, "response": response}


def build_graph():
    g = StateGraph(EmpowerState)
    g.add_node("understand", node_understand)
    g.add_node("load_catalog", node_load_catalog)
    g.add_node("rank", node_rank)
    g.add_node("finalize", node_finalize)
    g.add_edge(START, "understand")
    g.add_edge("understand", "load_catalog")
    g.add_edge("load_catalog", "rank")
    g.add_edge("rank", "finalize")
    g.add_edge("finalize", END)
    return g.compile()


def run_match_workflow(user_message: str) -> dict[str, Any]:
    # Log the match request for analytics
    log_match_request(user_message)

    graph = build_graph()
    out = graph.invoke({"user_message": user_message})
    return out["response"]
