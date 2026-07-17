import { useCallback, useState } from 'react'
import './App.css'
import ChatView from './components/ChatView'
import ProgressView from './components/ProgressView'
import { loadStudentId, saveStudentId } from './storage'

type Tab = 'session' | 'progress'

export default function App() {
  const [tab, setTab] = useState<Tab>('session')
  const [studentId, setStudentId] = useState<string | null>(() => loadStudentId())

  const handleStudent = useCallback((id: string) => {
    saveStudentId(id)
    setStudentId(id)
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
        </nav>
      </header>
      <main className="app-main">
        {tab === 'session' ? (
          <ChatView onStudent={handleStudent} />
        ) : (
          <ProgressView studentId={studentId} />
        )}
      </main>
    </div>
  )
}
