import { useState } from 'react'
import type { FormEvent } from 'react'
import { runMock } from '../api'
import type { MockOut, StudentOut } from '../types'
import Markdown from './Markdown'

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

interface MockViewProps {
  student: StudentOut
  onBack: () => void
}

// Weekly timed mock: one exam-conditions write, summative A–E feedback.
// No coaching or scaffolds — just like the real thing. The result lands on
// the Progress chart as a diamond, distinct from daily practice circles.
export default function MockView({ student, onBack }: MockViewProps) {
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<MockOut | null>(null)

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    runMock(student.id, text)
      .then(setResult)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.')
      })
      .finally(() => setBusy(false))
  }

  if (result) {
    return (
      <div className="chat-shell">
        <section className="start-card">
          <h1 className="start-title">Your exam-style feedback</h1>
          <div className="level-badges" aria-label="Your levels for this mock">
            {result.feedback.rubric_scores.map((s) => (
              <span key={s.criterion_name} className={`level-badge ${levelClass(s.level)}`} title={s.note ?? undefined}>
                <span className="level-badge-name">{s.criterion_name}</span>
                <span className="level-badge-value">{s.level}</span>
              </span>
            ))}
          </div>
          <Markdown text={result.report} className="mock-report" />
          <p className="muted">This mock is on your Progress chart as a ◆ diamond.</p>
          <button type="button" className="btn primary" onClick={onBack}>
            Back to today
          </button>
        </section>
      </div>
    )
  }

  return (
    <div className="chat-shell">
      <section className="start-card">
        <h1 className="start-title">This week's timed mock</h1>
        <p className="start-sub">
          Just like the real thing: one timed sitting, no hints and no coaching. Paste the
          piece you wrote under exam conditions and I'll give you honest A–E feedback —
          one strength and the 1–2 moves that would lift it most.
        </p>
        {error ? (
          <p className="error-banner" role="alert">
            {error}
          </p>
        ) : null}
        <form onSubmit={handleSubmit} className="start-form">
          <label className="field-label" htmlFor="mock-text">
            My timed piece
          </label>
          <textarea
            id="mock-text"
            className="text-input"
            rows={10}
            placeholder="Paste the essay or paragraph you wrote under exam conditions…"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <button type="submit" className="btn primary" disabled={busy || !text.trim()}>
            {busy ? 'Marking…' : 'Get my exam-style feedback'}
          </button>
          <button type="button" className="btn ghost" onClick={onBack} disabled={busy}>
            Not today
          </button>
        </form>
      </section>
    </div>
  )
}
