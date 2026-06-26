import json
import os
import random
from typing import Any

import httpx
from dotenv import load_dotenv

from app.ecg_generator import RHYTHMS, generate_waveform
from app.seed_data import EXPLANATIONS, KEY_FEATURES


load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"
GROQ_CASE_TIMEOUT_SECONDS = 4
GROQ_LEARN_MORE_TIMEOUT_SECONDS = 8
DIFFICULTY_MAP = {
    "Easy": "Beginner",
    "Medium": "Intermediate",
    "Hard": "Advanced",
    "Beginner": "Beginner",
    "Intermediate": "Intermediate",
    "Advanced": "Advanced",
}


RHYTHMS_BY_DIFFICULTY = {
    "Beginner": [
        "Normal sinus rhythm",
        "Sinus bradycardia",
        "Sinus tachycardia",
        "Sinus arrhythmia",
    ],
    "Intermediate": [
        "Atrial fibrillation",
        "Atrial flutter",
        "First-degree AV block",
        "Second-degree AV block type I",
        "PVCs",
        "PACs",
        "Junctional rhythm",
        "Paced rhythm",
        "LVH pattern",
        "Right bundle branch block",
    ],
    "Advanced": [
        "Ventricular tachycardia",
        "Ventricular fibrillation",
        "Accelerated idioventricular rhythm",
        "SVT",
        "Second-degree AV block type II",
        "Third-degree AV block",
        "Left bundle branch block",
        "Hyperkalemia pattern",
        "Prolonged QT",
        "Atrial fibrillation",
        "Atrial flutter",
        "PVCs",
    ],
}

_CASE_TEXT_CACHE: dict[tuple[str, str], dict[str, Any]] = {}
_LEARN_MORE_CACHE: dict[str, dict[str, Any]] = {}


def generate_case_with_groq(difficulty: str, rhythm: str | None = None) -> dict[str, Any]:
    normalized = normalize_difficulty(difficulty)
    selected_rhythm = rhythm or choose_rhythm(normalized)
    cached = _CASE_TEXT_CACHE.get((normalized, selected_rhythm))
    if cached:
        return _build_case_from_text(cached, normalized, selected_rhythm, "groq-cache")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return local_fallback_case(normalized, "local-fallback", selected_rhythm)

    try:
        generated = _request_groq_case(api_key, normalized, selected_rhythm)
        case_text = _coerce_case_text(generated, selected_rhythm)
        _CASE_TEXT_CACHE[(normalized, selected_rhythm)] = case_text
        return _build_case_from_text(case_text, normalized, selected_rhythm, "groq-generated")
    except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return local_fallback_case(normalized, "groq-fallback", selected_rhythm)


def generate_learn_more(case: dict[str, Any]) -> dict[str, Any]:
    rhythm = case["rhythm_label"]
    cached = _LEARN_MORE_CACHE.get(rhythm)
    if cached:
        return cached

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _fallback_learn_more(rhythm)

    try:
        generated = _request_groq_learn_more(api_key, case)
        lesson = _coerce_learn_more(generated, rhythm)
        _LEARN_MORE_CACHE[rhythm] = lesson
        return lesson
    except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return _fallback_learn_more(rhythm)


def normalize_difficulty(difficulty: str) -> str:
    if difficulty not in DIFFICULTY_MAP:
        raise ValueError("Unsupported difficulty")
    return DIFFICULTY_MAP[difficulty]


def choose_rhythm(difficulty: str, recent_labels: list[str] | None = None) -> str:
    choices = RHYTHMS_BY_DIFFICULTY[difficulty]
    recent = recent_labels or []
    last_seen = {
        rhythm: index
        for index, rhythm in enumerate(recent)
        if rhythm in choices and rhythm not in recent[:index]
    }
    unseen = [rhythm for rhythm in choices if rhythm not in last_seen]
    if unseen:
        return random.choice(unseen)

    oldest_seen_index = max(last_seen.values())
    oldest_rhythms = [
        rhythm
        for rhythm in choices
        if last_seen[rhythm] == oldest_seen_index
    ]
    return random.choice(oldest_rhythms)


