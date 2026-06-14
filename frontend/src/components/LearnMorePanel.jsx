import capybaraStudy from "../assets/capybara-study.png";

export function LearnMorePanel({ lesson }) {
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
    </section>
  );
}
