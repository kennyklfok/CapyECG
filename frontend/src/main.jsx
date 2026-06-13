import React from "react";
import { createRoot } from "react-dom/client";
import { Activity, Play, RotateCcw } from "lucide-react";
import capybaraIcon from "./assets/capybara-icon.png";
import capybaraCoach from "./assets/capybara-coach.png";
import capybaraLoading from "./assets/capybara-loading.png";
import capybaraSpa from "./assets/capybara-spa.png";
import capybaraStudy from "./assets/capybara-study.png";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const DISCLAIMER = "For training only. Not for clinical diagnosis.";

function App() {
  const [screen, setScreen] = React.useState("home");
  const [difficulty, setDifficulty] = React.useState("Easy");
  const [caseData, setCaseData] = React.useState(null);
  const [answer, setAnswer] = React.useState("");
  const [feedback, setFeedback] = React.useState(null);
  const [learnMore, setLearnMore] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [learningLoading, setLearningLoading] = React.useState(false);
  const [loadingText, setLoadingText] = React.useState("");
  const [error, setError] = React.useState("");
  const [score, setScore] = React.useState({ correct: 0, total: 0 });

  async function startPractice() {
    setLoading(true);
    setLoadingText("Capy is checking their heart rhythm...");
    setError("");
    setFeedback(null);
    setLearnMore(null);
    setAnswer("");
    try {
      const params = new URLSearchParams({ difficulty });
      const response = await fetch(`${API_BASE}/api/cases/new?${params}`);
      if (!response.ok) throw new Error("Could not load ECG case.");
      setCaseData(await response.json());
      setScreen("practice");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setLoadingText("");
    }
  }

  async function submitAnswer(event) {
    event.preventDefault();
    if (!caseData || !answer) return;
    setLoading(true);
    setLoadingText("Capy is comparing the rhythm features...");
    setError("");
    try {
      const response = await fetch(`${API_BASE}/api/answers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ case_id: caseData.id, answer }),
      });
      if (!response.ok) throw new Error("Could not submit answer.");
      const result = await response.json();
      setFeedback(result);
      setScore((current) => ({
        correct: current.correct + (result.is_correct ? 1 : 0),
        total: current.total + 1,
      }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setLoadingText("");
    }
  }

  async function loadLearnMore() {
    if (!caseData || !feedback) return;
    setLearningLoading(true);
    setLoadingText("Capy is soaking up a deeper explanation...");
    setError("");
    try {
      const response = await fetch(`${API_BASE}/api/cases/${caseData.id}/learn-more`);
      if (!response.ok) throw new Error("Could not load the learning note.");
      setLearnMore(await response.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLearningLoading(false);
      setLoadingText("");
    }
  }

  function resetSession() {
    setScreen("home");
    setCaseData(null);
    setFeedback(null);
    setLearnMore(null);
    setAnswer("");
    setLoadingText("");
    setScore({ correct: 0, total: 0 });
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">
            <img src={capybaraIcon} alt="" />
          </span>
          <div>
            <strong>CapyECG</strong>
            <span>Cozy educational rhythm trainer</span>
          </div>
        </div>
        <p className="disclaimer">{DISCLAIMER}</p>
      </header>

      {screen === "home" ? (
        <Home
          difficulty={difficulty}
          setDifficulty={setDifficulty}
          loading={loading}
          loadingText={loadingText}
          error={error}
          onStart={startPractice}
        />
      ) : (
        <Practice
          caseData={caseData}
          answer={answer}
          setAnswer={setAnswer}
          feedback={feedback}
          loading={loading}
          loadingText={loadingText}
          error={error}
          score={score}
          learnMore={learnMore}
          learningLoading={learningLoading}
          onSubmit={submitAnswer}
          onLearnMore={loadLearnMore}
          onNext={startPractice}
          onReset={resetSession}
        />
      )}
    </main>
  );
}

function Home({
  difficulty,
  setDifficulty,
  loading,
  loadingText,
  error,
  onStart,
}) {
  return (
    <section className="home-layout">
      <div className="hero">
        <span className="eyebrow">10-second ECG rhythm strips</span>
        <h1>CapyECG</h1>
        <p className="lede">Practice interpreting 10-second ECG rhythm strips.</p>
        <p className="source-note">
          Pick a level and Groq helps write the educational prompt and answer choices.
          CapyECG renders the strip with a rhythm simulator.
        </p>
        <div className="spa-badges" aria-label="CapyECG theme details">
          <span>Green spa focus</span>
          <span>Orange-on-head mascot</span>
          <span>Educational ECG reps</span>
        </div>
        <p className="training-note">For training only. Not for clinical diagnosis.</p>
        <button className="primary-button" onClick={onStart} disabled={loading}>
          <Play size={18} />
          {loading ? "Getting strip..." : "Start practice"}
        </button>
        {loading && <LoadingCard text={loadingText} />}
        {error && <p className="error-text">{error}</p>}
      </div>

      <section className="setup-panel cozy-panel" aria-label="Practice setup">
        <CapybaraMascot />
        <h2>Practice setup</h2>
        <OptionGroup
          label="Choose your round"
          value={difficulty}
          onChange={setDifficulty}
          options={["Easy", "Medium", "Hard"]}
        />
      </section>
    </section>
  );
}

function CapybaraMascot() {
  return (
    <div className="capy-mascot">
      <img src={capybaraSpa} alt="Cute capybara relaxing in a cozy spa bath" />
      <p>Take a breath, read the strip, then commit.</p>
    </div>
  );
}

function OptionGroup({ label, value, onChange, options }) {
  return (
    <div className="option-group">
      <span>{label}</span>
      <div className="segmented">
        {options.map((option) => {
          const optionValue = Array.isArray(option) ? option[0] : option;
          const optionLabel = Array.isArray(option) ? option[1] : option;
          return (
            <button
              key={optionValue}
              className={value === optionValue ? "selected" : ""}
              onClick={() => onChange(optionValue)}
              type="button"
            >
              {optionLabel}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function Practice({
  caseData,
  answer,
  setAnswer,
  feedback,
  loading,
  loadingText,
  error,
  score,
  learnMore,
  learningLoading,
  onSubmit,
  onLearnMore,
  onNext,
  onReset,
}) {
  return (
    <section className="practice-layout">
      <div className="practice-header">
        <div>
          <span className="eyebrow">{caseData?.difficulty} practice</span>
          <h1>What rhythm is this?</h1>
        </div>
        <div className="score-pill">
          Score {score.correct}/{score.total}
        </div>
      </div>

      <section className="coach-card" aria-label="Capybara coach tip">
        <img src={capybaraCoach} alt="" />
        <div>
          <strong>Capy coach says: scan calmly.</strong>
          <span>Rate, regularity, P waves, PR interval, QRS width. Then choose.</span>
        </div>
      </section>

      {loading && <LoadingCard text={loadingText} />}

      <section className="strip-panel">
        <div className="strip-toolbar">
          <div>
            <strong>10-second rhythm strip</strong>
            <span>{caseData?.waveform?.lead || "Lead II"} / {caseData?.source_type}</span>
          </div>
          <div className="strip-companion">
            <img src={capybaraIcon} alt="" />
            <span>Static strip</span>
          </div>
        </div>
        {caseData?.waveform && <StripStats waveform={caseData.waveform} />}
        {caseData?.source_note && <p className="case-source-note">{caseData.source_note}</p>}
        {caseData && <EcgViewer waveform={caseData.waveform} />}
      </section>

      <form className="answer-panel" onSubmit={onSubmit}>
        <span className="answer-label">What rhythm is this?</span>
        <div className="choice-grid">
          {(caseData?.options || []).map((rhythm) => (
            <button
              key={rhythm}
              type="button"
              className={answer === rhythm ? "choice selected" : "choice"}
              onClick={() => setAnswer(rhythm)}
              disabled={Boolean(feedback) || loading}
            >
              {rhythm}
            </button>
          ))}
        </div>
        <div className="answer-row">
          <button className="primary-button" disabled={loading || !answer || Boolean(feedback)}>
            {loading ? "Checking..." : "Submit answer"}
          </button>
        </div>
      </form>

      {error && <p className="error-text">{error}</p>}
      {feedback && <FeedbackPanel feedback={feedback} />}
      {learnMore && <LearnMorePanel lesson={learnMore} />}

      {feedback && (
        <div className="action-row post-submit-actions">
          <button
            className="secondary-button"
            onClick={onLearnMore}
            type="button"
            disabled={learningLoading}
          >
            {learningLoading ? "Learning..." : "Learn more"}
          </button>
          <button className="primary-button" onClick={onNext} type="button" disabled={loading}>
            Next strip
          </button>
          <button className="quiet-button" onClick={onReset} type="button">
            <RotateCcw size={16} />
            Reset
          </button>
        </div>
      )}
    </section>
  );
}

function LoadingCard({ text }) {
  return (
    <section className="loading-card" role="status" aria-live="polite">
      <img src={capybaraLoading} alt="" />
      <div>
        <strong>{text || "Capy is checking their heart rhythm..."}</strong>
        <span>Warm bath, steady paws, clean ECG grid.</span>
      </div>
    </section>
  );
}

function StripStats({ waveform }) {
  const stats = [
    waveform.paperSpeed || "25 mm/s",
    waveform.gain || "10 mm/mV",
  ];

  return (
    <div className="strip-stats" aria-label="ECG strip settings">
      {stats.map((stat) => (
        <span key={stat}>{stat}</span>
      ))}
    </div>
  );
}

function EcgViewer({ waveform }) {
  const width = 1000;
  const height = 360;
  const visibleSamples = waveform.samples;
  const points = visibleSamples
    .map((sample, index) => {
      const x = (index / (visibleSamples.length - 1)) * width;
      const y = height / 2 - sample * 95;
      return `${x.toFixed(1)},${Math.max(20, Math.min(height - 20, y)).toFixed(1)}`;
    })
    .join(" ");

  return (
    <div className="ecg-frame" aria-label="ECG rhythm strip">
      <svg viewBox={`0 0 ${width} ${height}`} role="img">
        <defs>
          <pattern id="small-grid" width="10" height="10" patternUnits="userSpaceOnUse">
            <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#f2b6b1" strokeWidth="0.8" />
          </pattern>
          <pattern id="large-grid" width="50" height="50" patternUnits="userSpaceOnUse">
            <rect width="50" height="50" fill="url(#small-grid)" />
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#de8b86" strokeWidth="1.4" />
          </pattern>
        </defs>
        <rect width={width} height={height} fill="#fff8f7" />
        <rect width={width} height={height} fill="url(#large-grid)" />
        <line x1="0" x2={width} y1={height / 2} y2={height / 2} stroke="#e9aaa5" strokeWidth="1" />
        <text x="860" y="326" fill="#5f786c" fontSize="22" fontWeight="700">
          10 sec
        </text>
        <polyline points={points} fill="none" stroke="#26332f" strokeWidth="3.1" strokeLinejoin="round" strokeLinecap="round" />
      </svg>
    </div>
  );
}

function FeedbackPanel({ feedback }) {
  return (
    <section className={feedback.is_correct ? "feedback correct" : "feedback review"}>
      <div className="feedback-head">
        <img src={capybaraIcon} alt="" />
        <div>
          <div className="feedback-title">
            <Activity size={19} />
            <strong>{feedback.is_correct ? "Correct" : "Review this rhythm"}</strong>
          </div>
          <span>{feedback.is_correct ? "Nice warm-bath rhythm reading." : "No stress. Soak in the features."}</span>
        </div>
      </div>
      <p>
        Correct answer: <strong>{feedback.correct_answer}</strong>
      </p>
      <p>{feedback.explanation}</p>
      <ul>
        {feedback.key_features.map((feature) => (
          <li key={feature}>{feature}</li>
        ))}
      </ul>
      <small>{feedback.disclaimer}</small>
    </section>
  );
}

function LearnMorePanel({ lesson }) {
  return (
    <section className="learn-more-panel">
      <div className="feedback-head">
        <img src={capybaraStudy} alt="" />
        <div>
          <span className="eyebrow">Capy study soak</span>
          <h2>{lesson.rhythm}</h2>
        </div>
      </div>
      <p>{lesson.overview}</p>
      <div className="lesson-grid">
        <div>
          <strong>How to recognize it</strong>
          <ul>
            {lesson.how_to_recognize.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <strong>Common mix-ups</strong>
          <ul>
            {lesson.common_confusions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
      <p className="memory-tip">{lesson.memory_tip}</p>
      <small>{lesson.disclaimer}</small>
    </section>
  );
}

createRoot(document.getElementById("root")).render(<App />);
