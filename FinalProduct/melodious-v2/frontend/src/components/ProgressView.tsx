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
        <div className="file">{job.filename ?? 'Your score'}</div>

        <div className="progress-bar">
          <motion.div
            className="progress-fill"
            initial={{ width: '4%' }}
            animate={{ width: `${Math.max(4, pct)}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          />
        </div>
        <div className="progress-pct">
          <span>Reading your score</span>
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

      <div className="progress-card">
        <span className="section-eyebrow">Your page</span>
        <div className="live-preview" style={{ marginTop: 14, minHeight: 280 }}>
          {previewUrl ? (
            <>
              <img src={previewUrl} alt="Uploaded score preview" />
              <div className="reading-shimmer" />
            </>
          ) : (
            <div style={{ display: 'grid', placeItems: 'center', gap: 12, color: 'var(--text-dim)', padding: 40 }}>
              <Music2 size={42} />
              <span className="subtle">Processing sample score…</span>
            </div>
          )}
        </div>
        <p className="subtle" style={{ marginTop: 16, lineHeight: 1.55 }}>
          This usually takes about a minute. We&apos;re reading the notation, connecting the symbols, and preparing
          your downloadable score.
        </p>
      </div>
    </motion.div>
  )
}
