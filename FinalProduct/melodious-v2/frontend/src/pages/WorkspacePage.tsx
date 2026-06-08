import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { AlertOctagon, RotateCcw, Info } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTranscription } from '../lib/transcription-context'
import { ProgressView } from '../components/ProgressView'
import { Workspace } from '../components/Workspace'

export function WorkspacePage() {
  const { job, previewUrl, error, apiDown, rehydrating, busy, instrument, instruments, setInstrument, reset } =
    useTranscription()
  const navigate = useNavigate()

  const showWorkspace = job?.status === 'complete'
  const showProgress = busy
  const showError = !!error || job?.status === 'failed'

  useEffect(() => {
    if (rehydrating) return
    if (!job && !error && !busy) {
      navigate('/')
    }
  }, [job, error, busy, rehydrating, navigate])

  if (rehydrating) {
    return <div className="subtle page-enter">Loading your session…</div>
  }

  if (!job && !error) {
    return null
  }

  return (
    <div className="page-enter">
      {apiDown && (
        <div className="disclaimer" style={{ marginBottom: 18 }}>
          <Info className="ic" size={15} />
          <span>
            Cannot reach the Melodious API. Start the backend with <code>python scripts/run_api.py</code>.
          </span>
        </div>
      )}

      {showError ? (
        <motion.div
          className="error-card"
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <AlertOctagon className="ic" size={26} />
          <div>
            <h3>Something went wrong</h3>
            <p>{error ?? job?.error ?? 'The transcription could not be completed.'}</p>
            <button
              className="btn btn--primary"
              onClick={() => {
                reset()
                navigate('/')
              }}
            >
              <RotateCcw size={16} /> Start over
            </button>
          </div>
        </motion.div>
      ) : showWorkspace && job ? (
        <Workspace job={job} instrument={instrument} instruments={instruments} onInstrument={setInstrument} />
      ) : showProgress && job ? (
        <ProgressView job={job} previewUrl={previewUrl} />
      ) : null}
    </div>
  )
}
