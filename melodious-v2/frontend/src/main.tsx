import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

type SampleRecord = {
  sample_id: string
  title: string
  description: string
}

type Artifact = {
  artifact_type: string
  uri: string | null
}

type TranscriptionResponse = {
  job_id: string
  detector_mode: string
  detection_count: number
  relationship_count: number
  assembly_mode: {
    requested_mode: string
    applied_mode: string
    fallback_applied: boolean
    fallback_reason: string | null
  }
  artifacts: Artifact[]
  warnings: string[]
  metric_provenance: Record<string, string>
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const result = String(reader.result)
      resolve(result.includes(',') ? result.split(',')[1] : result)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

function App() {
  const [samples, setSamples] = useState<SampleRecord[]>([])
  const [result, setResult] = useState<TranscriptionResponse | null>(null)
  const [status, setStatus] = useState('Ready')

  useEffect(() => {
    fetch(`${API_BASE}/samples`)
      .then((response) => response.json())
      .then(setSamples)
      .catch(() => setStatus('API unavailable'))
  }, [])

  async function transcribeSample(sampleId: string) {
    setStatus('Transcribing sample')
    const response = await fetch(`${API_BASE}/transcriptions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sample_id: sampleId, requested_assembly_mode: 'auto' }),
    })
    setResult(await response.json())
    setStatus('Complete')
  }

  async function transcribeUpload(file: File) {
    setStatus('Uploading image')
    const image_base64 = await fileToBase64(file)
    const response = await fetch(`${API_BASE}/transcriptions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_base64,
        filename: file.name,
        requested_assembly_mode: 'auto',
      }),
    })
    setResult(await response.json())
    setStatus('Complete')
  }

  return (
    <main className="shell">
      <section className="header">
        <p className="eyebrow">Melodious V2</p>
        <h1>Full-Taxonomy Cloud OMR</h1>
        <p className="lede">
          Upload a score image or run a contract sample. The app shows detector mode,
          assembly fallback status, metric provenance, and export artifacts.
        </p>
      </section>

      <section className="panel panel--upload">
        <h2>Upload</h2>
        <input
          type="file"
          accept="image/*"
          onChange={(event) => {
            const file = event.target.files?.[0]
            if (file) void transcribeUpload(file)
          }}
        />
      </section>

      <section className="panel panel--samples">
        <h2>Samples</h2>
        <div className="samples">
          {samples.map((sample) => (
            <button key={sample.sample_id} onClick={() => void transcribeSample(sample.sample_id)}>
              <strong>{sample.title}</strong>
              <span>{sample.description}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="panel panel--status">
        <h2>Status</h2>
        <p>{status}</p>
        {result && (
          <div className="result">
            <div className="metrics">
              <span>Job {result.job_id}</span>
              <span>Detector {result.detector_mode}</span>
              <span>Detections {result.detection_count}</span>
              <span>Relationships {result.relationship_count}</span>
              <span>Assembly {result.assembly_mode.applied_mode}</span>
            </div>
            {result.warnings.length > 0 && (
              <ul className="warnings">
                {result.warnings.map((warning) => (
                  <li key={warning}>{warning}</li>
                ))}
              </ul>
            )}
            <div className="artifacts">
              {result.artifacts.map((artifact) => (
                <a key={artifact.artifact_type} href={`${API_BASE}${artifact.uri}`}>
                  Download {artifact.artifact_type}
                </a>
              ))}
            </div>
            <pre>{JSON.stringify(result.metric_provenance, null, 2)}</pre>
          </div>
        )}
      </section>
    </main>
  )
}

createRoot(document.getElementById('root')!).render(<App />)
