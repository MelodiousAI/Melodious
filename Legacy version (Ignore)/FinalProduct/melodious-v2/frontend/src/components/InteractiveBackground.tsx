import { useEffect, useState, useRef } from 'react'
import { motion, useMotionValue, useSpring } from 'framer-motion'

interface NoteData {
  id: number
  x: number // percentage
  y: number // percentage
  type: 'quarter' | 'half' | 'eighth-beamed' | 'clef'
  scale: number
  opacity: number
  speedX: number
  speedY: number
  rotation: number
}

export function InteractiveBackground({ dragActive, busy }: { dragActive: boolean; busy: boolean }) {
  const [notes, setNotes] = useState<NoteData[]>([])
  const containerRef = useRef<HTMLDivElement>(null)

  // Mouse tracking for parallax
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)

  // Smooth springs for mouse movement
  const springX = useSpring(mouseX, { stiffness: 50, damping: 20 })
  const springY = useSpring(mouseY, { stiffness: 50, damping: 20 })

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const { clientX, clientY } = e
      const width = window.innerWidth
      const height = window.innerHeight
      // Map to range -50 to 50
      mouseX.set(((clientX / width) - 0.5) * 60)
      mouseY.set(((clientY / height) - 0.5) * 60)
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [mouseX, mouseY])

  // Initialize beautiful drifting notes
  useEffect(() => {
    const initialNotes: NoteData[] = Array.from({ length: 15 }).map((_, idx) => ({
      id: idx,
      x: Math.random() * 100,
      y: 20 + Math.random() * 60,
      type: idx % 4 === 0 ? 'clef' : idx % 4 === 1 ? 'half' : idx % 4 === 2 ? 'quarter' : 'eighth-beamed',
      scale: 0.6 + Math.random() * 0.8,
      opacity: 0.1 + Math.random() * 0.15,
      speedX: (0.02 + Math.random() * 0.05) * (Math.random() > 0.5 ? 1 : -1),
      speedY: (0.01 + Math.random() * 0.03) * (Math.random() > 0.5 ? 1 : -1),
      rotation: Math.random() * 360,
    }))
    setNotes(initialNotes)
  }, [])

  // Animation frame loop for floating drift
  useEffect(() => {
    let animationId: number

    const updateDrift = () => {
      setNotes((prevNotes) =>
        prevNotes.map((note) => {
          let nextX = note.x + note.speedX * (busy ? 2.5 : 1)
          let nextY = note.y + note.speedY * (busy ? 2.5 : 1)

          // Drag effect: notes slowly gravitate toward center if user is dragging a file
          if (dragActive) {
            const dx = 50 - note.x
            const dy = 50 - note.y
            nextX += dx * 0.015
            nextY += dy * 0.015
          }

          // Boundary wrapping
          if (nextX < -10) nextX = 110
          if (nextX > 110) nextX = -10
          if (nextY < -10) nextY = 110
          if (nextY > 110) nextY = -10

          return {
            ...note,
            x: nextX,
            y: nextY,
            rotation: note.rotation + 0.05 * (busy ? 3 : 1),
          }
        })
      )
      animationId = requestAnimationFrame(updateDrift)
    }

    animationId = requestAnimationFrame(updateDrift)
    return () => cancelAnimationFrame(animationId)
  }, [dragActive, busy])

  // Custom inline SVG paths for music elements
  const renderMusicSvg = (type: string) => {
    switch (type) {
      case 'clef':
        return (
          // Beautiful high-fidelity G Clef (Treble Clef) SVG
          <svg viewBox="0 0 32 80" fill="currentColor" className="w-8 h-20">
            <path d="M18.2,59.3c-1.3-0.5-2.6-1.5-3.4-2.8c-0.8-1.3-1.1-2.9-0.8-4.5c0.4-2.1,1.9-3.9,4-4.8c1.6-0.7,3.5-0.7,5.1-0.1 c2.2,0.8,3.7,2.8,3.9,5.2c0.2,2.8-1.1,5.3-3.6,6.6C21.7,59.7,19.9,59.8,18.2,59.3 M17,46.1c-3.1,1.5-5.1,4.5-5,7.9 c0.1,4.1,2.7,7.7,6.6,9c1.9,0.6,4.1,0.5,5.9-0.3c3.8-1.7,5.9-5.7,5.2-9.8c-0.6-3.7-3.4-6.6-7-7.4c-1.5-0.3-3-0.2-4.4,0.3L20.8,12 c1-0.1,2,0.1,3,0.5c1.9,0.8,3.2,2.6,3.4,4.7c0.1,1.4-0.4,2.8-1.4,3.8c-0.9,1-2.3,1.4-3.6,1c-1.2-0.4-2.1-1.4-2.3-2.6 c-0.2-1.3,0.3-2.5,1.3-3.3c0.7-0.6,1.7-0.8,2.6-0.6c0.3,0.1,0.6,0,0.7-0.3c0.1-0.3,0-0.6-0.3-0.7c-1.4-0.3-2.9,0.1-3.9,1.1 c-1.3,1.2-1.9,3.1-1.6,4.9c0.4,2,2,3.5,4,3.9c2.1,0.5,4.3-0.3,5.5-2.1c1.3-1.8,1.6-4.2,0.8-6.3c-0.8-2.3-2.7-4-5-4.6 c-1.7-0.4-3.4-0.1-4.9,0.7c-0.7,0.4-1,1.2-1.1,2L16,48.2 M15.2,64.2c-0.2,0-0.4,0.1-0.5,0.3c-1.4,2-1.8,4.5-1.1,6.8 c0.7,2.5,2.7,4.3,5.2,4.7c3,0.5,6-1.1,7.1-3.9c0.8-2,0.4-4.4-1.1-5.9c-1.3-1.3-3.2-1.8-5-1.4L18,66 M15,75.1c-1.2,0-2.4-0.4-3.4-1.2 c-1.8-1.5-2.5-4-1.8-6.3c0.6-2,2-3.7,3.9-4.5c0.3-0.1,0.6,0.1,0.7,0.4c0.1,0.3-0.1,0.6-0.4,0.7c-1.6,0.7-2.7,2.1-3.2,3.8 c-0.6,1.9,0,3.9,1.4,5.2c1.3,1.2,3.2,1.6,4.9,1l0.6,2C17.1,75,16,75.1,15,75.1z" />
          </svg>
        );
      case 'half':
        return (
          // Beautiful Half Note SVG
          <svg viewBox="0 0 24 40" fill="currentColor" className="w-6 h-10">
            <ellipse cx="8" cy="32" rx="7" ry="5" transform="rotate(-20 8 32)" stroke="currentColor" strokeWidth="2" fill="none" />
            <line x1="14" y1="31" x2="14" y2="4" stroke="currentColor" strokeWidth="2.5" />
          </svg>
        );
      case 'quarter':
        return (
          // Beautiful Quarter Note SVG
          <svg viewBox="0 0 24 40" fill="currentColor" className="w-6 h-10">
            <ellipse cx="8" cy="32" rx="7" ry="5" transform="rotate(-20 8 32)" />
            <line x1="14" y1="32" x2="14" y2="4" stroke="currentColor" strokeWidth="2.5" />
          </svg>
        );
      case 'eighth-beamed':
        return (
          // Beautiful Pair of Beamed 8th Notes SVG
          <svg viewBox="0 0 44 40" fill="currentColor" className="w-12 h-10">
            <ellipse cx="8" cy="32" rx="6" ry="4" transform="rotate(-20 8 32)" />
            <line x1="13" y1="32" x2="13" y2="4" stroke="currentColor" strokeWidth="2" />
            <ellipse cx="32" cy="28" rx="6" ry="4" transform="rotate(-20 32 28)" />
            <line x1="37" y1="28" x2="37" y2="0" stroke="currentColor" strokeWidth="2" />
            {/* Beamed bar */}
            <polygon points="13,4 37,0 37,5 13,9" />
          </svg>
        );
      default:
        return null;
    }
  }

  return (
    <div className="interactive-background" ref={containerRef}>
      {/* Dynamic atmospheric ambient glowing light orbs */}
      <motion.div
        className="ambient-light-glow light-1"
        style={{
          x: springX,
          y: springY,
        }}
        animate={{
          scale: dragActive ? 1.25 : busy ? 1.15 : 1.0,
          opacity: dragActive ? 0.35 : busy ? 0.25 : 0.18,
        }}
        transition={{ type: 'spring', stiffness: 30, damping: 15 }}
      />
      <motion.div
        className="ambient-light-glow light-2"
        style={{
          x: useSpring(mouseX, { stiffness: 40, damping: 25 }),
          y: useSpring(mouseY, { stiffness: 40, damping: 25 }),
        }}
        animate={{
          scale: dragActive ? 1.3 : busy ? 1.1 : 1.0,
          opacity: dragActive ? 0.28 : busy ? 0.2 : 0.14,
        }}
        transition={{ type: 'spring', stiffness: 20, damping: 12 }}
      />

      {/* Floating vector music notation symbols */}
      <div className="music-elements-container">
        {notes.map((note) => (
          <motion.div
            key={note.id}
            className="floating-music-element"
            style={{
              left: `${note.x}%`,
              top: `${note.y}%`,
              scale: note.scale,
              opacity: note.opacity,
              rotate: note.rotation,
              color: 'var(--accent)',
            }}
            animate={dragActive ? {
              scale: note.scale * 1.15,
              opacity: note.opacity * 1.8,
              color: 'var(--accent-2)',
            } : busy ? {
              opacity: note.opacity * 1.4,
              color: 'var(--accent-3)',
            } : {}}
            transition={{ duration: 0.5 }}
          >
            {renderMusicSvg(note.type)}
          </motion.div>
        ))}
      </div>

      {/* Dynamic horizontal music staffs running across screen */}
      <div className="background-staffs">
        {[1, 2, 3].map((staveIdx) => (
          <div
            key={staveIdx}
            className={`bg-staff staff-${staveIdx}`}
            style={{
              top: `${22 + staveIdx * 20}%`,
              opacity: dragActive ? 0.15 : busy ? 0.1 : 0.06,
              transform: `translateY(${(staveIdx - 2) * 20}px)`,
            }}
          >
            <div className="staff-line-bg" />
            <div className="staff-line-bg" />
            <div className="staff-line-bg" />
            <div className="staff-line-bg" />
            <div className="staff-line-bg" />
          </div>
        ))}
      </div>

      {/* Papyrus/Manuscript organic grain overlay */}
      <div className="manuscript-overlay" />
    </div>
  )
}
