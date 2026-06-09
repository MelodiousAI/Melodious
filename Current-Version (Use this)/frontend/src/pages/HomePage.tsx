import { ArrowRight, FileText, Headphones, Music, Upload } from 'lucide-react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { FloatingScore } from '../components/FloatingScore'

const steps = [
  {
    icon: Music,
    title: 'Choose a score',
    description: 'Pick from our curated library or upload your own sheet music — PDF, image, or photo.',
  },
  {
    icon: FileText,
    title: 'Melodious transcribes it',
    description: 'We read the notation — notes, rests, clefs, dynamics — and produce a clean digital version.',
  },
  {
    icon: Headphones,
    title: 'Listen, review, export',
    description: 'Play it back, inspect the results, and download as MusicXML or MIDI.',
  },
]

const ways = [
  {
    icon: Music,
    title: 'Try a sample',
    description: 'Start with a curated piece from our library — no upload needed.',
    to: '/library',
    alt: false,
  },
  {
    icon: Upload,
    title: 'Upload a score',
    description: 'Bring your own sheet music as an image or photo.',
    to: '/upload',
    alt: true,
  },
]

export function HomePage() {
  return (
    <div className="page-enter">
      <section className="hero-section">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55 }}>
          <h1 className="hero-headline">
            Sheet music,
            <br />
            <span className="accent">understood.</span>
          </h1>
          <p className="hero-lead">
            Melodious reads your sheet music and turns it into a playable, exportable digital score. No scanning
            headaches — just music.
          </p>
          <div className="hero-actions">
            <Link to="/library" className="btn btn--primary">
              Try a sample <ArrowRight size={16} />
            </Link>
            <Link to="/upload" className="btn btn--ghost">
              Upload a score
            </Link>
          </div>
        </motion.div>
        <div className="hero-art">
          <FloatingScore />
        </div>
      </section>

      <section className="how-section">
        <h2>How it works</h2>
        <div className="how-grid">
          {steps.map((step, i) => {
            const Icon = step.icon
            return (
              <motion.div
                key={step.title}
                className="how-step"
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.45 }}
              >
                <div className="how-icon">
                  <Icon size={18} />
                </div>
                <div>
                  <h3>{step.title}</h3>
                  <p>{step.description}</p>
                </div>
              </motion.div>
            )
          })}
        </div>
      </section>

      <section className="ways-section">
        <motion.div initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <h2>Ways to start</h2>
          <p className="ways-sub">Bring your music in however works best for you.</p>
          <div className="ways-grid">
            {ways.map((way, i) => {
              const Icon = way.icon
              return (
                <motion.div
                  key={way.title}
                  initial={{ opacity: 0, y: 12 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.08 }}
                >
                  <Link to={way.to} className={`way-card${way.alt ? ' alt' : ''}`}>
                    <div className="way-icon">
                      <Icon size={22} />
                    </div>
                    <h3>{way.title}</h3>
                    <p>{way.description}</p>
                  </Link>
                </motion.div>
              )
            })}
          </div>
        </motion.div>
      </section>
    </div>
  )
}
