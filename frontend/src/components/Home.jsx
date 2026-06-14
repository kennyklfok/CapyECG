import { Play } from "lucide-react";
import capybaraSpa from "../assets/capybara-spa.png";
import { LoadingCard } from "./LoadingCard.jsx";
import { OptionGroup } from "./OptionGroup.jsx";

export function Home({
  difficulty,
  setDifficulty,
  sessionLength,
  setSessionLength,
  loading,
  isWarmingUp,
  loadingText,
  error,
  onStart,
}) {
  return (
    <section className="home-layout">
      <div className="hero">
        <span className="eyebrow">AI-assisted ECG practice</span>
        <h1>CapyECG</h1>
        <p className="lede">Cozy 10-second rhythm and ECG pattern practice, generated for focused reps.</p>
        <p className="source-note">
          AI drafts the learning prompt and answer choices. CapyECG draws the strip from a known rhythm label.
        </p>
        <button className="primary-button" onClick={onStart} disabled={loading}>
          <Play size={18} />
          {loading ? "Getting strip..." : "Start practice"}
        </button>
        {isWarmingUp && !loading && (
          <p className="warmup-text">Warming up the backend so your first strip loads faster.</p>
        )}
        {loading && <LoadingCard text={loadingText} />}
        {error && <p className="error-text">{error}</p>}
      </div>

      <section className="setup-panel" aria-label="Practice setup">
        <CapybaraMascot />
        <h2>Practice setup</h2>
        <OptionGroup
          label="Choose your difficulty"
          value={difficulty}
          onChange={setDifficulty}
          options={["Easy", "Medium", "Hard"]}
        />
        <OptionGroup
          label="Strips this session"
          value={sessionLength}
          onChange={setSessionLength}
          options={[
            [5, "5"],
            [10, "10"],
            [15, "15"],
          ]}
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
