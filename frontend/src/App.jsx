import React from "react";
import capybaraIcon from "./assets/capybara-icon.png";
import { getHealth, getLearnMore, getNewCase, submitAnswer } from "./api.js";
import { Home } from "./components/Home.jsx";
import { Practice } from "./components/Practice.jsx";
import { SessionReview } from "./components/SessionReview.jsx";

const DISCLAIMER = "For training only. Not for clinical diagnosis.";

export function App() {
  const [screen, setScreen] = React.useState("home");
  const [difficulty, setDifficulty] = React.useState("Easy");
  const [sessionLength, setSessionLength] = React.useState(10);
  const [caseData, setCaseData] = React.useState(null);
  const [answer, setAnswer] = React.useState("");
  const [feedback, setFeedback] = React.useState(null);
  const [learnMore, setLearnMore] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [learningLoading, setLearningLoading] = React.useState(false);
  const [loadingText, setLoadingText] = React.useState("");
  const [isWarmingUp, setIsWarmingUp] = React.useState(true);
  const [error, setError] = React.useState("");
  const [score, setScore] = React.useState({ correct: 0, total: 0 });
  const [sessionResults, setSessionResults] = React.useState([]);
  const prefetchedCaseRef = React.useRef(null);
  const prefetchPromiseRef = React.useRef(null);

  React.useEffect(() => {
    let isMounted = true;

    getHealth()
      .catch(() => null)
      .finally(() => {
        if (isMounted) setIsWarmingUp(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  React.useEffect(() => {
    if (isWarmingUp || screen !== "home") return;
    prefetchCase(difficulty);
  }, [difficulty, isWarmingUp, screen]);

  function prefetchCase(selectedDifficulty) {
    if (prefetchedCaseRef.current?.difficulty === selectedDifficulty) {
      return Promise.resolve(prefetchedCaseRef.current.caseData);
    }
    if (prefetchPromiseRef.current?.difficulty === selectedDifficulty) {
      return prefetchPromiseRef.current.promise;
    }

    const promise = getNewCase(selectedDifficulty)
      .then((newCase) => {
        prefetchedCaseRef.current = {
          difficulty: selectedDifficulty,
          caseData: newCase,
        };
        return newCase;
      })
      .catch(() => null)
      .finally(() => {
        if (prefetchPromiseRef.current?.promise === promise) {
          prefetchPromiseRef.current = null;
        }
      });

    prefetchPromiseRef.current = {
      difficulty: selectedDifficulty,
      promise,
    };
    return promise;
  }

  async function startPractice() {
    setLoading(true);
    setLoadingText(
      isWarmingUp
        ? "Warming up the ECG room. First strip can take a moment..."
        : "Opening the next warmed-up rhythm strip..."
    );
    setError("");
    setFeedback(null);
    setLearnMore(null);
    setAnswer("");
    try {
      let nextCase = null;
      if (prefetchedCaseRef.current?.difficulty === difficulty) {
        nextCase = prefetchedCaseRef.current.caseData;
        prefetchedCaseRef.current = null;
      } else if (prefetchPromiseRef.current?.difficulty === difficulty) {
        nextCase = await prefetchPromiseRef.current.promise;
      }
      if (!nextCase) {
        nextCase = await getNewCase(difficulty);
      }
      setCaseData(nextCase);
      setScreen("practice");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setLoadingText("");
    }
  }

  async function handleSubmitAnswer(event) {
    event.preventDefault();
    if (!caseData || !answer) return;
    setLoading(true);
    setLoadingText("Capy is comparing the rhythm features...");
    setError("");
    try {
      const result = await submitAnswer(caseData.id, answer);
      setFeedback(result);
      if (!result.already_answered) {
        setScore((current) => ({
          correct: current.correct + (result.is_correct ? 1 : 0),
          total: current.total + 1,
        }));
        setSessionResults((current) => [
          ...current,
          {
            caseId: result.case_id,
            isCorrect: result.is_correct,
            submittedAnswer: result.submitted_answer,
            correctAnswer: result.correct_answer,
            difficulty: caseData.difficulty,
          },
        ]);
      }
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
      setLearnMore(await getLearnMore(caseData.id));
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
    setSessionResults([]);
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <button className="brand brand-button" onClick={resetSession} type="button">
          <span className="brand-mark">
            <img src={capybaraIcon} alt="" />
          </span>
          <div>
            <strong>CapyECG</strong>
            <span>Cozy ECG rhythm and pattern trainer</span>
          </div>
        </button>
        <p className="disclaimer">{DISCLAIMER}</p>
      </header>

      {screen === "home" && (
        <Home
          difficulty={difficulty}
          setDifficulty={setDifficulty}
          sessionLength={sessionLength}
          setSessionLength={setSessionLength}
          loading={loading}
          isWarmingUp={isWarmingUp}
          loadingText={loadingText}
          error={error}
          onStart={startPractice}
        />
      )}
      {screen === "practice" && (
        <Practice
          caseData={caseData}
          answer={answer}
          setAnswer={setAnswer}
          feedback={feedback}
          loading={loading}
          loadingText={loadingText}
          error={error}
          score={score}
          sessionLength={sessionLength}
          learnMore={learnMore}
          learningLoading={learningLoading}
          onSubmit={handleSubmitAnswer}
          onLearnMore={loadLearnMore}
          onNext={startPractice}
          onReview={() => setScreen("review")}
          onReset={resetSession}
        />
      )}
      {screen === "review" && (
        <SessionReview
          score={score}
          sessionLength={sessionLength}
          results={sessionResults}
          onRestart={resetSession}
        />
      )}
      <footer className="site-footer">
        <span>Created by KF</span>
        <span>Updated June 2026</span>
      </footer>
    </main>
  );
}