def local_fallback_case(
    difficulty: str,
    source_type: str = "local-fallback",
    rhythm: str | None = None,
) -> dict[str, Any]:
    rhythm = rhythm or choose_rhythm(difficulty)
    distractors = [option for option in RHYTHMS if option != rhythm]
    random.shuffle(distractors)
    options = distractors[:3] + [rhythm]
    random.shuffle(options)
    return {
        "rhythm_label": rhythm,
        "difficulty": difficulty,
        "source_type": source_type,
        "explanation": EXPLANATIONS[rhythm],
        "key_features": KEY_FEATURES[rhythm],
        "waveform": generate_waveform(rhythm, difficulty),
        "waveform_rhythm_label": rhythm,
        "options": options,
    }


def _request_groq_case(api_key: str, difficulty: str, rhythm: str) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": os.getenv("GROQ_MODEL", DEFAULT_MODEL),
        "temperature": 0.8,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "You create educational ECG rhythm trainer cases. "
                    "Do not provide medical advice or claim to diagnose patients. "
                    "Return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": _prompt(difficulty, rhythm),
            },
        ],
    }
    with httpx.Client(timeout=GROQ_CASE_TIMEOUT_SECONDS) as client:
        response = client.post(GROQ_URL, headers=headers, json=payload)
        response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def _request_groq_learn_more(api_key: str, case: dict[str, Any]) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    rhythm = case["rhythm_label"]
    features = ", ".join(case["key_features"])
    payload = {
        "model": os.getenv("GROQ_MODEL", DEFAULT_MODEL),
        "temperature": 0.45,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an ECG educator for a training-only rhythm app. "
                    "Explain known labels and features. Do not give clinical advice, "
                    "triage guidance, or claim to diagnose a patient. Return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": f"""
Create a concise learning note for this known ECG rhythm label: {rhythm}
Known features for this generated educational case: {features}

Return JSON with exactly these keys:
- overview: 2 short sentences
- how_to_recognize: 3 bullet strings
- common_confusions: 2 bullet strings
- memory_tip: 1 short sentence

Keep it educational, practical, and brief. Do not mention treatment or diagnosis.
""".strip(),
            },
        ],
    }
    with httpx.Client(timeout=GROQ_LEARN_MORE_TIMEOUT_SECONDS) as client:
        response = client.post(GROQ_URL, headers=headers, json=payload)
        response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def _prompt(difficulty: str, rhythm: str) -> str:
    return f"""
Create one {difficulty} ECG rhythm training case for a multiple-choice simulator.
The correct rhythm_label must be exactly: {rhythm}

Return JSON with exactly these keys:
- rhythm_label: one of {RHYTHMS}
- explanation: one short educational explanation based on the known label
- key_features: 3 short ECG features
- distractors: 3 plausible wrong answer choices from the same rhythm list

Difficulty rules:
- Beginner/Easy: obvious, clean, common rhythm
- Intermediate/Medium: ectopy, blocks, AFib/flutter, mild noise
- Advanced/Hard: subtle or noisier educational example

Do not include waveform samples. The app renders the ECG with its own simulator.
This is for training only, not clinical diagnosis.
""".strip()


def _coerce_case_text(generated: dict[str, Any], selected_rhythm: str) -> dict[str, Any]:
    rhythm = generated.get("rhythm_label") or selected_rhythm
    if rhythm != selected_rhythm:
        rhythm = selected_rhythm
    if rhythm not in RHYTHMS:
        raise ValueError("Groq returned an unsupported rhythm label")

    explanation = str(generated.get("explanation") or EXPLANATIONS[rhythm])[:500]
    key_features = _clean_string_list(generated.get("key_features"), fallback=KEY_FEATURES[rhythm], limit=3)
    distractors = [
        option
        for option in _clean_string_list(generated.get("distractors"), fallback=[], limit=6)
        if option in RHYTHMS and option != rhythm
    ]
    if len(distractors) < 3:
        remaining = [option for option in RHYTHMS if option != rhythm and option not in distractors]
        random.shuffle(remaining)
        distractors.extend(remaining[: 3 - len(distractors)])

    return {
        "rhythm_label": rhythm,
        "explanation": explanation,
        "key_features": key_features,
        "distractors": distractors[:3],
    }


