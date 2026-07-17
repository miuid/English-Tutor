import { useEffect, useMemo, useState } from 'react'
import { ApiError, getProgress } from '../api'
import type { ProgressScoreOut } from '../types'

// Okabe–Ito colorblind-friendly palette.
const SERIES_COLORS = ['#0072B2', '#E69F00', '#009E73', '#D55E00', '#CC79A7', '#56B4E9']

const LEVEL_BASE: Record<string, number> = { A: 5, B: 4, C: 3, D: 2, E: 1 }
const LEVEL_LETTERS = ['A', 'B', 'C', 'D', 'E']

function levelValue(level: string): number {
  const base = LEVEL_BASE[level.trim().toUpperCase().charAt(0)] ?? 0
  if (level.includes('+')) return base + 0.15
  if (level.includes('-') || level.includes('–')) return base - 0.15
  return base
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-AU', { day: 'numeric', month: 'short' })
}

function dayKey(iso: string): string {
  return iso.slice(0, 10)
}

interface SeriesPoint {
  day: string
  value: number
  level: string
  note: string | null
}

interface Series {
  name: string
  color: string
  points: SeriesPoint[]
  latest: string
}

interface ProgressViewProps {
  studentId: string | null
}

export default function ProgressView({ studentId }: ProgressViewProps) {
  const [scores, setScores] = useState<ProgressScoreOut[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!studentId) {
      setScores([])
      return
    }
    let cancelled = false
    getProgress(studentId)
      .then((out) => {
        if (!cancelled) setScores(out.scores)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 404) {
          setScores([])
        } else {
          setError(err instanceof Error ? err.message : 'Could not load progress.')
        }
      })
    return () => {
      cancelled = true
    }
  }, [studentId])

  const { series, days } = useMemo(() => {
    const all = scores ?? []
    const daySet = [...new Set(all.map((s) => dayKey(s.scored_at)))].sort()
    const byCriterion = new Map<string, ProgressScoreOut[]>()
    for (const score of all) {
      const list = byCriterion.get(score.criterion_name) ?? []
      list.push(score)
      byCriterion.set(score.criterion_name, list)
    }
    const built: Series[] = [...byCriterion.entries()].map(([name, rows], i) => {
      const sorted = [...rows].sort((a, b) => a.scored_at.localeCompare(b.scored_at))
      return {
        name,
        color: SERIES_COLORS[i % SERIES_COLORS.length],
        points: sorted.map((row) => ({
          day: dayKey(row.scored_at),
          value: levelValue(row.level),
          level: row.level,
          note: row.note,
        })),
        latest: sorted[sorted.length - 1].level,
      }
    })
    return { series: built, days: daySet }
  }, [scores])

  if (error) {
    return (
      <div className="progress-shell">
        <p className="error-banner" role="alert">
          {error}
        </p>
      </div>
    )
  }

  if (scores === null) {
    return (
      <div className="progress-shell">
        <p className="muted">Loading your progress…</p>
      </div>
    )
  }

  if (series.length === 0) {
    return (
      <div className="progress-shell">
        <div className="empty-state">
          <span className="empty-icon" aria-hidden="true">
            🌱
          </span>
          <h2>No progress yet — and that's okay</h2>
          <p className="muted">Complete a session to see your progress.</p>
        </div>
      </div>
    )
  }

  // Chart geometry.
  const W = 720
  const H = 340
  const PAD = { top: 24, right: 20, bottom: 48, left: 52 }
  const plotW = W - PAD.left - PAD.right
  const plotH = H - PAD.top - PAD.bottom
  const xFor = (day: string) =>
    days.length === 1
      ? PAD.left + plotW / 2
      : PAD.left + (days.indexOf(day) / (days.length - 1)) * plotW
  const yFor = (value: number) => PAD.top + ((5 - value) / 4) * plotH

  return (
    <div className="progress-shell">
      <h2 className="progress-title">How you're tracking</h2>

      <div className="latest-chips" aria-label="Latest level for each criterion">
        {series.map((s) => (
          <span key={s.name} className="latest-chip">
            <span className="chip-dot" style={{ backgroundColor: s.color }} aria-hidden="true" />
            <span className="latest-chip-name">{s.name}</span>
            <span className="latest-chip-level">{s.latest}</span>
          </span>
        ))}
      </div>

      <div className="chart-card">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          role="img"
          aria-label="Line chart of rubric levels over time, one line per criterion"
          className="progress-chart"
        >
          {/* Y gridlines + letter labels (A at top, E at bottom) */}
          {LEVEL_LETTERS.map((letter) => {
            const y = yFor(LEVEL_BASE[letter])
            return (
              <g key={letter}>
                <line x1={PAD.left} x2={W - PAD.right} y1={y} y2={y} className="grid-line" />
                <text x={PAD.left - 12} y={y + 4} textAnchor="end" className="axis-label">
                  {letter}
                </text>
              </g>
            )
          })}

          {/* X date labels */}
          {days.map((day) => (
            <text
              key={day}
              x={xFor(day)}
              y={H - PAD.bottom + 22}
              textAnchor="middle"
              className="axis-label"
            >
              {formatDate(day)}
            </text>
          ))}

          {/* One series per criterion */}
          {series.map((s) => (
            <g key={s.name}>
              {s.points.length > 1 ? (
                <polyline
                  fill="none"
                  stroke={s.color}
                  strokeWidth={2.5}
                  strokeLinejoin="round"
                  strokeLinecap="round"
                  points={s.points.map((p) => `${xFor(p.day)},${yFor(p.value)}`).join(' ')}
                />
              ) : null}
              {s.points.map((p, i) => (
                <circle
                  key={`${p.day}-${i}`}
                  cx={xFor(p.day)}
                  cy={yFor(p.value)}
                  r={5}
                  fill={s.color}
                  stroke="#fff"
                  strokeWidth={1.5}
                >
                  <title>
                    {`${s.name}: ${p.level} — ${formatDate(p.day)}${p.note ? `\n${p.note}` : ''}`}
                  </title>
                </circle>
              ))}
            </g>
          ))}
        </svg>

        <ul className="chart-legend">
          {series.map((s) => (
            <li key={s.name}>
              <span className="chip-dot" style={{ backgroundColor: s.color }} aria-hidden="true" />
              {s.name}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
