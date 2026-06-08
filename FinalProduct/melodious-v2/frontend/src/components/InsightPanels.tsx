import type { CSSProperties } from 'react'
import { motion } from 'framer-motion'
import {
  Gauge,
  ListChecks,
  Cpu,
  Workflow,
  Layers,
  TriangleAlert,
  Info,
  CircleCheck,
} from 'lucide-react'
import type {
  ModelAvailability,
  ModelProvenance,
  ProductCounts,
  QualitySummary,
} from '../lib/api'
import { CountUp } from './CountUp'

const QUALITY_COLORS: Record<string, string> = {
  high: 'var(--good)',
  review: 'var(--warn)',
  low: 'var(--bad)',
}

export function QualityPanel({ quality }: { quality: QualitySummary }) {
  const pct = Math.round(quality.score * 100)
  const color = QUALITY_COLORS[quality.label] ?? 'var(--warn)'
  return (
    <div className="panel">
      <div className="panel-head">
        <div className="ttl">
          <Gauge className="ic" size={17} /> Confidence
        </div>
        <span className={`q-pill q-${quality.label}`}>{quality.label}</span>
      </div>
      <div className="panel-body">
        <div className="quality">
          <motion.div
            className="quality-ring"
            style={{ '--val': pct, '--col': color } as CSSProperties}
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: 'spring', stiffness: 80, damping: 14 }}
          >
            <span>{pct}</span>
          </motion.div>
          <div className="quality-meta">
            <h4>{quality.headline}</h4>
            <ul className="quality-reasons">
              {quality.reasons.map((reason) => (
                <li key={reason}>
                  <CircleCheck className="ic" size={14} />
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

const COUNT_FIELDS: { key: keyof ProductCounts; label: string }[] = [
  { key: 'staff_systems', label: 'Staff systems' },
  { key: 'notes', label: 'Notes' },
  { key: 'rests', label: 'Rests' },
  { key: 'events', label: 'Events' },
  { key: 'dotted_notes', label: 'Dotted' },
  { key: 'stem_confirmed_notes', label: 'Stem-confirmed' },
  { key: 'slur_starts', label: 'Slurs' },
  { key: 'tie_starts', label: 'Ties' },
  { key: 'relationship_count', label: 'Links' },
]

export function CountsPanel({ counts }: { counts: ProductCounts }) {
  return (
    <div className="panel">
      <div className="panel-head">
        <div className="ttl">
          <ListChecks className="ic" size={17} /> Extraction summary
        </div>
      </div>
      <div className="panel-body">
        <div className="counts-grid">
          {COUNT_FIELDS.map((field) => (
            <div className="count-card" key={field.key}>
              <div className="v">
                <CountUp value={counts[field.key]} />
              </div>
              <div className="k">{field.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function shortPath(value: string | null): string {
  if (!value) return '—'
  const parts = value.replace(/\\/g, '/').split('/')
  return parts.slice(-2).join('/')
}

export function ProvenancePanel({
  provenance,
  availability,
  keyFifths,
  width,
  height,
}: {
  provenance: ModelProvenance
  availability: ModelAvailability
  keyFifths: number
  width: number | null
  height: number | null
}) {
  const stages = [
    { on: availability.full_page_detector, label: 'Symbol detection', icon: <Cpu size={13} /> },
    { on: availability.tiled_detector, label: 'Fine detail pass', icon: <Layers size={13} /> },
    { on: availability.gnn, label: 'Relationship assembly', icon: <Workflow size={13} /> },
  ]
  return (
    <div className="panel">
      <div className="panel-head">
        <div className="ttl">
          <Cpu className="ic" size={17} /> Processing details
        </div>
      </div>
      <div className="panel-body">
        <div className="stage-badges">
          {stages.map((stage) => (
            <span key={stage.label} className={`stage-badge${stage.on ? ' on' : ''}`}>
              {stage.icon}
              {stage.label}
            </span>
          ))}
        </div>
        <div className="kv">
          <div className="kv-row">
            <span className="k">Mode</span>
            <span className="v">{provenance.extractor_mode}</span>
          </div>
          <div className="kv-row">
            <span className="k">Assembly</span>
            <span className="v">{provenance.assembly_mode}</span>
          </div>
          <div className="kv-row">
            <span className="k">Detector</span>
            <span className="v">{shortPath(provenance.detector_checkpoint)}</span>
          </div>
          <div className="kv-row">
            <span className="k">Fine pass</span>
            <span className="v">{shortPath(provenance.thin_symbol_checkpoint)}</span>
          </div>
          <div className="kv-row">
            <span className="k">Assembly model</span>
            <span className="v">{shortPath(provenance.gnn_checkpoint)}</span>
          </div>
          <div className="kv-row">
            <span className="k">Key signature</span>
            <span className="v">{keyFifths} fifths</span>
          </div>
          <div className="kv-row">
            <span className="k">Page size</span>
            <span className="v">{width && height ? `${width}×${height}px` : '—'}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export function ReviewPanel({ warnings }: { warnings: string[] }) {
  return (
    <div className="panel">
      <div className="panel-head">
        <div className="ttl">
          <TriangleAlert className="ic" size={17} /> Review notes
        </div>
        <span className="subtle">{warnings.length} item(s)</span>
      </div>
      <div className="panel-body">
        {warnings.length === 0 ? (
          <div className="empty-note">
            <CircleCheck size={15} style={{ color: 'var(--good)' }} /> No processing warnings for this page.
          </div>
        ) : (
          <div className="warnings">
            {warnings.map((warning, index) => (
              <div className="warning-item" key={index}>
                <TriangleAlert className="ic" size={15} />
                <span>{warning}</span>
              </div>
            ))}
          </div>
        )}
        <div className="disclaimer" style={{ marginTop: 14 }}>
          <Info className="ic" size={15} />
          <span>
            Pitch is estimated from treble-clef staff geometry and rhythm is heuristic. This is a demo transcription,
            not an official accuracy metric.
          </span>
        </div>
      </div>
    </div>
  )
}
