import { motion } from 'framer-motion'
import { Music4, Cpu, Layers, Workflow, RefreshCw, Radio } from 'lucide-react'
import type { ModelAvailability } from '../lib/api'

interface Props {
  availability: ModelAvailability | null
  onReset: () => void
  showReset: boolean
  busy?: boolean
}

function TelemetryBadge({ on, label, icon }: { on: boolean; label: string; icon: React.ReactNode }) {
  return (
    <motion.div
      className={`telemetry-badge ${on ? 'online' : 'offline'}`}
      title={on ? `${label} Engine is online and ready` : `${label} Engine is initializing/offline`}
      whileHover={{ scale: 1.03, borderColor: on ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)' }}
      transition={{ type: 'spring', stiffness: 400, damping: 15 }}
    >
      <div className="status-indicator">
        <span className="glow-ring" />
        <span className="core-dot" />
      </div>
      <span className="telemetry-icon">{icon}</span>
      <span className="telemetry-label">
        {label} <span className="telemetry-status-text">{on ? 'ONLINE' : 'STDBY'}</span>
      </span>
    </motion.div>
  )
}

export function TopBar({ availability, onReset, showReset, busy = false }: Props) {
  return (
    <header className="topbar">
      <div className="brand">
        {/* Animated Brand Mark */}
        <motion.div
          className="brand-mark"
          animate={busy ? {
            rotate: [0, 5, -5, 0],
            scale: [1, 1.05, 0.98, 1],
            boxShadow: [
              '0 0 15px rgba(204, 164, 59, 0.4)',
              '0 0 25px rgba(204, 164, 59, 0.7)',
              '0 0 15px rgba(204, 164, 59, 0.4)',
            ]
          } : {}}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
          whileHover={{ scale: 1.08, rotate: 5 }}
        >
          <Music4 size={20} className="brand-logo-icon" />
        </motion.div>

        <div className="brand-text">
          <div className="brand-title-row">
            <h1 className="brand-name">Melodious</h1>
            <span className="brand-version">V2 OMR Workstation</span>
          </div>
          <p className="brand-subtitle">Optical Music Recognition neural transcriber</p>
        </div>
      </div>

      <div className="topbar-actions">
        {/* Hardware Rack-Style Telemetry Indicator Panel */}
        <div className="badge-row telemetry-panel">
          <div className="telemetry-panel-header">
            <Radio size={10} className="telemetry-header-icon" />
            <span>Telemetry</span>
          </div>
          <div className="telemetry-badges">
            <TelemetryBadge on={!!availability?.full_page_detector} label="DETECTOR" icon={<Cpu size={11} />} />
            <TelemetryBadge on={!!availability?.tiled_detector} label="TILED_STEM" icon={<Layers size={11} />} />
            <TelemetryBadge on={!!availability?.gnn} label="GNN_REL" icon={<Workflow size={11} />} />
          </div>
        </div>

        {showReset && (
          <motion.button
            className="btn btn--ghost btn--sm btn-reset"
            onClick={onReset}
            whileHover={{ scale: 1.04, y: -1 }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          >
            <RefreshCw size={12} className="reset-icon" />
            New Session
          </motion.button>
        )}
      </div>
    </header>
  )
}
