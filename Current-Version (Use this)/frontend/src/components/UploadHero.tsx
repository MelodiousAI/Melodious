import { useRef, useState, type DragEvent } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  UploadCloud,
  Image as ImageIcon,
  ScanLine,
  Workflow,
  FileMusic,
  Music,
  Compass,
  Play,
  FileCheck2,
} from 'lucide-react'
import type { ProductSample } from '../lib/api'

interface Props {
  samples: ProductSample[]
  instrument: string
  instruments: string[]
  onInstrument: (value: string) => void
  onFile: (file: File) => void
  onSample: (sampleId: string) => void
  busy: boolean
}

const POINTS = [
  { 
    ic: <ScanLine size={18} />, 
    title: 'Precision YOLOv8m Neural Detection',
    text: 'Identifies noteheads, clefs, and key signatures with a secondary tiled pass for stems, flags, and beams.' 
  },
  { 
    ic: <Workflow size={18} />, 
    title: 'Graph Neural Relation Resolver',
    text: 'A custom heterogenous GNN structures spatial note relationships to reconstruct rhythm and meter.' 
  },
  { 
    ic: <FileMusic size={18} />, 
    title: 'High-Fidelity Engraving & Playback',
    text: 'Generates MusicXML scores and standard MIDI files directly playable on your digital workstation.' 
  },
]

