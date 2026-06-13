from typing import Any

from pydantic import BaseModel, Field


class PublicCase(BaseModel):
    id: int
    difficulty: str
    source_type: str
    source_note: str
    waveform: dict[str, Any]
    options: list[str]
    disclaimer: str


class SubmitAnswerRequest(BaseModel):
    case_id: int = Field(gt=0)
    answer: str = Field(min_length=1, max_length=120)


class SubmitAnswerResponse(BaseModel):
    case_id: int
    is_correct: bool
    submitted_answer: str
    correct_answer: str
    explanation: str
    key_features: list[str]
    disclaimer: str


class LearnMoreResponse(BaseModel):
    case_id: int
    rhythm: str
    overview: str
    how_to_recognize: list[str]
    common_confusions: list[str]
    memory_tip: str
    disclaimer: str
