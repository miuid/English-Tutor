import type { FeedbackOut } from './types'

const SESSION_KEY = 'et.sessionId'
const STUDENT_KEY = 'et.studentId'
const FEEDBACK_PREFIX = 'et.feedback.'

export function loadStoredSessionId(): string | null {
  return localStorage.getItem(SESSION_KEY)
}

export function saveStoredSessionId(id: string): void {
  localStorage.setItem(SESSION_KEY, id)
}

export function clearStoredSessionId(): void {
  localStorage.removeItem(SESSION_KEY)
}

export function loadStudentId(): string | null {
  return localStorage.getItem(STUDENT_KEY)
}

export function saveStudentId(id: string): void {
  localStorage.setItem(STUDENT_KEY, id)
}

// Final feedback is only returned by the submit call, not by GET /sessions,
// so it is cached locally to survive a page reload of an ended session.
export function loadFeedback(sessionId: string): FeedbackOut | null {
  try {
    const raw = localStorage.getItem(FEEDBACK_PREFIX + sessionId)
    return raw ? (JSON.parse(raw) as FeedbackOut) : null
  } catch {
    return null
  }
}

export function saveFeedback(sessionId: string, feedback: FeedbackOut): void {
  localStorage.setItem(FEEDBACK_PREFIX + sessionId, JSON.stringify(feedback))
}

export function clearFeedback(sessionId: string): void {
  localStorage.removeItem(FEEDBACK_PREFIX + sessionId)
}
