"""JMC-common constants. Safe to ship: same for every Imperial JMC Y1 2025/26 student.

Per-user overrides live in user.config.json at the repo root.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

PANOPTO_HOST = "https://imperial.cloud.panopto.eu"
BLACKBOARD_HOST = "https://bb.imperial.ac.uk"

# Blackboard cookies beyond this set overflow nginx; SSO cookies like ESTSAUTH*
# must be stripped.
BB_COOKIE_ALLOWLIST = frozenset({
    "BbRouter", "JSESSIONID", "AWSELB", "AWSELBCORS",
    "shib_idp_session", "samlCookie", "SSOCOOKIEPULLED", "s_session_id",
})

# Panopto caption language enum; Imperial uses English_GB = 1.
PANOPTO_DEFAULT_LANG = "1"


@dataclass(frozen=True)
class SubjectMeta:
    slug: str
    code: str
    title: str
    panopto_folder: Optional[str]
    bb_course: Optional[str]
    bb_homepage: Optional[str] = None
    bb_lecture_notes: Optional[str] = None
    bb_problem_sheets: Optional[str] = None
    bb_coursework: Optional[str] = None


# Updated 2026-04-17 from the Imperial JMC Y1 2025/26 cohort. These IDs are
# identical across students; only re-scrape if the academic year changes.
SUBJECTS: dict[str, SubjectMeta] = {
    "analysis": SubjectMeta(
        slug="analysis",
        code="MATH40002",
        title="Analysis 1",
        panopto_folder="d8a27c20-9898-46c7-9163-b31c01552694",
        bb_course="_46862_1",
        bb_homepage="_3554584_1",
        bb_lecture_notes="_3658112_1",
        bb_problem_sheets="_3658113_1",
        bb_coursework="_3658114_1",
    ),
    "calculus": SubjectMeta(
        slug="calculus",
        code="MATH40004",
        title="Calculus and Applications",
        panopto_folder="a74c2408-69e3-4920-9139-b31b013ff055",
        bb_course="_46772_1",
    ),
    "linear-algebra": SubjectMeta(
        slug="linear-algebra",
        code="MATH40012",
        title="Linear Algebra and Groups for JMC",
        panopto_folder="44b6c0ec-8fa4-4fe3-81f2-b31b013fedae",
        bb_course="_46759_1",
    ),
}

SUBJECT_SLUGS = list(SUBJECTS.keys())


def subject(slug: str) -> SubjectMeta:
    if slug not in SUBJECTS:
        raise KeyError(f"Unknown subject {slug!r}. Known: {SUBJECT_SLUGS}")
    return SUBJECTS[slug]
