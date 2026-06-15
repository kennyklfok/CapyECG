import React from "react";
import { RotateCcw } from "lucide-react";
import capybaraCoach from "../assets/capybara-coach.png";
import { EcgViewer, SourceLabel, SourceNote, StripStats } from "./EcgViewer.jsx";
import { FeedbackPanel } from "./FeedbackPanel.jsx";
import { LearnMorePanel } from "./LearnMorePanel.jsx";
import { LoadingCard } from "./LoadingCard.jsx";
import { WarmingStrip } from "./WarmingStrip.jsx";

export function Practice({
  caseData,
  answer,
  setAnswer,
  feedback,
  loading,
  loadingText,
  error,
  score,
  sessionLength,
  learnMore,
  learningLoading,
  onSubmit,
  onLearnMore,
  onNext,
  onReview,
  onReset,
}) {
  const feedbackRef = React.useRef(null);
  const isSessionComplete = feedback && score.total >= sessionLength;
  const currentStrip = Math.min(score.total + (feedback ? 0 : 1), sessionLength);

  React.useEffect(() => {
    if (!feedback || !feedbackRef.current) return;

    requestAnimationFrame(() => {
      feedbackRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
      feedbackRef.current?.focus({ preventScroll: true });
    });
  }, [feedback]);

  return (
    <section className="practice-layout">
      <div className="practice-header">
        <div>
          <span className="eyebrow">{caseData?.difficulty} practice</span>
          <h1>Identify the strip</h1>
        </div>
        <div className="practice-header-actions">
          <button className="secondary-button back-button" onClick={onReset} type="button">
            <RotateCcw size={16} />
            Main screen
          </button>
          <div className="score-pill">
            Score {score.correct}/{score.total} · Strip {currentStrip} of {sessionLength}
          </div>
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
            <strong>12-lead ECG</strong>
            <span>
              Standard 3x4 layout with Lead II rhythm strip / <SourceLabel sourceType={caseData?.source_type} />
            </span>
          </div>
        </div>
        {caseData?.waveform && <StripStats waveform={caseData.waveform} />}
        {caseData?.source_type && <SourceNote sourceType={caseData.source_type} />}
        {caseData ? <EcgViewer waveform={caseData.waveform} /> : <WarmingStrip />}
      </section>

      <form className="answer-panel" onSubmit={onSubmit}>
        <span className="answer-label">Choose the rhythm or ECG pattern</span>
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
      {feedback && <FeedbackPanel feedback={feedback} waveform={caseData?.waveform} ref={feedbackRef} />}
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
          <button
            className="primary-button"
            onClick={isSessionComplete ? onReview : onNext}
            type="button"
            disabled={loading}
          >
            {isSessionComplete ? "View session review" : "Next strip"}
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
