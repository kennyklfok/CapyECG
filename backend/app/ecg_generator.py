import math
import random
from typing import Any


SAMPLE_RATE = 250
DURATION_SECONDS = 10
STANDARD_12_LEADS = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]


LEAD_PROFILES = {
    "I": {"scale": 0.82, "invert": 1, "offset": 0.0},
    "II": {"scale": 1.0, "invert": 1, "offset": 0.0},
    "III": {"scale": 0.74, "invert": 1, "offset": -0.01},
    "aVR": {"scale": 0.72, "invert": -1, "offset": 0.0},
    "aVL": {"scale": 0.54, "invert": 1, "offset": 0.01},
    "aVF": {"scale": 0.88, "invert": 1, "offset": -0.005},
    "V1": {"scale": 0.72, "invert": -1, "offset": 0.0},
    "V2": {"scale": 0.82, "invert": -1, "offset": 0.0},
    "V3": {"scale": 0.92, "invert": 1, "offset": 0.0},
    "V4": {"scale": 1.14, "invert": 1, "offset": 0.005},
    "V5": {"scale": 1.06, "invert": 1, "offset": 0.0},
    "V6": {"scale": 0.94, "invert": 1, "offset": -0.005},
}


RHYTHMS = [
    "Normal sinus rhythm",
    "Sinus bradycardia",
    "Sinus tachycardia",
    "Sinus arrhythmia",
    "Atrial fibrillation",
    "Atrial flutter",
    "First-degree AV block",
    "Second-degree AV block type I",
    "Second-degree AV block type II",
    "Third-degree AV block",
    "PVCs",
    "PACs",
    "Ventricular tachycardia",
    "Ventricular fibrillation",
    "Accelerated idioventricular rhythm",
    "SVT",
    "Junctional rhythm",
    "Paced rhythm",
    "LVH pattern",
    "Left bundle branch block",
    "Right bundle branch block",
    "Hyperkalemia pattern",
    "Prolonged QT",
]


def generate_waveform(
    rhythm: str,
    difficulty: str = "Beginner",
    seed: int | None = None,
) -> dict[str, Any]:
    rng = random.Random(seed if seed is not None else random.randrange(1_000_000))
    beat_times = _beat_times(rhythm, rng)
    ectopic_beats = _ectopic_beats(rhythm, beat_times)
    noise_level = {"Beginner": 0.006, "Intermediate": 0.018, "Advanced": 0.035}[difficulty]

    lead_samples = {lead: [] for lead in STANDARD_12_LEADS}
    for index in range(SAMPLE_RATE * DURATION_SECONDS):
        t = index / SAMPLE_RATE
        base_value = _baseline(t, rng, noise_level)
        base_value += _atrial_activity(t, rhythm)
        base_value += _standalone_p_waves(t, rhythm)

        if rhythm == "Ventricular fibrillation":
            base_value += _vfib_activity(t, rng)
        else:
            for beat_index, beat_time in enumerate(beat_times):
                beat_kind = ectopic_beats.get(beat_index, "normal")
                base_value += _beat_waveform(t, beat_time, rhythm, beat_kind)

        for lead in STANDARD_12_LEADS:
            lead_samples[lead].append(_shape_lead_value(base_value, t, rhythm, lead))

    return {
        "sampleRate": SAMPLE_RATE,
        "durationSeconds": DURATION_SECONDS,
        "lead": "12-lead ECG",
        "displayLayout": "standard-3x4-plus-rhythm",
        "rhythmLead": "II",
        "leadOrder": STANDARD_12_LEADS,
        "heartRate": _heart_rate(beat_times),
        "regularity": _regularity_label(rhythm, beat_times),
        "paperSpeed": "25 mm/s",
        "gain": "10 mm/mV",
        "calibration": "1 mV",
        "beatCount": len(beat_times),
        "samples": lead_samples["II"],
        "leads": lead_samples,
    }


def _shape_lead_value(base_value: float, t: float, rhythm: str, lead: str) -> float:
    profile = LEAD_PROFILES[lead]
    value = base_value * profile["scale"] * profile["invert"] + profile["offset"]

    if rhythm == "LVH pattern" and lead in {"I", "aVL", "V5", "V6"}:
        value *= 1.24
        value += _gaussian(t % 0.84, 0.72, 0.09, -0.10)
    if rhythm == "Right bundle branch block" and lead in {"V1", "V2"}:
        value *= -1.12
    if rhythm == "Left bundle branch block" and lead in {"V5", "V6", "I", "aVL"}:
        value *= 1.16
    if rhythm == "Hyperkalemia pattern" and lead.startswith("V"):
        value *= 1.08
    if rhythm == "Ventricular tachycardia" and lead in {"aVR", "V1", "V2"}:
        value *= -1.0

    return round(_clamp(value, -1.7, 1.9), 4)


def _heart_rate(beat_times: list[float]) -> int:
    if not beat_times:
        return 0
    return round(len(beat_times) * (60 / DURATION_SECONDS))


