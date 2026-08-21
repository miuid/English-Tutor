import { useEffect, useState } from 'react'
import { ApiError, getParentReport, parentReportPrintUrl } from '../api'
import type { CriterionTrendOut, ParentReportOut } from '../types'

const DIRECTION_LABEL: Record<string, string> = {
  up: '↑ improving',
  down: '↓ dipped',
  steady: '→ steady',
  new: '· first score',
}

function formatDay(iso: string): string {
  return new Date(`${iso}T12:00:00`).toLocaleDateString('en-AU', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  })
}

function formatPoints(trend: CriterionTrendOut): string {
  return trend.points
    .slice(-4)
    .map(
      (p) =>
        `${p.level} (${new Date(`${p.scored_on}T12:00:00`).toLocaleDateString('en-AU', {
          day: 'numeric',
          month: 'short',
        })})`,
    )
    .join(' → ')
}

interface ParentViewProps {
  studentId: string | null
}

// Weekly parent report (ISS-019). D3 privacy boundary: parents see trends,
// levels, time, and goals — never the student's essays or the tutor's
// feedback prose. The printable PDF comes from the same server-side data.
export default function ParentView({ studentId }: ParentViewProps) {
  const [report, setReport] = useState<ParentReportOut | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!studentId) {
      setReport(null)
      return
    }
    let cancelled = false
    getParentReport(studentId)
      .then((out) => {
        if (!cancelled) setReport(out)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 404) {
          setReport(null)
        } else {
          setError(err instanceof Error ? err.message : 'Could not load the report.')
        }
      })
    return () => {
      cancelled = true
    }
  }, [studentId])

  if (error) {
    return (
      <div className="progress-shell">
        <p className="error-banner" role="alert">
          {error}
        </p>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="progress-shell">
        <p className="muted">Loading the weekly report…</p>
      </div>
    )
  }

  const minutes = Math.floor(report.practice_seconds_this_week / 60)

  return (
    <div className="progress-shell">
      <h2 className="progress-title">Weekly parent report</h2>
      <p className="muted">
        {report.student_name} · Year {report.year_level} · {report.curriculum} · Week of{' '}
        {formatDay(report.week_start)} – {formatDay(report.week_end)}
      </p>

      <div className="motivation-strip" aria-label="This week's practice">
        <span className={`weekly-chip${report.goal_met ? ' met' : ''}`}>
          {report.goal_met
            ? `⭐ Weekly goal reached — ${report.sessions_this_week} of ${report.weekly_goal} sessions`
            : `This week: ${report.sessions_this_week} of ${report.weekly_goal} sessions`}
        </span>
        <span className="weekly-chip">{minutes} min practice</span>
        {report.shared_goal ? (
          <span className="weekly-chip">Shared goal: {report.shared_goal}</span>
        ) : null}
      </div>

      {report.highlight ? (
        <div className="levelup-card" role="status" aria-label="This week's highlight">
          <span className="levelup-headline">✨ {report.highlight}</span>
        </div>
      ) : null}

      <div className="chart-card">
        <h3 className="parent-section-title">How the writing is tracking</h3>
        {report.trends.length === 0 ? (
          <p className="muted">
            No graded writing yet — the first session will start the trend lines.
          </p>
        ) : (
          <table className="parent-trends">
            <thead>
              <tr>
                <th>Criterion</th>
                <th>Latest</th>
                <th>Trend</th>
                <th>Recent scores</th>
              </tr>
            </thead>
            <tbody>
              {report.trends.map((trend) => (
                <tr key={trend.criterion_name}>
                  <td>{trend.criterion_name}</td>
                  <td className="parent-level">{trend.latest_level}</td>
                  <td>{DIRECTION_LABEL[trend.direction] ?? trend.direction}</td>
                  <td className="muted">{formatPoints(trend)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="chart-card">
        <h3 className="parent-section-title">Suggested focus for next week</h3>
        <p>{report.next_week_suggestion}</p>
      </div>

      <p className="muted parent-privacy">
        This report shows progress trends only. Essays and detailed tutor feedback stay in the
        student view by design — ask {report.student_name} to walk you through a piece they're
        proud of.
      </p>

      {studentId ? (
        <button
          type="button"
          className="btn ghost"
          onClick={() => window.open(parentReportPrintUrl(studentId), '_blank', 'noopener')}
        >
          Print / save as PDF
        </button>
      ) : null}
    </div>
  )
}
