import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError, createStudent, getStudent, updateStudent } from '../api'
import type { StudentOut } from '../types'
import {
  clearStudentId,
  clearStudentProfile,
  loadStudentId,
  loadStudentProfile,
  saveStudentId,
  saveStudentProfile,
} from '../storage'

const TEXT_TYPES = ['analytical', 'persuasive', 'imaginative']

const COACH_TONES = [
  { value: 'warm', label: 'Warm', hint: 'Encouraging — effort first, gentle correction' },
  { value: 'strict', label: 'Strict', hint: 'Direct — names the problem, holds the standard' },
  { value: 'humorous', label: 'Humorous', hint: 'Playful — light jokes, clear teaching point' },
] as const

type Mode = 'loading' | 'empty' | 'edit' | 'saved'

interface ProfileViewProps {
  onStudent: (student: StudentOut) => void
  onClear?: () => void
}

export default function ProfileView({ onStudent, onClear }: ProfileViewProps) {
  const [mode, setMode] = useState<Mode>('loading')
  const [student, setStudent] = useState<StudentOut | null>(null)
  const [name, setName] = useState('')
  const [yearLevel, setYearLevel] = useState(8)
  const [curriculum, setCurriculum] = useState('QCAA')
  const [focusTextTypes, setFocusTextTypes] = useState<string[]>([])
  const [weeklyGoal, setWeeklyGoal] = useState(4)
  const [coachTone, setCoachTone] = useState('warm')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const stored = loadStudentProfile()
    const id = loadStudentId()
    if (stored) {
      hydrate(stored)
      setMode('saved')
      onStudent(stored)
      return
    }
    if (id) {
      getStudent(id)
        .then((s) => {
          hydrate(s)
          saveStudentProfile(s)
          onStudent(s)
          setMode('saved')
        })
        .catch((err: unknown) => {
          if (err instanceof ApiError && err.status === 404) {
            setMode('empty')
          } else {
            setError(err instanceof Error ? err.message : 'Could not load profile.')
            setMode('empty')
          }
        })
      return
    }
    setMode('empty')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function hydrate(s: StudentOut) {
    setStudent(s)
    setName(s.name)
    setYearLevel(s.year_level)
    setCurriculum(s.curriculum)
    setFocusTextTypes(s.focus_text_types ?? [])
    // Cached profiles from before the weekly goal shipped may lack the field.
    setWeeklyGoal(s.weekly_goal ?? 4)
    setCoachTone(s.coach_tone ?? 'warm')
  }

  function toggleTextType(type: string) {
    setFocusTextTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type],
    )
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const focus = focusTextTypes.length > 0 ? focusTextTypes : undefined
      if (student) {
        const updated = await updateStudent(student.id, {
          name,
          year_level: yearLevel,
          curriculum,
          focus_text_types: focus,
          weekly_goal: weeklyGoal,
          coach_tone: coachTone,
        })
        finishSave(updated)
      } else {
        const created = await createStudent({
          name,
          year_level: yearLevel,
          curriculum,
          focus_text_types: focus,
          weekly_goal: weeklyGoal,
          coach_tone: coachTone,
        })
        finishSave(created)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save profile.')
    } finally {
      setBusy(false)
    }
  }

  function finishSave(s: StudentOut) {
    hydrate(s)
    saveStudentId(s.id)
    saveStudentProfile(s)
    onStudent(s)
    setMode('saved')
  }

  function handleEdit() {
    setMode('edit')
  }

  function handleExport() {
    if (!student) return
    // Local JSON download of everything the tutor holds about this student.
    const a = document.createElement('a')
    a.href = `/api/students/${student.id}/export`
    a.rel = 'noopener'
    document.body.appendChild(a)
    a.click()
    a.remove()
  }

  function handleClear() {
    clearStudentProfile()
    clearStudentId()
    setStudent(null)
    setName('')
    setYearLevel(8)
    setCurriculum('QCAA')
    setFocusTextTypes([])
    setWeeklyGoal(4)
    setCoachTone('warm')
    setMode('empty')
    // Return the app to the first-run wizard so another profile can be
    // selected or created (e.g. a sibling on a shared family device).
    onClear?.()
  }

  if (mode === 'loading') {
    return (
      <div className="profile-shell">
        <p className="muted">Loading your profile…</p>
      </div>
    )
  }

  if (mode === 'saved' && student) {
    return (
      <div className="profile-shell">
        <section className="profile-card">
          <h2 className="profile-title">Your profile</h2>
          <dl className="profile-grid">
            <div>
              <dt>Name</dt>
              <dd>{student.name}</dd>
            </div>
            <div>
              <dt>Year level</dt>
              <dd>{student.year_level}</dd>
            </div>
            <div>
              <dt>Curriculum</dt>
              <dd>{student.curriculum}</dd>
            </div>
            <div>
              <dt>Focus text types</dt>
              <dd>
                {student.focus_text_types.length > 0
                  ? student.focus_text_types.join(', ')
                  : 'All types (no focus set)'}
              </dd>
            </div>
            <div>
              <dt>Weekly goal</dt>
              <dd>{student.weekly_goal ?? 4} sessions / week</dd>
            </div>
            <div>
              <dt>Coach tone</dt>
              <dd>
                {COACH_TONES.find((t) => t.value === (student.coach_tone ?? 'warm'))?.label ??
                  'Warm'}
              </dd>
            </div>
          </dl>
          <div className="profile-actions">
            <button type="button" className="btn primary" onClick={handleEdit}>
              Edit profile
            </button>
            <button type="button" className="btn ghost" onClick={handleExport}>
              Export my data
            </button>
            <button type="button" className="btn ghost" onClick={handleClear}>
              Clear
            </button>
          </div>
          <p className="muted small">
            Export downloads one JSON file with your profile, sessions, writing,
            and progress. Keep it somewhere safe — it's private.
          </p>
        </section>
      </div>
    )
  }

  // edit or empty → form
  return (
    <div className="profile-shell">
      <section className="profile-card">
        <h2 className="profile-title">
          {student ? 'Edit your profile' : 'Set up your profile'}
        </h2>
        <p className="profile-sub">
          Tell your tutor your year level and which text types you're working on.
          Sessions will use this so feedback matches where you are.
        </p>
        {error ? (
          <p className="error-banner" role="alert">
            {error}
          </p>
        ) : null}
        <form onSubmit={handleSubmit} className="profile-form">
          <label className="field-label" htmlFor="profile-name">
            Your name
          </label>
          <input
            id="profile-name"
            className="text-input"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Alex"
            required
            autoFocus
          />

          <label className="field-label" htmlFor="profile-year">
            Year level
          </label>
          <select
            id="profile-year"
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

          <label className="field-label" htmlFor="profile-curriculum">
            Curriculum
          </label>
          <select
            id="profile-curriculum"
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
            Leave empty to practise all text types. Picking one focuses sessions on it.
          </p>

          <label className="field-label" htmlFor="profile-weekly-goal">
            Weekly goal
          </label>
          <select
            id="profile-weekly-goal"
            className="text-input"
            value={weeklyGoal}
            onChange={(e) => setWeeklyGoal(Number(e.target.value))}
          >
            {[2, 3, 4, 5, 6, 7].map((n) => (
              <option key={n} value={n}>
                {n} sessions / week{n === 4 ? ' (recommended)' : ''}
              </option>
            ))}
          </select>
          <p className="muted small">
            A gentle target — missing a day never costs you anything.
          </p>

          <span className="field-label">Coach tone</span>
          <div className="chip-group" role="group" aria-label="Coach tone">
            {COACH_TONES.map((tone) => (
              <button
                key={tone.value}
                type="button"
                className={`chip${coachTone === tone.value ? ' active' : ''}`}
                title={tone.hint}
                onClick={() => setCoachTone(tone.value)}
              >
                {tone.label}
              </button>
            ))}
          </div>
          <p className="muted small">
            How your tutor sounds — never what it teaches. Feedback stays the same either way.
          </p>

          <button type="submit" className="btn primary wide" disabled={busy || !name.trim()}>
            {busy ? 'Saving…' : student ? 'Save changes' : 'Create profile'}
          </button>
        </form>
      </section>
    </div>
  )
}