def _regularity_label(rhythm: str, beat_times: list[float]) -> str:
    if rhythm == "Ventricular fibrillation":
        return "Chaotic"
    if rhythm == "Atrial fibrillation":
        return "Irregularly irregular"
    if rhythm in {"Sinus arrhythmia", "Second-degree AV block type I", "Second-degree AV block type II"}:
        return "Irregular"
    if rhythm == "Third-degree AV block":
        return "AV dissociation"
    if rhythm in {"PVCs", "PACs"}:
        return "Mostly regular with early beats"
    if len(beat_times) < 3:
        return "Not enough beats"
    intervals = [round(beat_times[i + 1] - beat_times[i], 2) for i in range(len(beat_times) - 1)]
    return "Regular" if max(intervals) - min(intervals) < 0.12 else "Irregular"


def _beat_times(rhythm: str, rng: random.Random) -> list[float]:
    if rhythm == "Ventricular fibrillation":
        return []
    if rhythm == "Atrial fibrillation":
        return _irregular_times(rng, 0.42, 1.18, start=0.45)
    if rhythm == "Ventricular tachycardia":
        return _regular_times(rng, 0.34, jitter=0.012, start=0.25)
    if rhythm == "Accelerated idioventricular rhythm":
        return _regular_times(rng, 0.86, jitter=0.025, start=0.35)
    if rhythm == "SVT":
        return _regular_times(rng, 0.40, jitter=0.008, start=0.35)
    if rhythm == "Junctional rhythm":
        return _regular_times(rng, 1.02, jitter=0.018, start=0.52)
    if rhythm == "Paced rhythm":
        return _regular_times(rng, 0.92, jitter=0.002, start=0.45)
    if rhythm == "Sinus bradycardia":
        return _regular_times(rng, 1.28, jitter=0.035, start=0.55)
    if rhythm == "Sinus tachycardia":
        return _regular_times(rng, 0.48, jitter=0.012, start=0.42)
    if rhythm == "Sinus arrhythmia":
        return _sinus_arrhythmia_times(rng)
    if rhythm == "Atrial flutter":
        return _regular_times(rng, 0.72, jitter=0.01, start=0.42)
    if rhythm == "Second-degree AV block type I":
        return [0.48, 1.34, 2.34, 3.98, 4.84, 5.84, 7.48, 8.34, 9.34]
    if rhythm == "Second-degree AV block type II":
        return [0.48, 1.36, 3.12, 4.0, 5.76, 6.64, 8.4, 9.28]
    if rhythm == "Third-degree AV block":
        return _regular_times(rng, 1.55, jitter=0.01, start=0.72)
    return _regular_times(rng, 0.84, jitter=0.025, start=0.48)


def _regular_times(rng: random.Random, interval: float, jitter: float, start: float) -> list[float]:
    times = []
    t = start
    while t < DURATION_SECONDS:
        times.append(t)
        t += interval + rng.uniform(-jitter, jitter)
    return times


def _irregular_times(rng: random.Random, low: float, high: float, start: float) -> list[float]:
    times = []
    t = start
    while t < DURATION_SECONDS:
        times.append(t)
        t += rng.uniform(low, high)
    return times


def _sinus_arrhythmia_times(rng: random.Random) -> list[float]:
    times = []
    t = 0.48
    index = 0
    while t < DURATION_SECONDS:
        interval = 0.82 + 0.18 * math.sin(index * 0.85) + rng.uniform(-0.025, 0.025)
        times.append(t)
        t += interval
        index += 1
    return times


def _ectopic_beats(rhythm: str, beat_times: list[float]) -> dict[int, str]:
    if rhythm == "PVCs" and len(beat_times) > 5:
        beat_times[3] = max(0.25, beat_times[3] - 0.28)
        beat_times[4] = beat_times[3] + 1.08
        return {3: "pvc"}
    if rhythm == "PACs" and len(beat_times) > 6:
        beat_times[4] = max(0.25, beat_times[4] - 0.24)
        return {4: "pac"}
    return {}


def _baseline(t: float, rng: random.Random, noise_level: float) -> float:
    wander = 0.025 * math.sin(2 * math.pi * 0.23 * t)
    fine_noise = rng.uniform(-noise_level, noise_level)
    return wander + fine_noise


def _atrial_activity(t: float, rhythm: str) -> float:
    if rhythm == "Atrial flutter":
        phase = (t * 5.0) % 1.0
        saw = 2.0 * abs(2.0 * phase - 1.0) - 1.0
        return 0.18 * saw
    if rhythm == "Atrial fibrillation":
        return (
            0.035 * math.sin(2 * math.pi * 6.6 * t)
            + 0.022 * math.sin(2 * math.pi * 8.9 * t + 0.8)
        )
    return 0.0


