import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

export type Vibe = 'Default' | 'Synthwave' | 'Classical' | 'Lofi'

interface Props {
  vibe: Vibe
  busy: boolean
}

const VIBE_COLORS = {
  Default: ['rgba(124, 92, 255, 0.4)', 'rgba(34, 211, 238, 0.3)', 'rgba(244, 114, 182, 0.3)'],
  Synthwave: ['rgba(255, 0, 128, 0.5)', 'rgba(0, 255, 255, 0.4)', 'rgba(128, 0, 255, 0.4)'],
  Classical: ['rgba(255, 215, 0, 0.3)', 'rgba(0, 50, 150, 0.4)', 'rgba(255, 255, 255, 0.1)'],
  Lofi: ['rgba(255, 150, 100, 0.4)', 'rgba(200, 100, 200, 0.3)', 'rgba(255, 200, 150, 0.4)'],
}

export function AmbientBackground({ vibe, busy }: Props) {
  const colors = VIBE_COLORS[vibe] || VIBE_COLORS.Default
  const duration = busy ? 4 : 12

  return (
    <div className="ambient-background">
      <motion.div
        className="ambient-orb orb-1"
        animate={{
          background: colors[0],
          x: [0, 100, -50, 0],
          y: [0, -50, 100, 0],
          scale: busy ? [1, 1.2, 1] : [1, 1.05, 1],
        }}
        transition={{ duration: duration * 1.5, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="ambient-orb orb-2"
        animate={{
          background: colors[1],
          x: [0, -100, 50, 0],
          y: [0, 100, -50, 0],
          scale: busy ? [1, 1.3, 1] : [1, 1.1, 1],
        }}
        transition={{ duration: duration * 1.2, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="ambient-orb orb-3"
        animate={{
          background: colors[2],
          x: [0, 50, -100, 0],
          y: [0, -100, 50, 0],
          scale: busy ? [1, 1.25, 1] : [1, 1.08, 1],
        }}
        transition={{ duration: duration * 1.8, repeat: Infinity, ease: 'easeInOut' }}
      />
      <div className="ambient-overlay" />
    </div>
  )
}