def _build_case_from_text(
    case_text: dict[str, Any],
    difficulty: str,
    rhythm: str,
    source_type: str,
) -> dict[str, Any]:
    options = case_text["distractors"] + [rhythm]
    random.shuffle(options)
    return {
        "rhythm_label": rhythm,
        "difficulty": difficulty,
        "source_type": source_type,
        "explanation": case_text["explanation"],
        "key_features": case_text["key_features"],
        "waveform": generate_waveform(rhythm, difficulty),
        "waveform_rhythm_label": rhythm,
        "options": options,
    }


def _clean_string_list(value: Any, fallback: list[str], limit: int) -> list[str]:
    if not isinstance(value, list):
        return fallback[:limit]
    cleaned = [str(item).strip() for item in value if str(item).strip()]
    return cleaned[:limit] or fallback[:limit]


def _coerce_learn_more(generated: dict[str, Any], rhythm: str) -> dict[str, Any]:
    fallback = _fallback_learn_more(rhythm)
    return {
        "overview": str(generated.get("overview") or fallback["overview"])[:700],
        "how_to_recognize": _clean_string_list(
            generated.get("how_to_recognize"),
            fallback=fallback["how_to_recognize"],
            limit=3,
        ),
        "common_confusions": _clean_string_list(
            generated.get("common_confusions"),
            fallback=fallback["common_confusions"],
            limit=2,
        ),
        "memory_tip": str(generated.get("memory_tip") or fallback["memory_tip"])[:240],
    }


def _fallback_learn_more(rhythm: str) -> dict[str, Any]:
    return {
        "overview": EXPLANATIONS[rhythm],
        "how_to_recognize": KEY_FEATURES[rhythm],
        "common_confusions": _fallback_confusions(rhythm),
        "memory_tip": f"Start with rate and regularity, then confirm the key features for {rhythm}.",
    }


def _fallback_confusions(rhythm: str) -> list[str]:
    confusions = {
        "Normal sinus rhythm": ["Sinus bradycardia when the rate is slow", "Sinus tachycardia when the rate is fast"],
        "Sinus bradycardia": ["Normal sinus rhythm at the low end of normal", "Slow atrial fibrillation if P waves are unclear"],
        "Sinus tachycardia": ["SVT when the rate is very fast", "Atrial flutter with regular conduction"],
        "Sinus arrhythmia": ["PACs if early beats are isolated", "Atrial fibrillation if P waves are hard to see"],
        "Atrial fibrillation": ["PACs when irregularity is intermittent", "Atrial flutter with variable block"],
        "Atrial flutter": ["SVT if flutter waves are hidden", "Atrial fibrillation if conduction varies"],
        "First-degree AV block": ["Normal sinus rhythm if PR interval is not measured", "Higher-grade block if dropped beats appear"],
        "Second-degree AV block type I": ["Second-degree AV block type II", "Blocked PACs"],
        "Second-degree AV block type II": ["Second-degree AV block type I", "Complete heart block"],
        "Third-degree AV block": ["Second-degree AV block type II", "Junctional rhythm with AV dissociation missed"],
        "PVCs": ["PACs with aberrancy", "Ventricular tachycardia if wide beats run together"],
        "PACs": ["PVCs if the early beat is wide", "Sinus arrhythmia when timing varies"],
        "Ventricular tachycardia": ["SVT with aberrancy", "Frequent PVCs if the run is brief"],
        "Ventricular fibrillation": ["Artifact", "Polymorphic ventricular tachycardia"],
        "Accelerated idioventricular rhythm": ["Slow ventricular tachycardia", "Paced rhythm"],
        "SVT": ["Sinus tachycardia", "Atrial flutter with 2:1 conduction"],
        "Junctional rhythm": ["Sinus bradycardia with visible P waves", "Accelerated idioventricular rhythm if QRS is wide"],
        "Paced rhythm": ["Left bundle branch block", "Ventricular rhythm without visible pacing spikes"],
        "LVH pattern": ["Normal high voltage variant", "Left bundle branch block if QRS is wide"],
        "Left bundle branch block": ["Paced rhythm", "Ventricular rhythm"],
        "Right bundle branch block": ["PVCs with aberrancy", "Normal rhythm if terminal widening is missed"],
        "Hyperkalemia pattern": ["Early repolarization", "Acute ischemic T-wave changes"],
        "Prolonged QT": ["Normal sinus rhythm", "Hypokalemia-style repolarization changes"],
    }
    return confusions[rhythm]
