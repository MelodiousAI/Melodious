import { useState } from 'react'
import { motion } from 'framer-motion'
import { Music, Play, FileCheck2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTranscription } from '../lib/transcription-context'

export function LibraryPage() {
  const { samples, busy, startWithSample } = useTranscription()
  const navigate = useNavigate()
  const [starting, setStarting] = useState<string | null>(null)

  async function handleSample(sampleId: string) {
    if (busy || starting) return
    setStarting(sampleId)
    try {
      await startWithSample(sampleId)
      navigate('/workspace')
    } catch {
      setStarting(null)
    }
  }

  return (
    <div className="page-enter library-page">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <h1>Score library</h1>
        <p className="lead">Curated samples to try Melodious — pick one and we&apos;ll transcribe it for you.</p>
      </motion.div>

      <div className="sample-grid">
        {samples.map((sample, idx) => (
          <motion.button
            key={sample.sample_id}
            className="sample-card"
            disabled={busy || !sample.available || starting !== null}
            onClick={() => handleSample(sample.sample_id)}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.06 }}
            whileHover={sample.available ? { y: -3 } : {}}
          >
            <div className="s-top">
              <span className="s-ic">
                {sample.available ? <Music size={16} /> : <FileCheck2 size={16} />}
              </span>
              <div>
                <strong>{sample.title}</strong>
                <div className="s-sub">{sample.subtitle}</div>
              </div>
              <span className="spacer" />
              {sample.available && (
                <span className="play-pill">
                  <Play size={11} />
                </span>
              )}
            </div>
            <div className="s-desc">{sample.description}</div>
          </motion.button>
        ))}
      </div>
    </div>
  )
}
