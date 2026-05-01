"""Gold layer scorer — LLM scoring via forced tool use."""

from __future__ import annotations

import dataclasses
from typing import Any

from src.llm.adapter import LLMAdapter
from src.pipeline.normalizer import SilverRecord
from src.prompts.scoring import SCORING_SYSTEM_PROMPT

SCORE_SIGNALS_TOOL: dict[str, object] = {
    "name": "score_signals",
    "description": "Return distress scores for a single ZIP code.",
    "input_schema": {
        "type": "object",
        "properties": {
            "delinquency_score": {
                "type": "integer",
                "description": "Loan delinquency distress score 0-100.",
                "minimum": 0,
                "maximum": 100,
            },
            "employment_score": {
                "type": "integer",
                "description": "Employment distress score 0-100.",
                "minimum": 0,
                "maximum": 100,
            },
            "rent_vacancy_score": {
                "type": "integer",
                "description": "Rent/vacancy distress score 0-100.",
                "minimum": 0,
                "maximum": 100,
            },
            "overall_score": {
                "type": "integer",
                "description": "Weighted overall distress score 0-100.",
                "minimum": 0,
                "maximum": 100,
            },
            "rationale": {
                "type": "string",
                "description": "2-3 sentence explanation of dominant risk factors.",
            },
        },
        "required": [
            "delinquency_score",
            "employment_score",
            "rent_vacancy_score",
            "overall_score",
            "rationale",
        ],
    },
}


@dataclasses.dataclass(frozen=True)
class GoldRecord:
    zip_code: str
    delinquency_score: int
    employment_score: int
    rent_vacancy_score: int
    overall_score: int
    rationale: str
    rank: int = 0


def _build_user_message(record: SilverRecord) -> str:
    return (
        f"ZIP code: {record.zip_code}\n"
        f"Delinquency rate: {record.delinquency_rate} (date: {record.delinquency_date})\n"
        f"Unemployment rate: {record.unemployment_rate}%"
        f" (MoM change: {record.unemployment_mom_change}pp)\n"
        f"Average rent: ${record.average_rent}, median rent: ${record.median_rent}\n"
        f"Rent change (30-day): {record.rent_change_pct}%\n"
        f"Vacancy rate: {record.vacancy_rate}%\n"
        "\nScore this ZIP code using the score_signals tool."
    )


def score_zip(record: SilverRecord, adapter: LLMAdapter) -> GoldRecord:
    """Call the LLM with forced tool use and return a GoldRecord (rank=0)."""
    response: Any = adapter.complete(
        messages=[{"role": "user", "content": _build_user_message(record)}],
        system=SCORING_SYSTEM_PROMPT,
        tools=[SCORE_SIGNALS_TOOL],
        tool_choice={"type": "tool", "name": "score_signals"},
    )

    content = response.content if isinstance(response.content, list) else []
    tool_block = next(
        (b for b in content if getattr(b, "name", None) == "score_signals"),
        None,
    )
    if tool_block is None:
        raise RuntimeError(
            "LLM did not return a score_signals tool use block. " f"Content: {response.content}"
        )

    scores: dict[str, object] = tool_block.input
    return GoldRecord(
        zip_code=record.zip_code,
        delinquency_score=int(str(scores["delinquency_score"])),
        employment_score=int(str(scores["employment_score"])),
        rent_vacancy_score=int(str(scores["rent_vacancy_score"])),
        overall_score=int(str(scores["overall_score"])),
        rationale=str(scores["rationale"]),
        rank=0,
    )


def build_digest(records: list[GoldRecord]) -> list[GoldRecord]:
    """Sort by overall_score descending and assign 1-based ranks. Returns new list."""
    sorted_records = sorted(records, key=lambda r: r.overall_score, reverse=True)
    return [dataclasses.replace(record, rank=i + 1) for i, record in enumerate(sorted_records)]
