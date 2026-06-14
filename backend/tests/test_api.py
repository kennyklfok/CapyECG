from fastapi.testclient import TestClient

from app.database import get_connection, init_db, row_to_case
from app.ecg_generator import RHYTHMS, generate_waveform
from app.groq_cases import choose_rhythm
from app.main import app
from app.seed_data import DIFFICULTY_BY_RHYTHM, EXPLANATIONS, KEY_FEATURES


client = TestClient(app)


def test_new_case_and_submit_answer_flow(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    init_db()
    case_response = client.get("/api/cases/new?difficulty=Easy")

    assert case_response.status_code == 200
    case = case_response.json()
    assert case["id"] > 0
    assert len(case["options"]) == 4
    assert case["waveform"]["durationSeconds"] == 10
    assert case["waveform"]["paperSpeed"] == "25 mm/s"
    assert case["waveform"]["gain"] == "10 mm/mV"
    assert "rhythm_label" not in case

    answer_response = client.post(
        "/api/answers",
        json={"case_id": case["id"], "answer": case["options"][0]},
    )

    assert answer_response.status_code == 200
    feedback = answer_response.json()
    assert feedback["correct_answer"]
    assert feedback["explanation"]
    assert feedback["already_answered"] is False
    assert feedback["disclaimer"] == "For training only. Not for clinical diagnosis."

    repeat_response = client.post(
        "/api/answers",
        json={"case_id": case["id"], "answer": case["options"][0]},
    )

    assert repeat_response.status_code == 200
    assert repeat_response.json()["already_answered"] is True


def test_invalid_case_returns_404():
    init_db()
    response = client.post("/api/answers", json={"case_id": 999999, "answer": "SVT"})

    assert response.status_code == 404


def test_learn_more_returns_educational_note(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    init_db()
    case = client.get("/api/cases/new?difficulty=Easy").json()

    response = client.get(f"/api/cases/{case['id']}/learn-more")

    assert response.status_code == 200
    lesson = response.json()
    assert lesson["rhythm"]
    assert lesson["overview"]
    assert len(lesson["how_to_recognize"]) >= 1
    assert len(lesson["common_confusions"]) >= 1
    assert lesson["disclaimer"] == "For training only. Not for clinical diagnosis."


def test_choose_rhythm_avoids_recent_labels_when_possible():
    recent = ["Normal sinus rhythm", "Sinus bradycardia", "Sinus arrhythmia"]
    choices = {choose_rhythm("Beginner", recent) for _ in range(10)}

    assert choices == {"Sinus tachycardia"}


def test_choose_rhythm_uses_oldest_recent_when_pool_is_exhausted():
    recent = ["Sinus arrhythmia", "Sinus tachycardia", "Sinus bradycardia", "Normal sinus rhythm"]

    assert choose_rhythm("Beginner", recent) == "Normal sinus rhythm"


def test_choose_rhythm_uses_newest_duplicate_for_rotation():
    recent = [
        "Sinus arrhythmia",
        "Normal sinus rhythm",
        "Sinus tachycardia",
        "Sinus bradycardia",
        "Normal sinus rhythm",
    ]

    assert choose_rhythm("Beginner", recent) == "Sinus bradycardia"


def test_rhythm_library_has_metadata_and_waveforms():
    assert len(RHYTHMS) >= 20

    for index, rhythm in enumerate(RHYTHMS, start=1):
        assert rhythm in DIFFICULTY_BY_RHYTHM
        assert rhythm in EXPLANATIONS
        assert rhythm in KEY_FEATURES
        assert len(KEY_FEATURES[rhythm]) >= 3

        waveform = generate_waveform(rhythm, DIFFICULTY_BY_RHYTHM[rhythm], seed=index)
        assert waveform["durationSeconds"] == 10
        assert waveform["sampleRate"] == 250
        assert len(waveform["samples"]) == 2500


def test_generated_case_stores_matching_waveform_rhythm_label(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    init_db()
    response = client.get("/api/cases/new?difficulty=Medium")

    assert response.status_code == 200
    case_id = response.json()["id"]
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM ecg_cases WHERE id = ?", [case_id]).fetchone()

    stored_case = row_to_case(row)
    assert stored_case["rhythm_label"] == stored_case["waveform_rhythm_label"]
