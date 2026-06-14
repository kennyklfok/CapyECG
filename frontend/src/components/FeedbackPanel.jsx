import React from "react";
import { Activity } from "lucide-react";
import capybaraIcon from "../assets/capybara-icon.png";

export const FeedbackPanel = React.forwardRef(function FeedbackPanel({ feedback, waveform }, ref) {
  return (
    <section
      ref={ref}
      className={feedback.is_correct ? "feedback correct" : "feedback review"}
      tabIndex={-1}
    >
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
      {waveform && (
        <div className="post-answer-stats" aria-label="Post-answer ECG clues">
          <span>Rate: {waveform.heartRate} bpm</span>
          <span>Regularity: {waveform.regularity}</span>
        </div>
      )}
      <ul>
        {feedback.key_features.map((feature) => (
          <li key={feature}>{feature}</li>
        ))}
      </ul>
    </section>
  );
});
