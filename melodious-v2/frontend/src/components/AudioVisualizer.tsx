import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

export function AudioVisualizer({ active }: { active: boolean }) {
  const bars = Array.from({ length: 12 })
  const [heights, setHeights] = useState(bars.map(() => 10))

  useEffect(() => {
    if (!active) {
      setHeights(bars.map(() => 10))
      return
    }

    const interval = setInterval(() => {
      setHeights(bars.map(() => 10 + Math.random() * 40))
    }, 150)

    return () => clearInterval(interval)
  }, [active])

  return (
    <div className="audio-visualizer">
      {heights.map((h, i) => (
        <motion.div
          key={i}
          className="visualizer-bar"
          animate={{ height: h }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
        />
      ))}
    </div>
  )
}
