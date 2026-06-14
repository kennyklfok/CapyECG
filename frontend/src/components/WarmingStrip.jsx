export function WarmingStrip({ compact = false }) {
  return (
    <div className={compact ? "warming-strip compact" : "warming-strip"} aria-hidden="true">
      <div className="warming-grid">
        <svg viewBox="0 0 420 90" preserveAspectRatio="none">
          <polyline
            points="0,50 30,50 42,18 58,72 72,50 118,50 130,18 146,72 160,50 206,50 218,18 234,72 248,50 294,50 306,18 322,72 336,50 382,50 394,18 410,72 420,50"
            fill="none"
            stroke="#2f3a36"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="5"
          />
        </svg>
      </div>
      <span className="warming-sweep" />
    </div>
  );
}
