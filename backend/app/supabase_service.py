from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def _rest_headers() -> dict[str, str]:
    key = settings.supabase_key
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
    }


def _get_json(path: str, params: dict[str, str]) -> list[dict[str, Any]]:
    base = settings.supabase_url.rstrip("/")
    url = f"{base}/rest/v1/{path}"
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.get(url, headers=_rest_headers(), params=params)
            r.raise_for_status()
            data = r.json()
            return list(data) if isinstance(data, list) else []
    except Exception as e:
        logger.exception("Supabase REST request failed: %s", e)
        return []


def fetch_mentors() -> list[dict[str, Any]]:
    if not settings.supabase_url or not settings.supabase_key:
        logger.warning("Supabase URL or key missing; using empty catalogs.")
        return []
    return _get_json(
        "mentors",
        {"select": "*", "is_active": "eq.true", "limit": "50"},
    )


def fetch_jobs() -> list[dict[str, Any]]:
    if not settings.supabase_url or not settings.supabase_key:
        return []
    return _get_json(
        "jobs",
        {"select": "*", "is_open": "eq.true", "limit": "50"},
    )


def seed_catalog_if_empty() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """In-memory demo data when Supabase is not configured or tables are empty."""
    mentors = [
        {
            "id": "demo-m1",
            "name": "Aisha Okonkwo",
            "title": "Director of UX Research, Health Tech",
            "bio": "Former clinician turned researcher; as a woman of color in tech, I mentor career pivots, portfolio reviews, and navigating imposter syndrome in male-dominated fields.",
            "expertise": ["ux research", "health tech", "career pivot", "interviews", "diversity", "imposter syndrome"],
            "industry_tags": ["healthcare", "saas"],
        },
        {
            "id": "demo-m2",
            "name": "Marina Volkov",
            "title": "Staff Backend Engineer",
            "bio": "Backend engineering lead who advocates for women in tech; specializes in distributed systems, interview prep, and building confidence in technical leadership roles.",
            "expertise": ["backend", "python", "system design", "new grad", "leadership", "confidence building"],
            "industry_tags": ["fintech", "enterprise"],
        },
        {
            "id": "demo-m3",
            "name": "Priya Desai",
            "title": "Group PM, Fintech",
            "bio": "Returned from parental leave as a senior woman in tech; focuses on flexible remote paths, work-life balance, and helping other women advance in product management careers.",
            "expertise": ["product management", "fintech", "remote work", "parental leave", "work-life balance"],
            "industry_tags": ["fintech"],
        },
    ]
    jobs = [
        {
            "id": "demo-j1",
            "title": "UX Researcher II",
            "company": "Northwind Health",
            "location": "Remote (US)",
            "employment_type": "Full-time",
            "summary": "Women-led health tech company seeking diverse perspectives for clinician workflow studies. Flexible remote work, comprehensive benefits, and commitment to work-life balance. Cross-functional collaboration with design and PM teams.",
            "skill_tags": ["ux research", "healthcare", "mixed methods", "remote work", "diversity"],
            "industry": "health tech",
        },
        {
            "id": "demo-j2",
            "title": "Backend Engineer",
            "company": "Riverbank Labs",
            "location": "Hybrid · NYC",
            "employment_type": "Full-time",
            "summary": "Inclusive fintech startup building Python services with modern architecture. Strong focus on diversity and inclusion, with dedicated mentorship programs and flexible hybrid work options. Active in supporting women in engineering careers.",
            "skill_tags": ["python", "backend", "distributed systems", "mentorship", "inclusion"],
            "industry": "fintech",
        },
        {
            "id": "demo-j3",
            "title": "Senior Product Manager",
            "company": "Cedar Payments",
            "location": "Remote",
            "employment_type": "Full-time",
            "summary": "Women-founded payments company prioritizing work-life balance and family-friendly policies. Fully remote with unlimited PTO, parental leave, and career development support. Partner with compliance and design teams on customer experience innovation.",
            "skill_tags": ["product management", "fintech", "remote", "work-life balance", "parental support"],
            "industry": "fintech",
        },
    ]
    return mentors, jobs
