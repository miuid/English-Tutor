// API types mirroring backend/app/api/schemas.py

export interface StudentOut {
  id: string
  name: string
  year_level: number
  curriculum: string
  focus_text_types: string[]
  created_at: string
}

export interface StudentCreate {
  name: string
  year_level: number
  curriculum?: string
  focus_text_types?: string[]
}

export interface StudentUpdate {
  name?: string
  year_level?: number
  curriculum?: string
  focus_text_types?: string[]
}

export interface TurnOut {
  id: string
  kind: string // "tutor" | "student"
  skill: string | null
  task_type: string
  mode: string
  text: string
  prompt: string
  created_at: string
}

export interface SessionOut {
  id: string
  student_id: string
  stage: string
  ended: boolean
  paused: boolean
  learning_intention: string | null
  time_limit_seconds: number
  time_spent_seconds: number
  time_up: boolean
  turns: TurnOut[]
}

export interface StartSessionRequest {
  task_prompt?: string
  context?: string
  student_id?: string
  year_level?: string
  text_type?: string
}

export interface AdvanceOut {
  session_id: string
  stage: string
  turn: TurnOut
  time_up: boolean
  paused: boolean
}

export interface RubricScoreOut {
  criterion_name: string
  level: string
  note: string | null
  scored_at: string
}

export interface FeedbackOut {
  id: string
  strength: string
  next_steps: string
  rubric_scores: RubricScoreOut[]
}

export interface SubmitOut {
  session_id: string
  stage: string
  ended: boolean
  turns: TurnOut[]
  feedback: FeedbackOut | null
  time_up: boolean
  paused: boolean
}

export interface ProgressScoreOut {
  criterion_name: string
  level: string
  note: string | null
  scored_at: string
  session_id: string
  feedback_id: string
}

export interface ProgressOut {
  student_id: string
  scores: ProgressScoreOut[]
}
