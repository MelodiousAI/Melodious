import { motion } from 'framer-motion'
import { Check, Loader2, Music2 } from 'lucide-react'
import type { ProductTranscription } from '../lib/api'
import { TIMELINE_STEPS, activeStepIndex } from '../lib/stages'

interface Props {
  job: ProductTranscription
  previewUrl: string | null
}

export function ProgressView({ job, previewUrl }: Props) {
  const activeIndex = activeStepIndex(job.stage, job.status)
  const pct = Math.round((job.progress || 0) * 100)

  return (
    <motion.div
      className="progress-shell"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
    >
      <div className="progress-card">
        <span className="section-eyebrow">Transcribing</span>
        <h3>{job.stage_label}</h3>
        <div className="file">{job.filename ?? 'Uploaded score'}</div>

        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${Math.max(4, pct)}%` }} />
        </div>
        <div className="progress-pct">
          <span>Live pipeline</span>
          <span>{pct}%</span>
        </div>

        <div className="timeline" style={{ marginTop: 22 }}>
          {TIMELINE_STEPS.map((step, index) => {
            const state = index < activeIndex ? 'done' : index === activeIndex ? 'active' : ''
            return (
              <div className={`tl-step ${state}`} key={step.id}>
                <div className="tl-rail">
                  <div className="tl-dot">
                    {state === 'done' ? (
                      <Check size={14} />
                    ) : state === 'active' ? (
                      <Loader2 size={14} className="spin-ic" />
                    ) : (
                      index + 1
                    )}
                  </div>
                  {index < TIMELINE_STEPS.length - 1 && <div className="tl-line" />}
                </div>
                <div className="tl-body">
                  <div className="tl-title">{step.label}</div>
                  <div className="tl-note">{step.note}</div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      <div className="progress-card" style={{ display: 'flex', flexDirection: 'column' }}>
        <span className="section-eyebrow">Source page</span>
        <div className="live-preview" style={{ marginTop: 14, flex: 1 }}>
          {previewUrl ? (
            <>
              <img src={previewUrl} alt="Uploaded score preview" />
              <div className="scanline" />
            </>
          ) : (
            <div style={{ display: 'grid', placeItems: 'center', gap: 12, color: 'var(--text-dim)' }}>
              <Music2 size={42} />
              <span className="subtle">Processing demo sample…</span>
              <div className="scanline" />
            </div>
          )}
        </div>
        <p className="subtle" style={{ marginTop: 12 }}>
          Running on CPU — a full page typically takes around a minute through the detector, tiled pass,
          and GNN.
        </p>
      </div>
    </motion.div>
  )
}
