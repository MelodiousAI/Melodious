import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import {
  getJob,
  getModels,
  getSamples,
  transcribeImage,
  transcribeSample,
  type ModelsInfo,
  type ProductSample,
  type ProductTranscription,
} from './api'

const JOB_STORAGE_KEY = 'melodious_v2_job_id'

const FALLBACK_INSTRUMENTS = [
  'Piano',
  'Electric Piano',
  'Organ',
  'Guitar',
  'Violin',
  'Strings',
  'Flute',
  'Music Box',
]

interface TranscriptionContextValue {
  dragActive: boolean
  setDragActive: (value: boolean) => void
  models: ModelsInfo | null
  samples: ProductSample[]
  instrument: string
  setInstrument: (value: string) => void
  instruments: string[]
  job: ProductTranscription | null
  previewUrl: string | null
  error: string | null
  apiDown: boolean
  rehydrating: boolean
  busy: boolean
  startWithFile: (file: File) => Promise<void>
  startWithSample: (sampleId: string) => Promise<void>
  reset: () => void
}

const TranscriptionContext = createContext<TranscriptionContextValue | null>(null)

export function TranscriptionProvider({ children }: { children: ReactNode }) {
  const [dragActive, setDragActive] = useState(false)
  const [models, setModels] = useState<ModelsInfo | null>(null)
  const [samples, setSamples] = useState<ProductSample[]>([])
  const [instrument, setInstrument] = useState('Piano')
  const [job, setJob] = useState<ProductTranscription | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [apiDown, setApiDown] = useState(false)
  const [rehydrating, setRehydrating] = useState(() => !!sessionStorage.getItem(JOB_STORAGE_KEY))
  const pollRef = useRef<number | null>(null)

  useEffect(() => {
    getModels()
      .then(setModels)
      .catch(() => setApiDown(true))
    getSamples()
      .then(setSamples)
      .catch(() => setApiDown(true))

    const savedJobId = sessionStorage.getItem(JOB_STORAGE_KEY)
    if (savedJobId) {
      getJob(savedJobId)
        .then((restored) => {
          if (restored.status === 'complete' || restored.status === 'failed') {
            setJob(restored)
          } else if (restored.status === 'queued' || restored.status === 'processing') {
            setJob(restored)
          } else {
            sessionStorage.removeItem(JOB_STORAGE_KEY)
          }
        })
        .catch(() => sessionStorage.removeItem(JOB_STORAGE_KEY))
        .finally(() => setRehydrating(false))
    } else {
      setRehydrating(false)
    }
  }, [])

  useEffect(() => {
    if (job?.job_id) {
      sessionStorage.setItem(JOB_STORAGE_KEY, job.job_id)
    }
  }, [job?.job_id])

  const stopPolling = useCallback(() => {
    if (pollRef.current !== null) {
      window.clearInterval(pollRef.current)
      pollRef.current = null
    }
  }, [])

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
        /* keep polling */
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
        throw exc
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
        throw exc
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
    sessionStorage.removeItem(JOB_STORAGE_KEY)
  }, [previewUrl, stopPolling])

  const instruments = models?.instruments?.length ? models.instruments : FALLBACK_INSTRUMENTS

  return (
    <TranscriptionContext.Provider
      value={{
        dragActive,
        setDragActive,
        models,
        samples,
        instrument,
        setInstrument,
        instruments,
        job,
        previewUrl,
        error,
        apiDown,
        rehydrating,
        busy,
        startWithFile,
        startWithSample,
        reset,
      }}
    >
      {children}
    </TranscriptionContext.Provider>
  )
}

export function useTranscription() {
  const ctx = useContext(TranscriptionContext)
  if (!ctx) throw new Error('useTranscription must be used within TranscriptionProvider')
  return ctx
}
