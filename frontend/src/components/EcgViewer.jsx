export function StripStats({ waveform }) {
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

export function SourceLabel({ sourceType }) {
  const labels = {
    "groq-generated": "AI-assisted educational case",
    "groq-cache": "Cached AI-assisted case",
    "groq-fallback": "Local case after AI timeout",
    "local-fallback": "Local educational case",
    synthetic: "Synthetic educational case",
  };

  return labels[sourceType] || "Educational case";
}

export function SourceNote({ sourceType }) {
  const notes = {
    "groq-generated": "AI drafted the prompt and answer choices; CapyECG generated the ECG strip from the stored answer.",
    "groq-cache": "This uses a cached AI draft with a freshly generated ECG strip.",
    "groq-fallback": "AI took too long, so CapyECG used a local educational case.",
    "local-fallback": "CapyECG used a local educational case without waiting on AI.",
    synthetic: "This strip is generated from a known educational rhythm template.",
  };

  return <p className="case-source-note">{notes[sourceType] || "Generated educational rhythm practice."}</p>;
}

export function EcgViewer({ waveform }) {
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
