import type { FeedbackOut, StudentOut } from './types'

const SESSION_KEY = 'et.sessionId'
const STUDENT_KEY = 'et.studentId'
const STUDENT_PROFILE_KEY = 'et.studentProfile'
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

export function loadStudentProfile(): StudentOut | null {
  try {
    const raw = localStorage.getItem(STUDENT_PROFILE_KEY)
    return raw ? (JSON.parse(raw) as StudentOut) : null
  } catch {
    return null
  }
}

export function saveStudentProfile(student: StudentOut): void {
  localStorage.setItem(STUDENT_PROFILE_KEY, JSON.stringify(student))
}

export function clearStudentProfile(): void {
  localStorage.removeItem(STUDENT_PROFILE_KEY)
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
