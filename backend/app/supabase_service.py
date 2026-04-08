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
            "bio": "Former clinician turned researcher; mentors career pivots and portfolio reviews.",
            "expertise": ["ux research", "health tech", "career pivot", "interviews"],
            "industry_tags": ["healthcare", "saas"],
        },
        {
            "id": "demo-m2",
            "name": "Marina Volkov",
            "title": "Staff Backend Engineer",
            "bio": "Backend, distributed systems, and interview loops at product companies.",
            "expertise": ["backend", "python", "system design", "new grad"],
            "industry_tags": ["fintech", "enterprise"],
        },
        {
            "id": "demo-m3",
            "name": "Priya Desai",
            "title": "Group PM, Fintech",
            "bio": "Returned from parental leave; focuses on flexible remote paths for PMs.",
            "expertise": ["product management", "fintech", "remote work", "parental leave"],
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
            "summary": "Mixed-methods studies for clinician workflows; cross-functional with design and PM.",
            "skill_tags": ["ux research", "healthcare", "mixed methods"],
            "industry": "health tech",
        },
        {
            "id": "demo-j2",
            "title": "Backend Engineer",
            "company": "Riverbank Labs",
            "location": "Hybrid · NYC",
            "employment_type": "Full-time",
            "summary": "Python services, event-driven architecture, mentoring interns.",
            "skill_tags": ["python", "backend", "distributed systems"],
            "industry": "saas",
        },
        {
            "id": "demo-j3",
            "title": "Senior Product Manager",
            "company": "Cedar Payments",
            "location": "Remote",
            "employment_type": "Full-time",
            "summary": "Payments roadmap; partner with compliance and design on customer journeys.",
            "skill_tags": ["product management", "fintech", "remote"],
            "industry": "fintech",
        },
    ]
    return mentors, jobs
