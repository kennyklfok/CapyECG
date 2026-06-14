import math
import random
from typing import Any


SAMPLE_RATE = 250
DURATION_SECONDS = 10


RHYTHMS = [
    "Normal sinus rhythm",
    "Sinus bradycardia",
    "Sinus tachycardia",
    "Atrial fibrillation",
    "Atrial flutter",
    "First-degree AV block",
    "PVCs",
    "PACs",
    "Ventricular tachycardia",
    "SVT",
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

    samples = []
    for index in range(SAMPLE_RATE * DURATION_SECONDS):
        t = index / SAMPLE_RATE
        value = _baseline(t, rng, noise_level)
        value += _atrial_activity(t, rhythm)

        for beat_index, beat_time in enumerate(beat_times):
            beat_kind = ectopic_beats.get(beat_index, "normal")
            value += _beat_waveform(t, beat_time, rhythm, beat_kind)

        samples.append(round(_clamp(value, -1.7, 1.9), 4))

    return {
        "sampleRate": SAMPLE_RATE,
        "durationSeconds": DURATION_SECONDS,
        "lead": "Lead II",
        "heartRate": _heart_rate(beat_times),
        "regularity": _regularity_label(rhythm, beat_times),
        "paperSpeed": "25 mm/s",
        "gain": "10 mm/mV",
        "calibration": "1 mV",
        "beatCount": len(beat_times),
        "samples": samples,
    }


def _heart_rate(beat_times: list[float]) -> int:
    if not beat_times:
        return 0
    return round(len(beat_times) * (60 / DURATION_SECONDS))


def _regularity_label(rhythm: str, beat_times: list[float]) -> str:
    if rhythm == "Atrial fibrillation":
        return "Irregularly irregular"
    if rhythm in {"PVCs", "PACs"}:
        return "Mostly regular with early beats"
    if len(beat_times) < 3:
        return "Not enough beats"
    intervals = [round(beat_times[i + 1] - beat_times[i], 2) for i in range(len(beat_times) - 1)]
    return "Regular" if max(intervals) - min(intervals) < 0.12 else "Irregular"


def _beat_times(rhythm: str, rng: random.Random) -> list[float]:
    if rhythm == "Atrial fibrillation":
        return _irregular_times(rng, 0.42, 1.18, start=0.45)
    if rhythm == "Ventricular tachycardia":
        return _regular_times(rng, 0.34, jitter=0.012, start=0.25)
    if rhythm == "SVT":
        return _regular_times(rng, 0.40, jitter=0.008, start=0.35)
    if rhythm == "Sinus bradycardia":
        return _regular_times(rng, 1.28, jitter=0.035, start=0.55)
    if rhythm == "Sinus tachycardia":
        return _regular_times(rng, 0.48, jitter=0.012, start=0.42)
    if rhythm == "Atrial flutter":
        return _regular_times(rng, 0.72, jitter=0.01, start=0.42)
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


def _beat_waveform(t: float, beat_time: float, rhythm: str, beat_kind: str) -> float:
    if rhythm == "Ventricular tachycardia":
        return _wide_complex(t, beat_time, amplitude=1.22, width=0.082, t_wave=False)
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
    if rhythm in {"Atrial fibrillation", "Atrial flutter", "SVT"}:
        p_amp = 0.0
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
    value += _gaussian(t, beat_time + 0.245, 0.085, t_amp)
    return value


def _wide_complex(t: float, beat_time: float, amplitude: float, width: float, t_wave: bool) -> float:
    value = 0.0
    value += _gaussian(t, beat_time - 0.045, width, -0.36 * amplitude)
    value += _gaussian(t, beat_time, width, amplitude)
    value += _gaussian(t, beat_time + 0.07, width * 1.05, -0.78 * amplitude)
    if t_wave:
        value += _gaussian(t, beat_time + 0.34, 0.13, -0.26)
    return value


def _gaussian(x: float, center: float, width: float, amplitude: float) -> float:
    return amplitude * math.exp(-((x - center) ** 2) / (2 * width**2))


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
