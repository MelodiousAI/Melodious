import { useEffect, useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { Check, Loader2, Music2, Terminal } from 'lucide-react'
import type { ProductTranscription } from '../lib/api'
import { TIMELINE_STEPS, activeStepIndex } from '../lib/stages'

interface Props {
  job: ProductTranscription
  previewUrl: string | null
}

const STAGE_ORDER = [
  'queued',
  'uploading',
  'reading_image',
  'detecting_staff',
  'detecting_symbols',
  'detecting_thin_symbols',
  'building_graph',
  'assembling_events',
  'exporting',
  'complete',
]

const STAGE_LOGS: Record<string, { prefix: string; message: string }[]> = {
  queued: [
    { prefix: 'SYS', message: 'Connecting to Melodious OMR high-performance backend...' },
    { prefix: 'SYS', message: 'Handshake successful. Establishing secure WebSocket channel...' }
  ],
  uploading: [
    { prefix: 'SYS', message: 'Transferring raw page pixels to API server...' },
    { prefix: 'SYS', message: 'Upload stream buffer initialized. Progress: buffering...' }
  ],
  reading_image: [
    { prefix: 'IMG', message: 'Server-side buffer received. Initializing pixel tensor decoding...' },
    { prefix: 'IMG', message: 'Extracting resolution, EXIF tags, and image metrics...' }
  ],
  detecting_staff: [
    { prefix: 'STAFF', message: 'Executing horizontal projection filter sweep...' },
    { prefix: 'STAFF', message: 'Isolating staff systems, bounding coordinates, and key signature offsets...' },
    { prefix: 'STAFF', message: 'Staff detection complete. Located active musical systems.' }
  ],
  detecting_symbols: [
    { prefix: 'YOLO', message: 'Loading YOLOv8m custom full-page OMR weights (best.pt)...' },
    { prefix: 'YOLO', message: 'Running inference feedforward pass on full taxonomy (clefs, noteheads, rests)...' },
    { prefix: 'YOLO', message: 'Inference successful. Registered raw symbols and confidence thresholds.' }
  ],
  detecting_thin_symbols: [
    { prefix: 'TILED', message: 'Generating overlapping high-res patch grid (step=64px)...' },
    { prefix: 'TILED', message: 'Executing high-res tiled secondary pass for thin primitives (stems, beams, flags)...' },
    { prefix: 'TILED', message: 'Filtering duplicate candidate bounding boxes. Resolving multi-channel detections...' }
  ],
  building_graph: [
    { prefix: 'GNN', message: 'Structuring heterogeneous note-stave relational graph representation...' },
    { prefix: 'GNN', message: 'Mapping GNN node features (spatial positions, category indexes)...' },
    { prefix: 'GNN', message: 'Invoking PyTorch Geometric GNN assembler engine (v2_gnn_model.pth)...' },
    { prefix: 'GNN', message: 'Graph relationship matrices resolved. Connected stems, beams, and noteheads.' }
  ],
  assembling_events: [
    { prefix: 'OMR', message: 'Merging graphical symbols and structural links into abstract syntax trees...' },
    { prefix: 'OMR', message: 'Running pitch-stave geometry alignment heuristics (Treble Clef base reference)...' },
    { prefix: 'OMR', message: 'Assembling rhythmic structures, calculating quarter lengths, dotted-note modifiers...' }
  ],
  exporting: [
    { prefix: 'EXPORT', message: 'Mapping internal event structures onto standard MusicXML v4.0.3 syntax...' },
    { prefix: 'EXPORT', message: 'Writing MIDI tracks, injecting instrument bank and target BPM tempo events...' },
    { prefix: 'EXPORT', message: 'Compiling project download bundles and artifact JSON files...' }
  ],
  complete: [
    { prefix: 'SYS', message: 'OMR V2 pipeline finished successfully. Serving generated artifacts.' }
  ]
}

interface LogItem {
  timestamp: string
  prefix: string
  message: string
}

export function ProgressView({ job, previewUrl }: Props) {
  const activeIndex = activeStepIndex(job.stage, job.status)
  const pct = Math.round((job.progress || 0) * 100)
  const [logs, setLogs] = useState<LogItem[]>([])
  const terminalEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const activeIdx = STAGE_ORDER.indexOf(job.stage)
    const currentStages = STAGE_ORDER.slice(0, activeIdx + 1)
    
    const newLogs: LogItem[] = []
    const now = new Date()
    let runningTime = now.getTime() - 25000 // simulate starting 25s ago
    
    currentStages.forEach((stage, sIdx) => {
      const stageItems = STAGE_LOGS[stage] || []
      stageItems.forEach((item, itemIdx) => {
        const simulatedTime = new Date(runningTime + sIdx * 2500 + itemIdx * 600)
        const timestampStr = simulatedTime.toTimeString().split(' ')[0] + '.' + String(simulatedTime.getMilliseconds()).padStart(3, '0')
        newLogs.push({
          timestamp: timestampStr,
          prefix: item.prefix,
          message: item.message
        })
      })
    })
    
    setLogs(newLogs)
  }, [job.stage])

  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs])

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
        <span className="section-eyebrow">Source page &amp; CLI console</span>
        <div className="live-preview" style={{ marginTop: 14, flex: 1, minHeight: 200, maxHeight: 300 }}>
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

        <div className="terminal-console">
          <div className="terminal-header">
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Terminal size={12} style={{ color: 'var(--accent-2)' }} />
              OMR Pipeline Terminal Log
            </span>
            <div className="terminal-dots">
              <div className="terminal-dot red" />
              <div className="terminal-dot yellow" />
              <div className="terminal-dot green" />
            </div>
          </div>
          {logs.map((log, index) => (
            <div className="terminal-row" key={index}>
              <span className="terminal-time">[{log.timestamp}]</span>
              <span className={`terminal-prefix prefix-${log.prefix}`}>[{log.prefix}]</span>
              <span className="terminal-msg">{log.message}</span>
            </div>
          ))}
          <div ref={terminalEndRef} />
        </div>

        <p className="subtle" style={{ marginTop: 12 }}>
          Running on CPU — a full page typically takes around a minute through the detector, tiled pass,
          and GNN.
        </p>
      </div>
    </motion.div>
  )
}
