import type {
  AdvanceOut,
  ProgressOut,
  SessionOut,
  StartSessionRequest,
  StudentCreate,
  StudentOut,
  StudentUpdate,
  SubmitOut,
} from './types'

export class ApiError extends Error {
  status: number

  constructor(status: number, detail: string) {
    super(detail)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(path, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    })
  } catch {
    throw new ApiError(0, 'Cannot reach the tutor server. Is the backend running?')
  }
  if (!res.ok) {
    let detail = `Something went wrong (${res.status}).`
    try {
      const body: unknown = await res.json()
      if (
        typeof body === 'object' &&
        body !== null &&
        'detail' in body &&
        typeof (body as { detail: unknown }).detail === 'string'
      ) {
        detail = (body as { detail: string }).detail
      }
    } catch {
      // keep the generic message
    }
    throw new ApiError(res.status, detail)
  }
  return (await res.json()) as T
}

export function startSession(
  taskPrompt: string,
  context: string,
  studentId?: string,
): Promise<SessionOut> {
  const body: StartSessionRequest = {}
  if (taskPrompt.trim()) body.task_prompt = taskPrompt.trim()
  if (context.trim()) body.context = context.trim()
  if (studentId) body.student_id = studentId
  return request<SessionOut>('/api/sessions', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export function createStudent(payload: StudentCreate): Promise<StudentOut> {
  return request<StudentOut>('/api/students', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function listStudents(): Promise<StudentOut[]> {
  return request<StudentOut[]>('/api/students')
}

export function getStudent(studentId: string): Promise<StudentOut> {
  return request<StudentOut>(`/api/students/${studentId}`)
}

export function updateStudent(
  studentId: string,
  payload: StudentUpdate,
): Promise<StudentOut> {
  return request<StudentOut>(`/api/students/${studentId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function getSession(sessionId: string): Promise<SessionOut> {
  return request<SessionOut>(`/api/sessions/${sessionId}`)
}

export function advanceSession(sessionId: string): Promise<AdvanceOut> {
  return request<AdvanceOut>(`/api/sessions/${sessionId}/advance`, { method: 'POST' })
}

export function submitText(sessionId: string, text: string): Promise<SubmitOut> {
  return request<SubmitOut>(`/api/sessions/${sessionId}/submit`, {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
}

export function pauseSession(sessionId: string): Promise<SessionOut> {
  return request<SessionOut>(`/api/sessions/${sessionId}/pause`, { method: 'POST' })
}

export function resumeSession(sessionId: string): Promise<SessionOut> {
  return request<SessionOut>(`/api/sessions/${sessionId}/resume`, { method: 'POST' })
}

export function getProgress(studentId: string): Promise<ProgressOut> {
  return request<ProgressOut>(`/api/students/${studentId}/progress`)
}
