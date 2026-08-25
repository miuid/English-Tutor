import { useEffect, useRef, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { createStudent, importStudent, listStudents } from '../api'
import { saveStudentId, saveStudentProfile } from '../storage'
import type { StudentOut } from '../types'

const TEXT_TYPES = ['analytical', 'persuasive', 'imaginative']

type Mode = 'loading' | 'pick' | 'create'

interface FirstRunWizardProps {
  onStudent: (student: StudentOut) => void
}

// Guided first run: shown when this browser has no student profile yet.
// The student either picks an existing profile (shared family server, new
// device) or creates a new one, then lands on the session start card.
export default function FirstRunWizard({ onStudent }: FirstRunWizardProps) {
  const [mode, setMode] = useState<Mode>('loading')
  const [existing, setExisting] = useState<StudentOut[]>([])
  const [name, setName] = useState('')
  const [yearLevel, setYearLevel] = useState(8)
  const [curriculum, setCurriculum] = useState('QCAA')
  const [focusTextTypes, setFocusTextTypes] = useState<string[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInput = useRef<HTMLInputElement | null>(null)

  useEffect(() => {
    let cancelled = false
    listStudents()
      .then((students) => {
        if (cancelled) return
        setExisting(students)
        setMode(students.length > 0 ? 'pick' : 'create')
      })
      .catch(() => {
        if (cancelled) return
        // Server unreachable or list failed: still allow creating a profile;
        // the create call will surface a clear error if the server is down.
        setMode('create')
      })
    return () => {
      cancelled = true
    }
  }, [])

  function finish(s: StudentOut) {
    saveStudentId(s.id)
    saveStudentProfile(s)
    onStudent(s)
  }

  function toggleTextType(type: string) {
    setFocusTextTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type],
    )
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const created = await createStudent({
        name,
        year_level: yearLevel,
        curriculum,
        focus_text_types: focusTextTypes.length > 0 ? focusTextTypes : undefined,
      })
      finish(created)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create the profile.')
      setBusy(false)
    }
  }

  // Restore a previously exported JSON backup as a new profile (fresh IDs,
  // progress preserved). This is how a family moves a student to a new
  // machine or recovers after a reset — no account, no cloud sync.
  async function handleRestoreFile(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return
    setBusy(true)
    setError(null)
    try {
      const text = await file.text()
      let payload: unknown
      try {
        payload = JSON.parse(text)
      } catch {
        throw new Error('That file is not valid JSON.')
      }
      const restored = await importStudent(payload)
      finish(restored)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Could not restore that backup file.',
      )
      setBusy(false)
    }
  }

  if (mode === 'loading') {
    return (
      <div className="profile-shell">
        <p className="muted">Getting things ready…</p>
      </div>
    )
  }

  return (
    <div className="profile-shell">
      <section className="profile-card">
        <h2 className="profile-title">Welcome to English Tutor 👋</h2>
        <p className="profile-sub">
          Fifteen focused minutes a day: set a goal, watch how it's done, practise
          together, then write your own piece with kind, honest feedback. First,
          let's find your profile.
        </p>
        {error ? (
          <p className="error-banner" role="alert">
            {error}
          </p>
        ) : null}

        {mode === 'pick' ? (
          <>
            <div className="wizard-list" role="group" aria-label="Existing profiles">
              {existing.map((s) => (
                <button
                  key={s.id}
                  type="button"
                  className="wizard-student"
                  onClick={() => finish(s)}
                  disabled={busy}
                >
                  <span className="wizard-student-name">{s.name}</span>
                  <span className="wizard-student-meta">
                    Year {s.year_level} · {s.curriculum}
                    {s.focus_text_types.length > 0
                      ? ` · ${s.focus_text_types.join(', ')}`
                      : ''}
                  </span>
                </button>
              ))}
            </div>
            <button
              type="button"
              className="btn ghost wide"
              onClick={() => setMode('create')}
            >
              Someone new →
            </button>
          </>
        ) : (
          <form onSubmit={handleCreate} className="profile-form">
            <label className="field-label" htmlFor="wizard-name">
              Your name
            </label>
            <input
              id="wizard-name"
              className="text-input"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Alex"
              required
              autoFocus
            />

            <label className="field-label" htmlFor="wizard-year">
              Year level
            </label>
            <select
              id="wizard-year"
              className="text-input"
              value={yearLevel}
              onChange={(e) => setYearLevel(Number(e.target.value))}
            >
              {[8, 9, 10, 11, 12].map((y) => (
                <option key={y} value={y}>
                  Year {y}
                </option>
              ))}
            </select>

            <label className="field-label" htmlFor="wizard-curriculum">
              Curriculum
            </label>
            <select
              id="wizard-curriculum"
              className="text-input"
              value={curriculum}
              onChange={(e) => setCurriculum(e.target.value)}
            >
              <option value="QCAA">QCAA (Queensland)</option>
              <option value="NESA">NESA (NSW)</option>
            </select>

            <span className="field-label">Focus text types (optional)</span>
            <div className="chip-group" role="group" aria-label="Focus text types">
              {TEXT_TYPES.map((type) => (
                <button
                  key={type}
                  type="button"
                  className={`chip${focusTextTypes.includes(type) ? ' active' : ''}`}
                  onClick={() => toggleTextType(type)}
                >
                  {type}
                </button>
              ))}
            </div>
            <p className="muted small">
              Leave empty to practise all text types. You can change everything later
              in the Profile tab.
            </p>

            <button
              type="submit"
              className="btn primary wide"
              disabled={busy || !name.trim()}
            >
              {busy ? 'Saving…' : 'Create profile & start'}
            </button>
            {existing.length > 0 ? (
              <button
                type="button"
                className="btn ghost wide"
                onClick={() => setMode('pick')}
              >
                ← Back to existing profiles
              </button>
            ) : null}
          </form>
        )}

        <input
          ref={fileInput}
          type="file"
          accept="application/json,.json"
          hidden
          onChange={handleRestoreFile}
        />
        <button
          type="button"
          className="btn ghost wide"
          disabled={busy}
          onClick={() => fileInput.current?.click()}
        >
          Restore from a backup file
        </button>
      </section>
    </div>
  )
}
