const API_BASE = import.meta.env.VITE_API_URL ?? "";

export type MentorMatch = {
  id: string;
  name: string;
  title: string;
  expertise: string[];
  bio: string;
  match_score: number;
  match_reason: string;
};

export type JobMatch = {
  id: string;
  title: string;
  company: string;
  location: string;
  type: string;
  summary: string;
  match_reason: string;
};

export type MatchResponse = {
  summary: string;
  interpreted_goals: string[];
  skills: string[];
  industry_focus: string | null;
  mentors: MentorMatch[];
  jobs: JobMatch[];
  next_steps: string[];
};

export async function postMatchQuery(message: string): Promise<MatchResponse> {
  console.log('Making API call to:', `${API_BASE}/api/match`, 'with message:', message);
  const res = await fetch(`${API_BASE}/api/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    cache: 'no-cache',
  });
  console.log('API response status:', res.status);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    console.error('API error response:', err);
    throw new Error((err as { detail?: string }).detail ?? res.statusText);
  }
  const data = await res.json();
  console.log('API response data:', data);
  return data;
}
