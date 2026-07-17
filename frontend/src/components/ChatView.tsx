import { useEffect, useRef, useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'
import {
  advanceSession,
  ApiError,
  getSession,
  startSession,
  submitText,
} from '../api'
import {
  clearFeedback,
  clearStoredSessionId,
  loadFeedback,
  loadStoredSessionId,
  saveFeedback,
  saveStoredSessionId,
} from '../storage'
import type { FeedbackOut, TurnOut } from '../types'

type Phase = 'loading' | 'start' | 'active'

interface ActiveSession {
  id: string
  stage: string
  ended: boolean
}

// Student-friendly labels for the loop stages / turn modes.
const STAGE_LABELS: Record<string, string> = {
  start: "Today's goal",
  'I do': "Watch how it's done",
  'we do': "Let's try together",
  'you do': 'Your turn',
  triage: 'Looking closely',
  coach: 'Coaching tip',
  end: 'Feedback',
  ended: 'Feedback',
}

function stageLabel(stage: string): string {
  return STAGE_LABELS[stage] ?? stage
}

const LEVEL_CLASS: Record<string, string> = {
  A: 'level-a',
  B: 'level-b',
  C: 'level-c',
  D: 'level-d',
  E: 'level-e',
}

function levelClass(level: string): string {
  return LEVEL_CLASS[level.trim().toUpperCase().charAt(0)] ?? 'level-c'
}

interface ChatViewProps {
  onStudent: (studentId: string) => void
}

export default function ChatView({ onStudent }: ChatViewProps) {
  const [phase, setPhase] = useState<Phase>('loading')
  const [session, setSession] = useState<ActiveSession | null>(null)
  const [turns, setTurns] = useState<TurnOut[]>([])
  const [feedback, setFeedback] = useState<FeedbackOut | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [taskPrompt, setTaskPrompt] = useState('')
  const [context, setContext] = useState('')
  const [draft, setDraft] = useState('')

  const bottomRef = useRef<HTMLDivElement>(null)
  const draftRef = useRef<HTMLTextAreaElement>(null)
  const lastActionRef = useRef<(() => Promise<void>) | null>(null)

  // Rebuild state from a stored session id on first load.
  useEffect(() => {
    const storedId = loadStoredSessionId()
    if (!storedId) {
      setPhase('start')
      return
    }
    let cancelled = false
    getSession(storedId)
      .then((state) => {
        if (cancelled) return
        onStudent(state.student_id)
        setSession({ id: state.id, stage: state.stage, ended: state.ended })
        setTurns(state.turns)
        setFeedback(state.ended ? loadFeedback(state.id) : null)
        setPhase('active')
      })
      .catch((err: unknown) => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 404) {
          clearStoredSessionId()
          setPhase('start')
        } else {
          setError(err instanceof Error ? err.message : 'Could not load your session.')
          setPhase('start')
        }
      })
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Keep the newest message in view.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [turns, busy, feedback])

  // Focus the input when it becomes the student's turn.
  useEffect(() => {
    if (session && (session.stage === 'we do' || session.stage === 'you do') && !session.ended) {
      draftRef.current?.focus()
    }
  }, [session])

  async function run(action: () => Promise<void>) {
    setBusy(true)
    setError(null)
    lastActionRef.current = action
    try {
      await action()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  function handleStart(e: FormEvent) {
    e.preventDefault()
    void run(async () => {
      const state = await startSession(taskPrompt, context)
      onStudent(state.student_id)
      saveStoredSessionId(state.id)
      setSession({ id: state.id, stage: state.stage, ended: state.ended })
      setTurns(state.turns)
      setFeedback(null)
      setDraft('')
      setPhase('active')
    })
  }

  function handleAdvance() {
    if (!session) return
    const id = session.id
    void run(async () => {
      const out = await advanceSession(id)
      setTurns((prev) => [...prev, out.turn])
      setSession({ id, stage: out.stage, ended: false })
    })
  }

  function handleSubmit() {
    const text = draft.trim()
    if (!session || !text) return
    const id = session.id
    void run(async () => {
      const out = await submitText(id, text)
      setTurns((prev) => [...prev, ...out.turns])
      setSession({ id, stage: out.stage, ended: out.ended })
      setDraft('')
      if (out.feedback) {
        setFeedback(out.feedback)
        saveFeedback(id, out.feedback)
      }
    })
  }

  function handleNewSession() {
    if (session) {
      clearStoredSessionId()
      clearFeedback(session.id)
    }
    setSession(null)
    setTurns([])
    setFeedback(null)
    setDraft('')
    setTaskPrompt('')
    setContext('')
    setError(null)
    setPhase('start')
  }

  function handleDraftKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      handleSubmit()
    }
  }

  if (phase === 'loading') {
    return (
      <div className="chat-shell centered" aria-live="polite">
        <p className="muted">Warming up…</p>
      </div>
    )
  }

  if (phase === 'start') {
    return (
      <div className="chat-shell">
        <section className="start-card">
          <h1 className="start-title">Ready for today's 15 minutes?</h1>
          <p className="start-sub">
            We'll set a goal together, watch how it's done, practise side by side, and
            finish with a piece of your own — with kind, honest feedback at the end.
          </p>
          {error ? (
            <p className="error-banner" role="alert">
              {error}
            </p>
          ) : null}
          <form onSubmit={handleStart} className="start-form">
            <label className="field-label" htmlFor="task-prompt">
              Paste my school task <span className="optional">(optional)</span>
            </label>
            <textarea
              id="task-prompt"
              className="text-input"
              rows={3}
              placeholder="e.g. Write an analytical paragraph about how the poet presents conflict…"
              value={taskPrompt}
              onChange={(e) => setTaskPrompt(e.target.value)}
              autoFocus
            />
            <label className="field-label" htmlFor="task-context">
              Anything your tutor should know? <span className="optional">(optional)</span>
            </label>
            <textarea
              id="task-context"
              className="text-input"
              rows={2}
              placeholder="e.g. Due Friday; teacher wants one TEEL paragraph."
              value={context}
              onChange={(e) => setContext(e.target.value)}
            />
            <button type="submit" className="btn primary" disabled={busy}>
              {busy ? 'Starting…' : "Start today's session"}
            </button>
          </form>
        </section>
      </div>
    )
  }

  const studentTurn = session !== null && !session.ended && (session.stage === 'we do' || session.stage === 'you do')
  const tutorLeading = session !== null && !session.ended && !studentTurn

  return (
    <div className="chat-shell">
      <div className="chat-header">
        <span className="stage-chip">{session ? stageLabel(session.ended ? 'ended' : session.stage) : ''}</span>
        <button type="button" className="btn ghost small" onClick={handleNewSession}>
          Start over
        </button>
      </div>

      <div className="messages" aria-live="polite" aria-label="Conversation with your tutor">
        {turns.map((turn) =>
          turn.kind === 'student' ? (
            <div key={turn.id} className="msg-row student">
              <div className="bubble student-bubble">
                <p className="bubble-text">{turn.text}</p>
              </div>
            </div>
          ) : (
            <div key={turn.id} className={`msg-row tutor${turn.mode === 'end' ? ' feedback-row' : ''}`}>
              <div className={`bubble tutor-bubble${turn.mode === 'end' ? ' feedback-bubble' : ''}`}>
                <span className="turn-chip">{stageLabel(turn.mode)}</span>
                <p className="bubble-text">{turn.text}</p>
                {turn.mode === 'end' && feedback ? (
                  <div className="level-badges" aria-label="Your levels for this piece">
                    {feedback.rubric_scores.map((score) => (
                      <span
                        key={score.criterion_name}
                        className={`level-badge ${levelClass(score.level)}`}
                        title={score.note ?? undefined}
                      >
                        <span className="level-badge-name">{score.criterion_name}</span>
                        <span className="level-badge-value">{score.level}</span>
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>
            </div>
          ),
        )}
        {busy ? (
          <div className="msg-row tutor">
            <div className="bubble tutor-bubble thinking" aria-label="Your tutor is thinking">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
          </div>
        ) : null}
        <div ref={bottomRef} />
      </div>

      {error ? (
        <div className="error-banner" role="alert">
          <span>{error}</span>
          <button
            type="button"
            className="btn ghost small"
            onClick={() => {
              const retry = lastActionRef.current
              if (retry) void run(retry)
            }}
          >
            Retry
          </button>
        </div>
      ) : null}

      <div className="composer">
        {session?.ended ? (
          <button type="button" className="btn primary wide" onClick={handleNewSession}>
            Start a new session
          </button>
        ) : tutorLeading ? (
          <button type="button" className="btn primary wide" onClick={handleAdvance} disabled={busy}>
            {busy ? 'One moment…' : 'Continue →'}
          </button>
        ) : (
          <form
            className="composer-form"
            onSubmit={(e) => {
              e.preventDefault()
              handleSubmit()
            }}
          >
            <label className="sr-only" htmlFor="student-draft">
              {session?.stage === 'you do' ? 'Write your own piece here' : 'Try it yourself here'}
            </label>
            <textarea
              id="student-draft"
              ref={draftRef}
              className="text-input composer-input"
              rows={3}
              placeholder={
                session?.stage === 'you do'
                  ? 'Write your own piece here… (Ctrl+Enter to hand in)'
                  : 'Have a go here — your tutor will help… (Ctrl+Enter to send)'
              }
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={handleDraftKeyDown}
              disabled={busy}
            />
            <div className="composer-actions">
              {session?.stage === 'we do' ? (
                <button type="button" className="btn ghost" onClick={handleAdvance} disabled={busy}>
                  Move on to my own piece →
                </button>
              ) : null}
              <button type="submit" className="btn primary" disabled={busy || !draft.trim()}>
                {session?.stage === 'you do' ? 'Hand in my writing' : 'Send'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
