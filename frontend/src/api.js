const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function getHealth() {
  const response = await fetch(`${API_BASE}/api/health`);
  if (!response.ok) throw new Error("Could not reach CapyECG.");
  return response.json();
}

export async function getNewCase(difficulty) {
  const params = new URLSearchParams({ difficulty });
  const response = await fetch(`${API_BASE}/api/cases/new?${params}`);
  if (!response.ok) throw new Error("Could not load ECG case.");
  return response.json();
}

export async function submitAnswer(caseId, answer) {
  const response = await fetch(`${API_BASE}/api/answers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ case_id: caseId, answer }),
  });
  if (!response.ok) throw new Error("Could not submit answer.");
  return response.json();
}

export async function getLearnMore(caseId) {
  const response = await fetch(`${API_BASE}/api/cases/${caseId}/learn-more`);
  if (!response.ok) throw new Error("Could not load the learning note.");
  return response.json();
}
