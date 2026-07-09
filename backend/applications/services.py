"""
applications/services.py

Two responsibilities, kept separate from views.py per the "keep views light"
principle:
1. extract_resume_text() — pull plain text out of an uploaded PDF/DOCX.
2. score_resume_fit()   — send {job requirements, resume text} to Claude
   and parse back a structured fit score.

Docs read before implementing:
- pdfplumber: https://github.com/jsvine/pdfplumber (page.extract_text() can
  return None for scanned/image pages — must guard against that)
- python-docx: https://python-docx.readthedocs.io/en/latest/ (paragraphs only;
  text in tables needs separate handling, out of scope for MVP)
- Anthropic Messages API: https://docs.claude.com/en/api/messages — using a
  tool-call (forced JSON via tool_choice) instead of parsing free text, so
  the response is guaranteed structured.
"""

import io
import json
import logging
import re

import docx
import pdfplumber
from anthropic import Anthropic
from django.conf import settings

logger = logging.getLogger(__name__)

_FIT_SCORE_TOOL = {
    "name": "submit_fit_score",
    "description": "Submit a structured resume-to-job fit assessment.",
    "input_schema": {
        "type": "object",
        "properties": {
            "fit_score": {"type": "integer", "minimum": 0, "maximum": 100},
            "matched_skills": {"type": "array", "items": {"type": "string"}},
            "missing_skills": {"type": "array", "items": {"type": "string"}},
            "summary": {"type": "string", "description": "2-3 sentence rationale."},
        },
        "required": ["fit_score", "matched_skills", "missing_skills", "summary"],
    },
}


class ResumeParsingError(Exception):
    """Raised when a resume file cannot be parsed into usable text."""


def extract_resume_text(uploaded_file) -> str:
    """
    Extracts plain text from an in-memory PDF or DOCX upload.

    Args:
        uploaded_file: Django UploadedFile (has .name and behaves like a file object).

    Returns:
        Extracted text, stripped.

    Raises:
        ResumeParsingError: if the extension is unsupported or extraction yields
            no usable text (e.g. a scanned/image-only PDF with no OCR layer).
    """
    name = uploaded_file.name.lower()
    uploaded_file.seek(0)

    if name.endswith(".pdf"):
        text_parts = []
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()  # can be None for scanned pages
                if page_text:
                    text_parts.append(page_text)
        text = "\n".join(text_parts).strip()

    elif name.endswith(".docx"):
        document = docx.Document(io.BytesIO(uploaded_file.read()))
        text = "\n".join(p.text for p in document.paragraphs).strip()

    else:
        raise ResumeParsingError("Only .pdf and .docx resumes are supported.")

    if not text:
        raise ResumeParsingError(
            "No extractable text found — this looks like a scanned/image resume. "
            "Flagging for manual review instead of failing the upload."
        )

    return text


def _local_fallback_score(job_requirements: str, resume_text: str) -> dict:
    """
    DEV/TEST-ONLY fallback — no API key required, no network call, $0 cost.

    Does simple keyword-overlap matching between the job's requirements text
    and the resume text to produce a plausible-looking score. This is NOT
    real AI reasoning — it exists purely so the UI/dashboard can be tested
    and screenshotted without a funded Anthropic API key.

    Swap back to score_resume_fit()'s real Claude call once ANTHROPIC_API_KEY
    is set to a real key — that happens automatically, see score_resume_fit().
    """
    # Pull out candidate "skill" tokens from requirements: words/phrases that
    # look like tools/skills (capitalized terms, or comma/period-separated chunks).
    raw_terms = re.split(r"[,.\n]", job_requirements)
    candidate_skills = [t.strip() for t in raw_terms if 2 <= len(t.strip()) <= 40]
    # Keep it to short, skill-like fragments — drop long sentence fragments.
    candidate_skills = [s for s in candidate_skills if len(s.split()) <= 5][:12]

    resume_lower = resume_text.lower()
    matched, missing = [], []
    for skill in candidate_skills:
        skill_lower = skill.lower()
        # crude but effective: check if the core word(s) appear in the resume
        core_word = re.sub(r"[^a-z0-9+#. ]", "", skill_lower).strip()
        if core_word and core_word in resume_lower:
            matched.append(skill)
        elif core_word:
            missing.append(skill)

    total = len(matched) + len(missing)
    fit_score = round((len(matched) / total) * 100) if total else 50
    # Keep scores in a believable band rather than hard 0 or 100.
    fit_score = max(15, min(fit_score, 95))

    summary = (
        f"[Local test scorer — not real AI] Resume matched {len(matched)} of "
        f"{total} extracted requirement keywords."
        if total
        else "[Local test scorer — not real AI] Could not extract clear "
        "keywords from the job requirements to compare."
    )

    return {
        "fit_score": fit_score,
        "matched_skills": matched[:8],
        "missing_skills": missing[:8],
        "summary": summary,
    }


def score_resume_fit(job_requirements: str, resume_text: str) -> dict:
    """
    Calls Claude with a forced tool call so the response is always valid JSON —
    no free-text parsing or "please return only JSON" prompt-fragility.

    Falls back to _local_fallback_score() automatically when:
    - ANTHROPIC_API_KEY is unset or still the placeholder value, OR
    - the live API call itself fails for any reason (no credit balance,
      network error, rate limit, etc.)

    This means the app stays fully testable at $0 cost regardless of billing
    state. Once a real, funded key is in place, this same function starts
    returning genuine Claude results automatically — no code change needed.

    Returns:
        dict with keys: fit_score (int), matched_skills (list[str]),
        missing_skills (list[str]), summary (str).
    """
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "sk-ant-your-key-here":
        logger.warning("No real ANTHROPIC_API_KEY configured — using local fallback scorer.")
        return _local_fallback_score(job_requirements, resume_text)

    try:
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            tools=[_FIT_SCORE_TOOL],
            tool_choice={"type": "tool", "name": "submit_fit_score"},
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Assess how well this resume fits the job requirements below. "
                        "Be concrete about matched and missing skills.\n\n"
                        f"JOB REQUIREMENTS:\n{job_requirements}\n\n"
                        f"RESUME:\n{resume_text}"
                    ),
                }
            ],
        )

        for block in message.content:
            if block.type == "tool_use" and block.name == "submit_fit_score":
                return block.input

        # Should not happen with tool_choice forced, but fail loudly if it does.
        logger.error("Claude did not return a tool_use block: %s", message.content)
        raise RuntimeError("AI fit scoring failed — no structured response returned.")

    except Exception as exc:
        # Covers: BadRequestError (no credit balance), rate limits, network
        # errors, or the RuntimeError raised above. Fall back rather than
        # blocking the seeker's application on a billing/infra issue.
        logger.warning("Live Claude API call failed (%s) — using local fallback scorer.", exc)
        return _local_fallback_score(job_requirements, resume_text)
