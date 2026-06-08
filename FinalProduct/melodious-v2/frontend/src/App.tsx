import { BrowserRouter, Route, Routes, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { TranscriptionProvider, useTranscription } from './lib/transcription-context'
import { Navbar } from './components/Navbar'
import { Footer } from './components/Footer'
import { PaperBackground } from './components/PaperBackground'
import { HomePage } from './pages/HomePage'
import { LibraryPage } from './pages/LibraryPage'
import { UploadPage } from './pages/UploadPage'
import { WorkspacePage } from './pages/WorkspacePage'

function AppShell() {
  const location = useLocation()
  const { dragActive, setDragActive, busy } = useTranscription()

  return (
    <div
      className="app"
      onDragOver={(e) => {
        e.preventDefault()
        setDragActive(true)
      }}
      onDragLeave={() => setDragActive(false)}
      onDrop={() => setDragActive(false)}
    >
      <PaperBackground busy={busy || dragActive} />
      <Navbar />
      <main className="stage">
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={<HomePage />} />
            <Route path="/library" element={<LibraryPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/workspace" element={<WorkspacePage />} />
          </Routes>
        </AnimatePresence>
      </main>
      <Footer />
    </div>
  )
}

export function App() {
  return (
    <BrowserRouter>
      <TranscriptionProvider>
        <AppShell />
      </TranscriptionProvider>
    </BrowserRouter>
  )
}
