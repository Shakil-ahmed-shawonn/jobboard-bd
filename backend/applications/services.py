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


def score_resume_fit(job_requirements: str, resume_text: str) -> dict:
    """
    Calls Claude with a forced tool call so the response is always valid JSON —
    no free-text parsing or "please return only JSON" prompt-fragility.

    Returns:
        dict with keys: fit_score (int), matched_skills (list[str]),
        missing_skills (list[str]), summary (str).
    """
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
