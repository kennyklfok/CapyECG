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
  const width = 1200;
  const height = 760;
  const rowHeight = 160;
  const rhythmRowY = 560;
  const segmentWidth = width / 4;
  const segmentSamples = Math.round((waveform.sampleRate || 250) * 2.5);
  const leads = waveform.leads || synthesizeDisplayLeads(waveform.samples || []);
  const layout = [
    ["I", "aVR", "V1", "V4"],
    ["II", "aVL", "V2", "V5"],
    ["III", "aVF", "V3", "V6"],
  ];

  const buildPoints = (samples, xOffset, yCenter, segmentIndex = 0, samplesPerSegment = segmentSamples, drawWidth = segmentWidth) => {
    const start = segmentIndex * samplesPerSegment;
    const visibleSamples = samples.slice(start, start + samplesPerSegment);

    return visibleSamples
      .map((sample, index) => {
        const x = xOffset + (index / Math.max(1, visibleSamples.length - 1)) * drawWidth;
        const y = yCenter - sample * 48;
        return `${x.toFixed(1)},${Math.max(yCenter - 66, Math.min(yCenter + 66, y)).toFixed(1)}`;
      })
      .join(" ");
  };

  return (
    <div className="ecg-frame" aria-label="12-lead ECG">
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
        {[80, 240, 400, rhythmRowY].map((y) => (
          <line key={y} x1="0" x2={width} y1={y} y2={y} stroke="#e9aaa5" strokeWidth="1" />
        ))}
        {[1, 2, 3].map((column) => (
          <line
            key={column}
            x1={column * segmentWidth}
            x2={column * segmentWidth}
            y1="0"
            y2="480"
            stroke="#cf817c"
            strokeDasharray="8 8"
            strokeWidth="1.2"
          />
        ))}
        {layout.map((row, rowIndex) =>
          row.map((lead, columnIndex) => {
            const x = columnIndex * segmentWidth;
            const y = 80 + rowIndex * rowHeight;
            return (
              <g key={lead}>
                <text x={x + 16} y={y - 50} fill="#31433d" fontSize="24" fontWeight="800">
                  {lead}
                </text>
                <polyline
                  points={buildPoints(leads[lead] || [], x, y, columnIndex)}
                  fill="none"
                  stroke="#26332f"
                  strokeWidth="3"
                  strokeLinejoin="round"
                  strokeLinecap="round"
                />
              </g>
            );
          }),
        )}
        <text x="16" y={rhythmRowY - 52} fill="#31433d" fontSize="24" fontWeight="800">
          II
        </text>
        <polyline
          points={buildPoints(leads[waveform.rhythmLead || "II"] || waveform.samples || [], 0, rhythmRowY, 0, (leads.II || waveform.samples || []).length, width)}
          fill="none"
          stroke="#26332f"
          strokeWidth="3"
          strokeLinejoin="round"
          strokeLinecap="round"
        />
        <text x="1010" y="724" fill="#5f786c" fontSize="22" fontWeight="700">
          10 sec
        </text>
      </svg>
    </div>
  );
}

function synthesizeDisplayLeads(samples) {
  const profiles = {
    I: { scale: 0.82, invert: 1, offset: 0 },
    II: { scale: 1, invert: 1, offset: 0 },
    III: { scale: 0.74, invert: 1, offset: -0.01 },
    aVR: { scale: 0.72, invert: -1, offset: 0 },
    aVL: { scale: 0.54, invert: 1, offset: 0.01 },
    aVF: { scale: 0.88, invert: 1, offset: -0.005 },
    V1: { scale: 0.72, invert: -1, offset: 0 },
    V2: { scale: 0.82, invert: -1, offset: 0 },
    V3: { scale: 0.92, invert: 1, offset: 0 },
    V4: { scale: 1.14, invert: 1, offset: 0.005 },
    V5: { scale: 1.06, invert: 1, offset: 0 },
    V6: { scale: 0.94, invert: 1, offset: -0.005 },
  };

  return Object.fromEntries(
    Object.entries(profiles).map(([lead, profile]) => [
      lead,
      samples.map((sample) => clamp(sample * profile.scale * profile.invert + profile.offset, -1.7, 1.9)),
    ]),
  );
}

function clamp(value, low, high) {
  return Math.max(low, Math.min(high, value));
}