def _standalone_p_waves(t: float, rhythm: str) -> float:
    if rhythm == "Second-degree AV block type I":
        p_times = [0.31, 1.14, 2.11, 3.08, 3.81, 4.64, 5.61, 6.58, 7.31, 8.14, 9.11]
        return sum(_gaussian(t, p_time, 0.032, 0.15) for p_time in p_times)
    if rhythm == "Second-degree AV block type II":
        p_times = [0.31, 1.19, 2.07, 2.95, 3.83, 4.71, 5.59, 6.47, 7.35, 8.23, 9.11]
        return sum(_gaussian(t, p_time, 0.03, 0.15) for p_time in p_times)
    if rhythm == "Third-degree AV block":
        p_times = [0.18 + 0.66 * index for index in range(16)]
        return sum(_gaussian(t, p_time, 0.028, 0.14) for p_time in p_times)
    return 0.0


def _vfib_activity(t: float, rng: random.Random) -> float:
    coarse = 0.55 * math.sin(2 * math.pi * 4.8 * t + 0.6 * math.sin(2 * math.pi * 0.7 * t))
    fine = 0.22 * math.sin(2 * math.pi * 8.4 * t + 1.7)
    return coarse + fine + rng.uniform(-0.12, 0.12)


def _beat_waveform(t: float, beat_time: float, rhythm: str, beat_kind: str) -> float:
    if rhythm == "Ventricular tachycardia":
        return _wide_complex(t, beat_time, amplitude=1.22, width=0.082, t_wave=False)
    if rhythm in {"Left bundle branch block", "Paced rhythm"}:
        value = _wide_complex(t, beat_time, amplitude=1.18, width=0.092, t_wave=True)
        if rhythm == "Paced rhythm":
            value += _pacing_spike(t, beat_time - 0.045)
        return value
    if rhythm == "Right bundle branch block":
        return _rbbb_complex(t, beat_time)
    if beat_kind == "pvc":
        return _wide_complex(t, beat_time, amplitude=1.32, width=0.07, t_wave=True)

    pr_delay = 0.17
    p_amp = 0.13
    p_width = 0.032
    qrs_width = 0.018
    qrs_amp = 1.08
    t_amp = 0.30

    if rhythm == "First-degree AV block":
        pr_delay = 0.30
    if rhythm in {"Second-degree AV block type I", "Second-degree AV block type II", "Third-degree AV block"}:
        p_amp = 0.0
    if rhythm in {"Atrial fibrillation", "Atrial flutter", "SVT"}:
        p_amp = 0.0
    if rhythm == "Junctional rhythm":
        p_amp = -0.08
        pr_delay = -0.08
    if rhythm == "LVH pattern":
        qrs_amp = 1.62
        t_amp = -0.18
    if rhythm == "Hyperkalemia pattern":
        p_amp = 0.05
        qrs_width = 0.026
        t_amp = 0.78
    if rhythm == "Prolonged QT":
        t_amp = 0.28
    if rhythm == "Sinus tachycardia":
        pr_delay = 0.14
        p_amp = 0.18
        p_width = 0.026
    if beat_kind == "pac":
        p_amp = 0.18
        p_width = 0.024
        pr_delay = 0.12
    if rhythm == "SVT":
        qrs_amp = 0.98
        t_amp = 0.22

    value = 0.0
    value += _gaussian(t, beat_time - pr_delay, p_width, p_amp)
    value += _gaussian(t, beat_time - 0.018, qrs_width, -0.20)
    value += _gaussian(t, beat_time, qrs_width, qrs_amp)
    value += _gaussian(t, beat_time + 0.026, qrs_width, -0.34)
    t_center = beat_time + (0.42 if rhythm == "Prolonged QT" else 0.245)
    t_width = 0.12 if rhythm in {"Hyperkalemia pattern", "Prolonged QT"} else 0.085
    value += _gaussian(t, t_center, t_width, t_amp)
    return value


def _wide_complex(t: float, beat_time: float, amplitude: float, width: float, t_wave: bool) -> float:
    value = 0.0
    value += _gaussian(t, beat_time - 0.045, width, -0.36 * amplitude)
    value += _gaussian(t, beat_time, width, amplitude)
    value += _gaussian(t, beat_time + 0.07, width * 1.05, -0.78 * amplitude)
    if t_wave:
        value += _gaussian(t, beat_time + 0.34, 0.13, -0.26)
    return value


def _rbbb_complex(t: float, beat_time: float) -> float:
    value = 0.0
    value += _gaussian(t, beat_time - 0.018, 0.018, -0.16)
    value += _gaussian(t, beat_time, 0.022, 0.92)
    value += _gaussian(t, beat_time + 0.052, 0.026, -0.28)
    value += _gaussian(t, beat_time + 0.095, 0.032, 0.56)
    value += _gaussian(t, beat_time + 0.255, 0.09, 0.24)
    return value


def _pacing_spike(t: float, spike_time: float) -> float:
    return _gaussian(t, spike_time, 0.004, 1.35) - _gaussian(t, spike_time + 0.006, 0.004, 0.85)


def _gaussian(x: float, center: float, width: float, amplitude: float) -> float:
    return amplitude * math.exp(-((x - center) ** 2) / (2 * width**2))


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
