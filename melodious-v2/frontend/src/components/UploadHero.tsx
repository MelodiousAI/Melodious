import { useRef, useState, type DragEvent } from 'react'
import { motion } from 'framer-motion'
import {
  UploadCloud,
  Image as ImageIcon,
  ScanLine,
  Workflow,
  FileMusic,
  Music,
  Sparkles,
  Play,
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
  { ic: <ScanLine size={18} />, text: 'Trained YOLOv8m detector finds noteheads, plus a tiled pass for stems, beams & flags.' },
  { ic: <Workflow size={18} />, text: 'A graph neural network links stems and beams to recover rhythm.' },
  { ic: <FileMusic size={18} />, text: 'Exports playable MusicXML and MIDI with an engraved score and note table.' },
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
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      <div className="hero-lead">
        <span className="section-eyebrow">Sheet music → MusicXML · MIDI</span>
        <h2>Turn a photo of a score into playable music.</h2>
        <p className="sub">
          Upload a sheet-music image and Melodious runs the real V2 recognition pipeline — detection,
          graph assembly, and export — then shows you the overlay, engraved score, audio, and every
          extracted note.
        </p>
        <div className="hero-points">
          {POINTS.map((point) => (
            <div className="hero-point" key={point.text}>
              <span className="ic">{point.ic}</span>
              <span>{point.text}</span>
            </div>
          ))}
        </div>

        <div className="controls-row">
          <div className="field">
            <label htmlFor="instrument">Playback instrument</label>
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

      <div>
        <div
          className={`dropzone ${drag ? 'dropzone--drag' : ''}`}
          onDragOver={(event) => {
            event.preventDefault()
            setDrag(true)
          }}
          onDragLeave={() => setDrag(false)}
          onDrop={handleDrop}
        >
          <div className="dropzone-inner">
            <div className="upload-orb float">
              <UploadCloud size={34} />
            </div>
            <h3>Drop a score image here</h3>
            <p>PNG, JPG or WEBP · single page works best</p>
            <div className="dz-actions">
              <button className="btn btn--primary" disabled={busy} onClick={() => inputRef.current?.click()}>
                <ImageIcon size={16} /> Choose image
              </button>
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
        </div>

        <div className="samples">
          <div className="samples-head">
            <div>
              <span className="section-eyebrow">
                <Sparkles size={12} style={{ verticalAlign: '-1px', marginRight: 6 }} />
                Demo gallery
              </span>
              <h3>Try a curated example</h3>
            </div>
          </div>
          <div className="sample-grid">
            {samples.map((sample) => (
              <button
                key={sample.sample_id}
                className="sample-card"
                disabled={busy || !sample.available}
                onClick={() => onSample(sample.sample_id)}
                title={sample.available ? sample.description : 'Sample image not present on this host'}
              >
                <div className="s-top">
                  <span className="s-ic">
                    <Music size={17} />
                  </span>
                  <div>
                    <strong>{sample.title}</strong>
                    <div className="s-sub">{sample.subtitle}</div>
                  </div>
                  <span className="spacer" />
                  {sample.available && <Play size={15} style={{ color: 'var(--accent-2)' }} />}
                </div>
                <div className="s-desc">{sample.description}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
