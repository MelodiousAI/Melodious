import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

interface NoteData {
  id: number
  x: number
  y: number
  size: number
  opacity: number
  speedX: number
  speedY: number
  rotation: number
}

export function PaperBackground({ busy }: { busy?: boolean }) {
  const [notes, setNotes] = useState<NoteData[]>([])

  useEffect(() => {
    setNotes(
      Array.from({ length: 8 }).map((_, idx) => ({
        id: idx,
        x: Math.random() * 100,
        y: 10 + Math.random() * 80,
        size: 0.5 + Math.random() * 0.6,
        opacity: 0.06 + Math.random() * 0.08,
        speedX: (0.008 + Math.random() * 0.02) * (Math.random() > 0.5 ? 1 : -1),
        speedY: (0.005 + Math.random() * 0.015) * (Math.random() > 0.5 ? 1 : -1),
        rotation: -15 + Math.random() * 30,
      })),
    )
  }, [])

  useEffect(() => {
    let animationId: number
    const tick = () => {
      setNotes((prev) =>
        prev.map((note) => {
          let nextX = note.x + note.speedX * (busy ? 1.8 : 1)
          let nextY = note.y + note.speedY * (busy ? 1.8 : 1)
          if (nextX < -5) nextX = 105
          if (nextX > 105) nextX = -5
          if (nextY < -5) nextY = 105
          if (nextY > 105) nextY = -5
          return { ...note, x: nextX, y: nextY }
        }),
      )
      animationId = requestAnimationFrame(tick)
    }
    animationId = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(animationId)
  }, [busy])

  return (
    <div className="paper-background" aria-hidden>
      <div className="paper-grain" />
      {[18, 42, 68].map((top) => (
        <div key={top} className="bg-staff-row" style={{ top: `${top}%` }}>
          {[0, 1, 2, 3, 4].map((i) => (
            <div key={i} className="line" />
          ))}
        </div>
      ))}
      {notes.map((note) => (
        <motion.div
          key={note.id}
          className="floating-note-bg"
          style={{
            left: `${note.x}%`,
            top: `${note.y}%`,
            transform: `rotate(${note.rotation}deg) scale(${note.size})`,
            opacity: note.opacity,
          }}
        >
          <svg viewBox="0 0 24 40" width="24" height="40" fill="currentColor">
            <ellipse cx="8" cy="32" rx="7" ry="5" transform="rotate(-20 8 32)" />
            <line x1="14" y1="32" x2="14" y2="4" stroke="currentColor" strokeWidth="2.5" />
          </svg>
        </motion.div>
      ))}
    </div>
  )
}
