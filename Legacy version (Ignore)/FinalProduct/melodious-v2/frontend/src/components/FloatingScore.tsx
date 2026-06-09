import { motion } from 'framer-motion'

const TOP_NOTES = [
  { x: 80, y: 64 },
  { x: 108, y: 56 },
  { x: 136, y: 52 },
  { x: 176, y: 60 },
  { x: 204, y: 68 },
  { x: 232, y: 56 },
  { x: 260, y: 48 },
  { x: 300, y: 60 },
]

const BOTTOM_NOTES = [
  { x: 80, y: 134 },
  { x: 136, y: 126 },
  { x: 176, y: 130 },
  { x: 232, y: 122 },
  { x: 300, y: 130 },
]

function NoteHead({ x, y, delay }: { x: number; y: number; delay: number }) {
  return (
    <motion.g
      initial={{ opacity: 0, y: y + 4 }}
      animate={{ opacity: 0.65, y }}
      transition={{ delay, duration: 0.45 }}
    >
      <ellipse cx={x} cy={y} rx="4.5" ry="3" fill="hsl(20 14% 10%)" transform={`rotate(-8 ${x} ${y})`} />
      <line x1={x + 4} y1={y} x2={x + 4} y2={y - 20} stroke="hsl(20 14% 10%)" strokeWidth="0.8" />
    </motion.g>
  )
}

export function FloatingScore() {
  return (
    <div className="floating-score">
      <motion.div
        className="score-sheet back"
        initial={{ opacity: 0, x: -12 }}
        animate={{ opacity: 0.85, x: 0 }}
        transition={{ delay: 0.1, duration: 0.7 }}
      >
        <svg viewBox="0 0 200 70" className="w-full" style={{ width: '100%' }} xmlns="http://www.w3.org/2000/svg">
          {[15, 23, 31, 39, 47].map((y) => (
            <line key={y} x1="10" y1={y} x2="190" y2={y} stroke="hsl(20 14% 10%)" strokeWidth="0.5" opacity="0.35" />
          ))}
          <text x="16" y="42" fontSize="18" fill="hsl(20 14% 10%)" opacity="0.5">
            C
          </text>
        </svg>
      </motion.div>

      <motion.div
        className="score-sheet front"
        initial={{ opacity: 0, y: 20, rotate: -3 }}
        animate={{ opacity: 1, y: 0, rotate: -1.5 }}
        transition={{ delay: 0.25, duration: 0.8, ease: 'easeOut' }}
      >
        <svg viewBox="0 0 360 180" style={{ width: '100%' }} xmlns="http://www.w3.org/2000/svg">
          {[40, 48, 56, 64, 72].map((y, i) => (
            <motion.line
              key={`s1-${i}`}
              x1="20"
              y1={y}
              x2="340"
              y2={y}
              stroke="hsl(20 14% 10%)"
              strokeWidth="0.6"
              opacity="0.35"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ delay: 0.5 + i * 0.04, duration: 0.6 }}
            />
          ))}
          <motion.text
            x="26"
            y="68"
            fontSize="24"
            fill="hsl(20 14% 10%)"
            opacity="0.55"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.55 }}
            transition={{ delay: 0.9 }}
          >
            𝄞
          </motion.text>
          {TOP_NOTES.map((note, i) => (
            <NoteHead key={`t-${i}`} x={note.x} y={note.y} delay={1.1 + i * 0.06} />
          ))}
          {[110, 118, 126, 134, 142].map((y, i) => (
            <motion.line
              key={`s2-${i}`}
              x1="20"
              y1={y}
              x2="340"
              y2={y}
              stroke="hsl(20 14% 10%)"
              strokeWidth="0.6"
              opacity="0.35"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ delay: 0.7 + i * 0.04, duration: 0.6 }}
            />
          ))}
          <motion.text
            x="26"
            y="136"
            fontSize="18"
            fill="hsl(20 14% 10%)"
            opacity="0.55"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.55 }}
            transition={{ delay: 1.1 }}
          >
            𝄢
          </motion.text>
          {BOTTOM_NOTES.map((note, i) => (
            <NoteHead key={`b-${i}`} x={note.x} y={note.y} delay={1.3 + i * 0.06} />
          ))}
          <motion.text
            x="70"
            y="162"
            fontSize="10"
            fontStyle="italic"
            fill="hsl(38 75% 38%)"
            opacity="0.65"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.65 }}
            transition={{ delay: 1.8 }}
          >
            mp espressivo
          </motion.text>
        </svg>
      </motion.div>
    </div>
  )
}
