from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    message: str = Field(..., min_length=3, max_length=8000)


class MentorMatch(BaseModel):
    id: str
    name: str
    title: str
    expertise: list[str]
    bio: str
    match_score: float
    match_reason: str


class JobMatch(BaseModel):
    id: str
    title: str
    company: str
    location: str
    type: str
    summary: str
    match_reason: str


class MatchResponse(BaseModel):
    summary: str
    interpreted_goals: list[str]
    skills: list[str]
    industry_focus: str | None
    mentors: list[MentorMatch]
    jobs: list[JobMatch]
    next_steps: list[str]
