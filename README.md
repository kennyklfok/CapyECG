# CapyECG

Hosted on https://capyecg.onrender.com/

CapyECG is an educational ECG rhythm trainer for med students, ECG techs, paramedics, and nurses. It shows a synthetic 12-lead ECG with a 10-second Lead II rhythm strip, asks the learner to identify the rhythm, then reveals the known answer with short teaching points.

**For training only. Not for clinical diagnosis.**

## MVP Features

- React frontend with a cozy, clean practice workflow
- FastAPI backend with SQLite storage
- Groq-generated educational prompts and answer choices with CapyECG-rendered simulator strips
- In-memory Groq caching for repeated rhythm explanations and learning notes
- Standard 12-lead ECG view on continuous grid paper
- Cozy green spa theme with a capybara mascot balancing an orange
- Four-option multiple-choice rhythm answers and feedback panel
- Post-answer Learn more button for a short Groq-powered educational rhythm note
- Basic session score tracking
- Backend stores known rhythm labels and explanations

## Rhythm Categories

- Normal sinus rhythm
- Sinus bradycardia
- Sinus tachycardia
- Sinus arrhythmia
- Atrial fibrillation
- Atrial flutter
- First-degree AV block
- Second-degree AV block type I
- Second-degree AV block type II
- Third-degree AV block
- PVCs
- PACs
- Ventricular tachycardia
- Ventricular fibrillation
- Accelerated idioventricular rhythm
- SVT
- Junctional rhythm
- Paced rhythm
- LVH pattern
- Left bundle branch block
- Right bundle branch block
- Hyperkalemia pattern
- Prolonged QT

## Project Structure

```text
CapyECG/
  backend/
    app/
      database.py       SQLite setup and seed loading
      ecg_generator.py  Synthetic educational 12-lead waveform generation
      main.py           FastAPI routes
      schemas.py        API request/response models
      seed_data.py      MVP rhythm labels, features, explanations
    tests/
      test_api.py
    requirements.txt
  frontend/
    src/
      main.jsx          React app, screens, ECG viewer
      styles.css        UI styling and ECG grid styling
    index.html
    package.json
    vite.config.js
  README.md
```

## One-Command Dev

After backend and frontend dependencies are installed, run both servers from the project root:

```bash
npm run dev
```

This starts:

- FastAPI at `http://localhost:8000`
- Vite at `http://localhost:5173`

Press `Ctrl+C` to stop both.

## Backend Setup

First-time setup from the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

For Groq generation, create `backend/.env`:

```text
GROQ_API_KEY=your_groq_key_here
```

You can copy `backend/.env.example` as a starting point. If `GROQ_API_KEY` is not set, CapyECG uses a local educational fallback case generator so the app still runs.

Useful endpoints:

- `GET /api/health`
- `GET /api/rhythms`
- `GET /api/cases/new?difficulty=Easy`
- `POST /api/answers`
- `GET /api/cases/{case_id}/learn-more`

SQLite data is created at `backend/data/capyecg.sqlite3` when the app starts.

## Frontend Setup

First-time setup:

```powershell
cd frontend
npm install
```

After that, prefer the root `npm run dev` command.

If the backend is running somewhere else, set:

```powershell
$env:VITE_API_BASE="http://localhost:8000"
npm run dev
```

## Tests

From the project root after installing backend dependencies:

```powershell
pytest
```

## Safety And AI Behavior

CapyECG does not diagnose patients. The MVP returns explanations based on the stored known rhythm label and metadata for each case. Explanations are intentionally short and educational.

AI-generated case prompts may be influenced by public or licensed examples that are already interpreted, but the app should treat generated case content as educational simulation. Each case still needs a known stored label, curated features, four answer options, and provenance metadata. The UI and API should describe this as generated educational content, not patient data.

Groq generation is requested when a learner chooses Easy, Medium, or Hard. Groq selects the educational case metadata and choices; CapyECG renders the 12-lead ECG with rhythm-specific simulator templates. Future AI-assisted explanations should continue to use the generated/stored label, source metadata, and curated ECG features as ground truth. They should not claim to independently diagnose a strip or provide medical advice.

## Future Real ECG Dataset Integration

The current MVP stores CapyECG-rendered simulator waveform JSON in SQLite. To add AI-generated files, real samples, or reference-influenced generated cases later:

- Import source metadata into `ecg_cases`
- Store calibrated waveform arrays or image paths in `waveform_json`
- Use `source_type = 'dataset'`
- Keep the verified rhythm label and explanation attached to the case
- Add provenance fields such as dataset name, license, generation prompt/version, reference source category, lead, sampling rate, and annotator notes

Add dataset retrieval as a separate case source when the MVP is ready for imported examples.