export function UploadHero({ samples, instrument, instruments, onInstrument, onFile, onSample, busy }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [drag, setDrag] = useState(false)

  function handleDrop(event: DragEvent) {
    event.preventDefault()
    setDrag(false)
    const file = event.dataTransfer.files?.[0]
    if (file) onFile(file)
  }

  return (
    <motion.div
      className="hero"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
    >
      <div className="hero-lead">
        <span className="section-eyebrow tracking-widest gold-glow">Sheet Music → Digital Audio Workstation</span>
        <h2 className="premium-headline">Reconstruct paper scores into playable music.</h2>
        <p className="sub leading-relaxed">
          Provide a single-page score image. Melodious runs our comprehensive V2 OMR pipeline — neural detection,
          graph relation assembly, and MusicXML/MIDI synthesis — revealing an interactive, audibly aligned engraved score.
        </p>

        {/* Elegant Animated Score Staff Deck */}
        <div className="animated-staff-container">
          <div className="animated-staff">
            <div className="staff-line" />
            <div className="staff-line" />
            <div className="staff-line" />
            <div className="staff-line" />
            <div className="staff-line" />
            
            {/* Elegant glowing notes gliding on the lines */}
            <motion.div 
              className="floating-note note-1"
              animate={{ 
                x: [10, 150, 20, 10],
                y: [4, -4, 12, 4],
              }}
              transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
            />
            <motion.div 
              className="floating-note note-2"
              animate={{ 
                x: [240, 40, 180, 240],
                y: [20, 12, 0, 20],
              }}
              transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
            />
            <motion.div 
              className="floating-note note-3"
              animate={{ 
                x: [120, 280, 80, 120],
                y: [12, 28, 4, 12],
              }}
              transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
            />
          </div>
        </div>

        <div className="hero-points">
          {POINTS.map((point, idx) => (
            <motion.div 
              className="hero-point-card" 
              key={point.title}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.15 + idx * 0.1, duration: 0.5 }}
              whileHover={{ x: 4, borderColor: 'rgba(204, 164, 59, 0.2)' }}
            >
              <span className="ic-box">{point.ic}</span>
              <div className="point-content">
                <h4>{point.title}</h4>
                <p>{point.text}</p>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="controls-row upload-controls">
          <div className="field">
            <label htmlFor="instrument">Playback Instrument</label>
            <div className="select-wrapper">
              <select
                id="instrument"
                className="select"
                value={instrument}
                onChange={(event) => onInstrument(event.target.value)}
              >
                {instruments.map((name) => (
                  <option key={name} value={name}>
                    {name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="hero-sidebar">
        {/* Luxurious Glassmorphic Dropzone */}
        <motion.div
          className={`dropzone ${drag ? 'dropzone--drag' : ''}`}
          onDragOver={(event) => {
            event.preventDefault()
            setDrag(true)
          }}
          onDragLeave={() => setDrag(false)}
          onDrop={handleDrop}
          whileHover={{ boxShadow: '0 20px 50px rgba(0, 0, 0, 0.5), 0 0 25px rgba(204, 164, 59, 0.08)' }}
        >
          <div className="dropzone-inner">
            <div className="upload-orb-container">
              <motion.div 
                className="orb-pulse" 
                animate={{ scale: drag ? [1, 1.4, 1] : [1, 1.25, 1], opacity: drag ? [0.4, 0.1, 0.4] : [0.3, 0, 0.3] }}
                transition={{ duration: 2.5, repeat: Infinity, ease: 'easeOut' }}
              />
              <motion.div 
                className="orb-pulse orb-pulse-2" 
                animate={{ scale: drag ? [1.2, 1.6, 1.2] : [1.1, 1.35, 1.1], opacity: drag ? [0.3, 0, 0.3] : [0.2, 0, 0.2] }}
                transition={{ duration: 2.5, delay: 1.25, repeat: Infinity, ease: 'easeOut' }}
              />
              <div className="upload-orb">
                <UploadCloud size={32} className="upload-icon" />
              </div>
            </div>
            
            <h3 className="dropzone-title">Awaiting Sheet Music...</h3>
            <p className="dropzone-text">Drag and drop score page here</p>
            <span className="dropzone-formats">PNG · JPG · WEBP · Single page format</span>
            
            <div className="dz-actions">
              <motion.button 
                className="btn btn--primary btn-choose-file" 
                disabled={busy} 
                onClick={() => inputRef.current?.click()}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
              >
                <ImageIcon size={15} /> Select File
              </motion.button>
            </div>
            
            <input
              ref={inputRef}
              className="hidden-input"
              type="file"
              accept="image/png,image/jpeg,image/webp,image/bmp,image/tiff"
              onChange={(event) => {
                const file = event.target.files?.[0]
                if (file) onFile(file)
                event.target.value = ''
              }}
            />
          </div>
        </motion.div>

        {/* Beautiful Curated Samples Gallery */}
        <div className="samples">
          <div className="samples-head">
            <div>
              <span className="section-eyebrow gold-glow">
                <Compass size={11} className="section-icon" />
                Score Library
              </span>
              <h3 className="gallery-title">Try a curated sample</h3>
            </div>
          </div>
          
          <div className="sample-grid">
            {samples.map((sample, idx) => (
              <motion.button
                key={sample.sample_id}
                className="sample-card"
                disabled={busy || !sample.available}
                onClick={() => onSample(sample.sample_id)}
                title={sample.available ? sample.description : 'Sample image not present on this host'}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={sample.available ? { y: -3, scale: 1.015, borderColor: 'rgba(204, 164, 59, 0.25)' } : {}}
                whileTap={sample.available ? { scale: 0.98 } : {}}
                transition={{ delay: 0.2 + idx * 0.08, duration: 0.4 }}
              >
                <div className="s-top">
                  <span className="s-ic">
                    {sample.available ? <Music size={15} /> : <FileCheck2 size={15} />}
                  </span>
                  <div className="s-header-text">
                    <strong className="sample-title">{sample.title}</strong>
                    <div className="s-sub">{sample.subtitle}</div>
                  </div>
                  <span className="spacer" />
                  {sample.available && (
                    <motion.span 
                      className="play-btn-pill"
                      whileHover={{ scale: 1.1, backgroundColor: 'rgba(204, 164, 59, 0.15)' }}
                    >
                      <Play size={10} className="play-icon" />
                    </motion.span>
                  )}
                </div>
                <div className="s-desc">{sample.description}</div>
              </motion.button>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
