import { useRef, useState, type DragEvent } from 'react'
import { motion } from 'framer-motion'
import { Upload, Image as ImageIcon } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTranscription } from '../lib/transcription-context'

export function UploadPage() {
  const { instrument, instruments, setInstrument, busy, startWithFile } = useTranscription()
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)
  const [drag, setDrag] = useState(false)
  const [uploading, setUploading] = useState(false)

  async function handleFile(file: File) {
    if (busy || uploading) return
    setUploading(true)
    try {
      await startWithFile(file)
      navigate('/workspace')
    } catch {
      setUploading(false)
    }
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault()
    setDrag(false)
    const file = event.dataTransfer.files?.[0]
    if (file) void handleFile(file)
  }

  return (
    <div className="page-enter upload-page">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <h1>Upload a score</h1>
        <p className="lead">
          Drop a single page of sheet music — we&apos;ll read the notation and turn it into MusicXML and MIDI.
        </p>
      </motion.div>

      <motion.div
        className={`dropzone${drag ? ' dropzone--drag' : ''}`}
        onDragOver={(e) => {
          e.preventDefault()
          setDrag(true)
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        whileHover={{ scale: 1.005 }}
      >
        <div className="dropzone-icon">
          <Upload size={26} />
        </div>
        <h3>Drop your score here</h3>
        <p>or click to browse</p>
        <span className="dropzone-formats">PNG · JPG · WEBP · BMP · TIFF</span>
        <input
          ref={inputRef}
          className="hidden-input"
          type="file"
          accept="image/png,image/jpeg,image/webp,image/bmp,image/tiff"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) void handleFile(file)
            e.target.value = ''
          }}
        />
      </motion.div>

      <div className="controls-row">
        <div className="field">
          <label htmlFor="instrument">Playback instrument</label>
          <select
            id="instrument"
            className="select"
            value={instrument}
            onChange={(e) => setInstrument(e.target.value)}
          >
            {instruments.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>
        <button
          className="btn btn--primary"
          disabled={busy || uploading}
          onClick={() => inputRef.current?.click()}
        >
          <ImageIcon size={16} /> Choose file
        </button>
      </div>
    </div>
  )
}
