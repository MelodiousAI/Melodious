import { useEffect, useState } from 'react'
import { useSpring, useTransform, motion } from 'framer-motion'

export function CountUp({ value, duration = 0.8 }: { value: number; duration?: number }) {
  const spring = useSpring(0, { stiffness: 60, damping: 18 })
  const display = useTransform(spring, (v) => Math.round(v))
  const [shown, setShown] = useState(0)

  useEffect(() => {
    spring.set(value)
    const unsub = display.on('change', (v) => setShown(v))
    return unsub
  }, [value, spring, display])

  return <motion.span initial={{ opacity: 0.6 }} animate={{ opacity: 1 }} transition={{ duration }}>{shown}</motion.span>
}
