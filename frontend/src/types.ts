// API types mirroring backend/app/api/schemas.py

export interface StudentOut {
  id: string
  name: string
  year_level: number
  curriculum: string
  focus_text_types: string[]
  weekly_goal: number
  coach_tone: string
  created_at: string
}

export interface StudentCreate {
  name: string
  year_level: number
  curriculum?: string
  focus_text_types?: string[]
  weekly_goal?: number
  coach_tone?: string
}

export interface StudentUpdate {
  name?: string
  year_level?: number
  curriculum?: string
  focus_text_types?: string[]
  weekly_goal?: number
  coach_tone?: string
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
  mode: string // attempt mode: daily loop stage, "baseline", or "assessment" (weekly mock)
}

export interface ProgressOut {
  student_id: string
  scores: ProgressScoreOut[]
}

export interface MockOut {
  session_id: string
  feedback: FeedbackOut
  report: string
}

export interface MotivationOut {
  student_id: string
  current_streak: number
  streak_broken: boolean // lapsed run -> show a recovery prompt, never a penalty
  weekly_goal: number
  sessions_this_week: number
  goal_met: boolean
  last_activity_date: string | null
}

export interface LevelUpOut {
  criterion_name: string
  from_level: string
  to_level: string
  note: string | null // rubric note recorded with the new score — the improvement mechanism
  scored_at: string
  session_id: string
  feedback_id: string
}

export interface LevelUpsOut {
  student_id: string
  level_ups: LevelUpOut[]
}
