import capybaraStudy from "../assets/capybara-study.png";

export function SessionReview({ score, sessionLength, results, onRestart }) {
  const percent = score.total ? Math.round((score.correct / score.total) * 100) : 0;
  const missedCounts = results
    .filter((result) => !result.isCorrect)
    .reduce((counts, result) => {
      counts[result.correctAnswer] = (counts[result.correctAnswer] || 0) + 1;
      return counts;
    }, {});
  const practiceNext = Object.entries(missedCounts)
    .sort((a, b) => b[1] - a[1])
    .map(([rhythm]) => rhythm)
    .slice(0, 3);

  return (
    <section className="review-layout">
      <div className="review-hero">
        <img src={capybaraStudy} alt="" />
        <div>
          <span className="eyebrow">Session review</span>
          <h1>Capy study soak</h1>
          <p>
            You scored <strong>{score.correct}/{score.total}</strong> ({percent}%) across this {sessionLength}-strip session.
          </p>
        </div>
      </div>

      <section className="review-panel">
        <div className="review-score">
          <strong>{percent}%</strong>
          <span>{score.correct} correct / {score.total} attempted</span>
        </div>
        <div>
          <h2>Practice these next</h2>
          {practiceNext.length ? (
            <ul className="practice-next-list">
              {practiceNext.map((rhythm) => (
                <li key={rhythm}>{rhythm}</li>
              ))}
            </ul>
          ) : (
            <p className="memory-tip">Clean session. Capy recommends moving up a difficulty or adding more strips.</p>
          )}
        </div>
      </section>

      <section className="review-panel">
        <h2>Missed strips</h2>
        {results.some((result) => !result.isCorrect) ? (
          <div className="missed-grid">
            {results
              .filter((result) => !result.isCorrect)
              .map((result) => (
                <div className="missed-item" key={result.caseId}>
                  <strong>{result.correctAnswer}</strong>
                  <span>You chose {result.submittedAnswer}</span>
                </div>
              ))}
          </div>
        ) : (
          <p>No missed rhythms or ECG patterns this round.</p>
        )}
      </section>

      <div className="action-row post-submit-actions">
        <button className="primary-button" onClick={onRestart} type="button">
          Start another session
        </button>
      </div>
    </section>
  );
}
