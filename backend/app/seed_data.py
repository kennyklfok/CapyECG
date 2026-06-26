from app.ecg_generator import RHYTHMS, generate_waveform


DIFFICULTY_BY_RHYTHM = {
    "Normal sinus rhythm": "Beginner",
    "Sinus bradycardia": "Beginner",
    "Sinus tachycardia": "Beginner",
    "Sinus arrhythmia": "Beginner",
    "Atrial fibrillation": "Intermediate",
    "Atrial flutter": "Intermediate",
    "First-degree AV block": "Intermediate",
    "Second-degree AV block type I": "Intermediate",
    "Second-degree AV block type II": "Advanced",
    "Third-degree AV block": "Advanced",
    "PVCs": "Intermediate",
    "PACs": "Intermediate",
    "Ventricular tachycardia": "Advanced",
    "Ventricular fibrillation": "Advanced",
    "Accelerated idioventricular rhythm": "Advanced",
    "SVT": "Advanced",
    "Junctional rhythm": "Intermediate",
    "Paced rhythm": "Intermediate",
    "LVH pattern": "Intermediate",
    "Left bundle branch block": "Advanced",
    "Right bundle branch block": "Intermediate",
    "Hyperkalemia pattern": "Advanced",
    "Prolonged QT": "Advanced",
}


EXPLANATIONS = {
    "Normal sinus rhythm": "Regular rhythm with upright P waves before each narrow QRS and a rate in the expected adult resting range.",
    "Sinus bradycardia": "Sinus pattern is preserved, but the ventricular rate is slow, typically below 60 beats per minute.",
    "Sinus tachycardia": "Sinus pattern is preserved with a fast regular rate, typically above 100 beats per minute.",
    "Sinus arrhythmia": "Sinus P waves are present, but the R-R interval varies in a repeating respiratory-style pattern.",
    "Atrial fibrillation": "Irregularly irregular R-R intervals with no consistent P waves; fibrillatory baseline activity may be present.",
    "Atrial flutter": "Organized atrial activity creates repeating flutter waves, often with a regular or patterned ventricular response.",
    "First-degree AV block": "Each P wave conducts to a QRS, but the PR interval is prolonged.",
    "Second-degree AV block type I": "Progressive AV nodal delay leads to a dropped QRS after a sequence of conducted P waves.",
    "Second-degree AV block type II": "Intermittent non-conducted P waves occur without progressive PR prolongation before the dropped beat.",
    "Third-degree AV block": "Atrial and ventricular activity are dissociated, with an independent slower escape rhythm.",
    "PVCs": "Premature wide ventricular beats interrupt the underlying rhythm and are usually followed by a compensatory pause.",
    "PACs": "Premature atrial beats arrive early, often with an abnormal P wave before a narrow QRS.",
    "Ventricular tachycardia": "Fast, regular, wide-complex rhythm pattern used here as an educational example of VT morphology.",
    "Ventricular fibrillation": "Chaotic ventricular activity is represented by an irregular waveform without organized QRS complexes.",
    "Accelerated idioventricular rhythm": "A regular wide-complex ventricular rhythm appears at a slower rate than ventricular tachycardia.",
    "SVT": "Fast, regular narrow-complex rhythm with P waves often hidden in or near the QRS complexes.",
    "Junctional rhythm": "A regular narrow-complex rhythm arises near the AV junction, with absent P waves in this simplified training strip.",
    "Paced rhythm": "Small pacer spikes precede broad ventricular complexes in this educational paced rhythm pattern.",
    "LVH pattern": "Tall QRS voltage with repolarization strain-style T-wave changes suggests an LVH pattern.",
    "Left bundle branch block": "Wide QRS complexes with broad morphology represent a left bundle branch block pattern.",
    "Right bundle branch block": "Wide terminal QRS forces create an RSR-prime style right bundle branch block pattern.",
    "Hyperkalemia pattern": "Tall peaked T waves with smaller P waves represent a classic educational hyperkalemia pattern.",
    "Prolonged QT": "The T wave is delayed, creating a long QT-style repolarization pattern.",
}


KEY_FEATURES = {
    "Normal sinus rhythm": ["Regular R-R intervals", "P before every QRS", "Narrow QRS"],
    "Sinus bradycardia": ["Sinus P waves", "Slow rate", "Regular rhythm"],
    "Sinus tachycardia": ["Sinus P waves", "Fast rate", "Regular rhythm"],
    "Sinus arrhythmia": ["Sinus P waves", "Variable R-R intervals", "Narrow QRS"],
    "Atrial fibrillation": ["Irregularly irregular", "No consistent P waves", "Variable R-R intervals"],
    "Atrial flutter": ["Flutter-wave baseline", "Atrial activity is organized", "Often patterned conduction"],
    "First-degree AV block": ["PR interval is prolonged", "One P for each QRS", "Usually narrow QRS"],
    "Second-degree AV block type I": ["Progressive PR lengthening", "Dropped QRS", "Grouped beating"],
    "Second-degree AV block type II": ["Dropped QRS complexes", "Constant PR intervals", "Intermittent conduction"],
    "Third-degree AV block": ["AV dissociation", "Slow escape rhythm", "P waves march through"],
    "PVCs": ["Early wide beat", "Different morphology", "Compensatory pause may follow"],
    "PACs": ["Early atrial beat", "Abnormal P wave", "Usually narrow QRS"],
    "Ventricular tachycardia": ["Fast rate", "Wide complexes", "Regular monomorphic pattern"],
    "Ventricular fibrillation": ["Chaotic waveform", "No organized QRS", "Irregular amplitude"],
    "Accelerated idioventricular rhythm": ["Wide complexes", "Regular rhythm", "Moderate ventricular rate"],
    "SVT": ["Fast regular rhythm", "Narrow complexes", "P waves may be hidden"],
    "Junctional rhythm": ["Regular narrow rhythm", "Absent P waves", "Rate often 40-60"],
    "Paced rhythm": ["Pacer spikes", "Wide paced complexes", "Regular capture"],
    "LVH pattern": ["Tall QRS voltage", "Strain-style T changes", "Narrow QRS pattern"],
    "Left bundle branch block": ["Wide QRS", "Broad ventricular morphology", "Secondary T-wave changes"],
    "Right bundle branch block": ["Wide QRS", "Terminal R-prime pattern", "Delayed right-sided activation"],
    "Hyperkalemia pattern": ["Tall peaked T waves", "Small P waves", "Slight QRS widening"],
    "Prolonged QT": ["Delayed T wave", "Long repolarization", "Narrow QRS"],
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
