from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.database import get_connection, init_db, insert_case, recent_rhythm_labels, row_to_case
from app.ecg_generator import RHYTHMS
from app.groq_cases import choose_rhythm, generate_case_with_groq, generate_learn_more, normalize_difficulty
from app.schemas import LearnMoreResponse, PublicCase, SubmitAnswerRequest, SubmitAnswerResponse


DISCLAIMER = "For training only. Not for clinical diagnosis."
DIFFICULTIES = {"Easy", "Medium", "Hard", "Beginner", "Intermediate", "Advanced"}


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="CapyECG API",
    description="Educational ECG rhythm trainer API. Not for clinical diagnosis.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://capyecg.onrender.com",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "disclaimer": DISCLAIMER}


@app.get("/api/rhythms")
def rhythms() -> dict[str, list[str]]:
    return {"rhythms": RHYTHMS}


@app.get("/api/cases/new", response_model=PublicCase)
def get_new_case(
    difficulty: str = Query("Easy"),
) -> PublicCase:
    if difficulty not in DIFFICULTIES:
        raise HTTPException(status_code=400, detail="Unsupported difficulty")

    try:
        normalized_difficulty = normalize_difficulty(difficulty)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Unsupported difficulty") from exc

    recent_labels = recent_rhythm_labels(normalized_difficulty)
    rhythm = choose_rhythm(normalized_difficulty, recent_labels)
    case = generate_case_with_groq(normalized_difficulty, rhythm)
    case_id = insert_case(case)

    return PublicCase(
        id=case_id,
        difficulty=case["difficulty"],
        source_type=case["source_type"],
        source_note=case["source_note"],
        waveform=case["waveform"],
        options=case["options"],
        disclaimer=DISCLAIMER,
    )


@app.post("/api/answers", response_model=SubmitAnswerResponse)
def submit_answer(payload: SubmitAnswerRequest) -> SubmitAnswerResponse:
    case = _get_case_or_404(payload.case_id)
    submitted = _normalize(payload.answer)
    correct = _normalize(case["rhythm_label"])

    return SubmitAnswerResponse(
        case_id=case["id"],
        is_correct=submitted == correct,
        submitted_answer=payload.answer,
        correct_answer=case["rhythm_label"],
        explanation=case["explanation"],
        key_features=case["key_features"],
        disclaimer=DISCLAIMER,
    )


@app.get("/api/cases/{case_id}/learn-more", response_model=LearnMoreResponse)
def get_learn_more(case_id: int) -> LearnMoreResponse:
    case = _get_case_or_404(case_id)
    lesson = generate_learn_more(case)
    return LearnMoreResponse(
        case_id=case["id"],
        rhythm=case["rhythm_label"],
        overview=lesson["overview"],
        how_to_recognize=lesson["how_to_recognize"],
        common_confusions=lesson["common_confusions"],
        memory_tip=lesson["memory_tip"],
        disclaimer=DISCLAIMER,
    )


def _get_case_or_404(case_id: int) -> dict:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM ecg_cases WHERE id = ?", [case_id]).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="ECG case not found")
    return row_to_case(row)


def _normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("-", " ").split())
