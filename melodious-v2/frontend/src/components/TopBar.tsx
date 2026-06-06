import type { ReactNode } from 'react'
import { Music4, Cpu, Layers, Workflow } from 'lucide-react'
import type { ModelAvailability } from '../lib/api'

interface Props {
  availability: ModelAvailability | null
  onReset: () => void
  showReset: boolean
}

function Badge({ on, label, icon }: { on: boolean; label: string; icon: ReactNode }) {
  return (
    <span className={`model-badge ${on ? 'on' : ''}`} title={on ? `${label}: available` : `${label}: unavailable`}>
      <span className="dot" />
      {icon}
      {label}
    </span>
  )
}

export function TopBar({ availability, onReset, showReset }: Props) {
  return (
    <header className="topbar">
      <div className="brand">
        <div className="brand-mark">
          <Music4 size={22} />
        </div>
        <div className="brand-text">
          <h1>Melodious V2</h1>
          <p>Optical Music Recognition workstation</p>
        </div>
      </div>
      <div className="topbar-actions">
        <div className="badge-row">
          <Badge on={!!availability?.full_page_detector} label="Detector" icon={<Cpu size={13} />} />
          <Badge on={!!availability?.tiled_detector} label="Tiled" icon={<Layers size={13} />} />
          <Badge on={!!availability?.gnn} label="GNN" icon={<Workflow size={13} />} />
        </div>
        {showReset && (
          <button className="btn btn--ghost btn--sm" onClick={onReset}>
            New transcription
          </button>
        )}
      </div>
    </header>
  )
}
