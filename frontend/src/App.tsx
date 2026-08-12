import { useCallback, useState } from 'react'
import './App.css'
import ChatView from './components/ChatView'
import ProfileView from './components/ProfileView'
import ProgressView from './components/ProgressView'
import { loadStudentId, saveStudentId } from './storage'
import type { StudentOut } from './types'

type Tab = 'session' | 'progress' | 'profile'

export default function App() {
  const [tab, setTab] = useState<Tab>('session')
  const [studentId, setStudentId] = useState<string | null>(() => loadStudentId())
  const [student, setStudent] = useState<StudentOut | null>(null)

  const handleStudent = useCallback((s: StudentOut) => {
    saveStudentId(s.id)
    setStudentId(s.id)
    setStudent(s)
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            ✳
          </span>
          <span className="brand-name">English Tutor</span>
        </div>
        <nav className="tabs" role="tablist" aria-label="Views">
          <button
            type="button"
            role="tab"
            aria-selected={tab === 'session'}
            className={tab === 'session' ? 'tab active' : 'tab'}
            onClick={() => setTab('session')}
          >
            Today
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={tab === 'progress'}
            className={tab === 'progress' ? 'tab active' : 'tab'}
            onClick={() => setTab('progress')}
          >
            Progress
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={tab === 'profile'}
            className={tab === 'profile' ? 'tab active' : 'tab'}
            onClick={() => setTab('profile')}
          >
            Profile
          </button>
        </nav>
      </header>
      <main className="app-main">
        {tab === 'session' ? (
          <ChatView student={student} />
        ) : tab === 'progress' ? (
          <ProgressView studentId={studentId} />
        ) : (
          <ProfileView onStudent={handleStudent} />
        )}
      </main>
    </div>
  )
}
