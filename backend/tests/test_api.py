from fastapi.testclient import TestClient

from app.database import get_connection, init_db, row_to_case
from app.ecg_generator import RHYTHMS, generate_waveform
from app import ecg_generator
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
    assert case["waveform"]["displayLayout"] == "standard-3x4-plus-rhythm"
    assert case["waveform"]["rhythmLead"] == "II"
    assert len(case["waveform"]["leads"]) == 12
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
        assert waveform["samples"] == waveform["leads"]["II"]
        assert waveform["leadOrder"] == ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
        assert set(waveform["leads"]) == set(waveform["leadOrder"])
        assert all(len(samples) == 2500 for samples in waveform["leads"].values())


def test_rhythm_templates_match_expected_rate_and_regularity():
    expectations = {
        "Normal sinus rhythm": ((60, 100), "Regular"),
        "Sinus bradycardia": ((35, 59), "Regular"),
        "Sinus tachycardia": ((100, 140), "Regular"),
        "Sinus arrhythmia": ((60, 100), "Irregular"),
        "Atrial fibrillation": ((50, 130), "Irregularly irregular"),
        "Atrial flutter": ((70, 110), "Regular"),
        "First-degree AV block": ((60, 100), "Regular"),
        "Second-degree AV block type I": ((40, 70), "Irregular"),
        "Second-degree AV block type II": ((35, 70), "Irregular"),
        "Third-degree AV block": ((25, 45), "AV dissociation"),
        "PVCs": ((60, 100), "Mostly regular with early beats"),
        "PACs": ((60, 100), "Mostly regular with early beats"),
        "Ventricular tachycardia": ((120, 220), "Regular"),
        "Ventricular fibrillation": ((0, 0), "Chaotic"),
        "Accelerated idioventricular rhythm": ((50, 110), "Regular"),
        "SVT": ((140, 220), "Regular"),
        "Junctional rhythm": ((40, 70), "Regular"),
        "Paced rhythm": ((50, 90), "Regular"),
        "LVH pattern": ((60, 100), "Regular"),
        "Left bundle branch block": ((60, 100), "Regular"),
        "Right bundle branch block": ((60, 100), "Regular"),
        "Hyperkalemia pattern": ((60, 100), "Regular"),
        "Prolonged QT": ((60, 100), "Regular"),
    }

    for index, rhythm in enumerate(RHYTHMS, start=1):
        waveform = generate_waveform(rhythm, DIFFICULTY_BY_RHYTHM[rhythm], seed=index)
        rate_range, regularity = expectations[rhythm]

        assert rate_range[0] <= waveform["heartRate"] <= rate_range[1]
        assert waveform["regularity"] == regularity


def test_junctional_template_has_absent_p_waves():
    beat_time = 1.0

    p_window_values = [
        abs(ecg_generator._beat_waveform(t, beat_time, "Junctional rhythm", "normal"))
        for t in [beat_time - 0.20, beat_time - 0.17, beat_time - 0.14, beat_time - 0.12]
    ]

    assert max(p_window_values) < 0.001


def test_wide_complex_templates_are_wide_when_labeled_wide():
    beat_time = 1.0
    qrs_window = [beat_time - 0.08 + 0.004 * index for index in range(41)]

    for rhythm in ["Accelerated idioventricular rhythm", "Left bundle branch block", "Right bundle branch block"]:
        active_points = [
            t
            for t in qrs_window
            if abs(ecg_generator._beat_waveform(t, beat_time, rhythm, "normal")) > 0.08
        ]

        assert active_points[-1] - active_points[0] >= 0.10


def test_bundle_branch_templates_keep_sinus_p_waves():
    beat_time = 1.0

    for rhythm in ["Left bundle branch block", "Right bundle branch block"]:
        p_value = ecg_generator._beat_waveform(beat_time - 0.17, beat_time, rhythm, "normal")

        assert p_value > 0.10


def test_paced_template_has_pacer_spike_before_wide_complex():
    beat_time = 1.0

    spike_value = ecg_generator._beat_waveform(beat_time - 0.045, beat_time, "Paced rhythm", "normal")

    assert spike_value > 0.8


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
