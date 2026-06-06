import { useCallback, useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { AlertOctagon, RotateCcw, ExternalLink, Info } from 'lucide-react'
import {
  getJob,
  getModels,
  getSamples,
  transcribeImage,
  transcribeSample,
  type ModelsInfo,
  type ProductSample,
  type ProductTranscription,
} from './lib/api'
import { TopBar } from './components/TopBar'
import { UploadHero } from './components/UploadHero'
import { ProgressView } from './components/ProgressView'
import { Workspace } from './components/Workspace'
import { InteractiveBackground } from './components/InteractiveBackground'

const FALLBACK_INSTRUMENTS = ['Piano', 'Electric Piano', 'Organ', 'Guitar', 'Violin', 'Strings', 'Flute', 'Music Box']

export function App() {
  const [dragActive, setDragActive] = useState(false)
  const [models, setModels] = useState<ModelsInfo | null>(null)
  const [samples, setSamples] = useState<ProductSample[]>([])
  const [instrument, setInstrument] = useState('Piano')
  const [job, setJob] = useState<ProductTranscription | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [apiDown, setApiDown] = useState(false)
  const pollRef = useRef<number | null>(null)

  useEffect(() => {
    getModels()
      .then(setModels)
      .catch(() => setApiDown(true))
    getSamples()
      .then(setSamples)
      .catch(() => setApiDown(true))
  }, [])

  const stopPolling = useCallback(() => {
    if (pollRef.current !== null) {
      window.clearInterval(pollRef.current)
      pollRef.current = null
    }
  }, [])

  // Poll the running job until it reaches a terminal state.
  useEffect(() => {
    if (!job || (job.status !== 'queued' && job.status !== 'processing')) {
      stopPolling()
      return
    }
    stopPolling()
    pollRef.current = window.setInterval(async () => {
      try {
        const next = await getJob(job.job_id)
        setJob(next)
      } catch {
        /* transient poll error; keep trying */
      }
    }, 900)
    return stopPolling
  }, [job, stopPolling])

  const busy = !!job && (job.status === 'queued' || job.status === 'processing')

  const startWithFile = useCallback(
    async (file: File) => {
      setError(null)
      if (previewUrl) URL.revokeObjectURL(previewUrl)
      setPreviewUrl(URL.createObjectURL(file))
      try {
        const started = await transcribeImage(file, instrument)
        setJob(started)
      } catch (exc) {
        setError(exc instanceof Error ? exc.message : 'Upload failed.')
        setJob(null)
      }
    },
    [instrument, previewUrl],
  )

  const startWithSample = useCallback(
    async (sampleId: string) => {
      setError(null)
      if (previewUrl) URL.revokeObjectURL(previewUrl)
      setPreviewUrl(null)
      try {
        const started = await transcribeSample(sampleId, instrument)
        setJob(started)
      } catch (exc) {
        setError(exc instanceof Error ? exc.message : 'Could not start sample.')
        setJob(null)
      }
    },
    [instrument, previewUrl],
  )

  const reset = useCallback(() => {
    stopPolling()
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(null)
    setJob(null)
    setError(null)
  }, [previewUrl, stopPolling])

  const instruments = models?.instruments?.length ? models.instruments : FALLBACK_INSTRUMENTS
  const showWorkspace = job?.status === 'complete'
  const showProgress = busy
  const showError = !!error || job?.status === 'failed'

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
      <InteractiveBackground dragActive={dragActive} busy={busy} />
      <TopBar
        availability={models?.availability ?? null}
        onReset={reset}
        showReset={!!job || !!error}
        busy={busy}
      />

      <main className="stage">
        {apiDown && (
          <div className="disclaimer" style={{ marginBottom: 18 }}>
            <Info className="ic" size={15} />
            <span>
              Cannot reach the Melodious API at the configured base URL. Start the backend with{' '}
              <code>python scripts/run_api.py</code>.
            </span>
          </div>
        )}

        <AnimatePresence mode="wait">
          {showError ? (
            <motion.div
              key="error"
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="error-card"
            >
              <AlertOctagon className="ic" size={26} />
              <div>
                <h3>Transcription problem</h3>
                <p>{error ?? job?.error ?? 'The transcription job failed.'}</p>
                <button className="btn btn--primary" onClick={reset}>
                  <RotateCcw size={16} /> Try another image
                </button>
              </div>
            </motion.div>
          ) : showWorkspace && job ? (
            <motion.div key="workspace" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <Workspace
                job={job}
                instrument={instrument}
                instruments={instruments}
                onInstrument={setInstrument}
              />
            </motion.div>
          ) : showProgress && job ? (
            <motion.div key="progress" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <ProgressView job={job} previewUrl={previewUrl} />
            </motion.div>
          ) : (
            <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <UploadHero
                samples={samples}
                instrument={instrument}
                instruments={instruments}
                onInstrument={setInstrument}
                onFile={startWithFile}
                onSample={startWithSample}
                busy={busy}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <footer className="footer">
        <span>Melodious V2 · Optical Music Recognition · demo transcription, not an official metric run.</span>
        <a href="https://github.com/MelodiousAI/Melodious" target="_blank" rel="noreferrer">
          <ExternalLink size={14} style={{ verticalAlign: '-2px', marginRight: 6 }} />
          MelodiousAI/Melodious
        </a>
      </footer>
    </div>
  )
}
