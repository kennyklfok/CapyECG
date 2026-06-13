from app.ecg_generator import RHYTHMS, generate_waveform


DIFFICULTY_BY_RHYTHM = {
    "Normal sinus rhythm": "Beginner",
    "Sinus bradycardia": "Beginner",
    "Sinus tachycardia": "Beginner",
    "Atrial fibrillation": "Intermediate",
    "Atrial flutter": "Intermediate",
    "First-degree AV block": "Intermediate",
    "PVCs": "Intermediate",
    "PACs": "Intermediate",
    "Ventricular tachycardia": "Advanced",
    "SVT": "Advanced",
}


EXPLANATIONS = {
    "Normal sinus rhythm": "Regular rhythm with upright P waves before each narrow QRS and a rate in the expected adult resting range.",
    "Sinus bradycardia": "Sinus pattern is preserved, but the ventricular rate is slow, typically below 60 beats per minute.",
    "Sinus tachycardia": "Sinus pattern is preserved with a fast regular rate, typically above 100 beats per minute.",
    "Atrial fibrillation": "Irregularly irregular R-R intervals with no consistent P waves; fibrillatory baseline activity may be present.",
    "Atrial flutter": "Organized atrial activity creates repeating flutter waves, often with a regular or patterned ventricular response.",
    "First-degree AV block": "Each P wave conducts to a QRS, but the PR interval is prolonged.",
    "PVCs": "Premature wide ventricular beats interrupt the underlying rhythm and are usually followed by a compensatory pause.",
    "PACs": "Premature atrial beats arrive early, often with an abnormal P wave before a narrow QRS.",
    "Ventricular tachycardia": "Fast, regular, wide-complex rhythm pattern used here as an educational example of VT morphology.",
    "SVT": "Fast, regular narrow-complex rhythm with P waves often hidden in or near the QRS complexes.",
}


KEY_FEATURES = {
    "Normal sinus rhythm": ["Regular R-R intervals", "P before every QRS", "Narrow QRS"],
    "Sinus bradycardia": ["Sinus P waves", "Slow rate", "Regular rhythm"],
    "Sinus tachycardia": ["Sinus P waves", "Fast rate", "Regular rhythm"],
    "Atrial fibrillation": ["Irregularly irregular", "No consistent P waves", "Variable R-R intervals"],
    "Atrial flutter": ["Flutter-wave baseline", "Atrial activity is organized", "Often patterned conduction"],
    "First-degree AV block": ["PR interval is prolonged", "One P for each QRS", "Usually narrow QRS"],
    "PVCs": ["Early wide beat", "Different morphology", "Compensatory pause may follow"],
    "PACs": ["Early atrial beat", "Abnormal P wave", "Usually narrow QRS"],
    "Ventricular tachycardia": ["Fast rate", "Wide complexes", "Regular monomorphic pattern"],
    "SVT": ["Fast regular rhythm", "Narrow complexes", "P waves may be hidden"],
}


def seed_cases() -> list[dict]:
    cases = []
    for index, rhythm in enumerate(RHYTHMS, start=1):
        difficulty = DIFFICULTY_BY_RHYTHM[rhythm]
        waveform = generate_waveform(rhythm, difficulty, seed=index)
        cases.append(
            {
                "rhythm_label": rhythm,
                "difficulty": difficulty,
                "source_type": "synthetic",
                "explanation": EXPLANATIONS[rhythm],
                "key_features": KEY_FEATURES[rhythm],
                "waveform": waveform,
            }
        )
    return cases
