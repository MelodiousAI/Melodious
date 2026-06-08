import { useRef, useState } from 'react'
import { ZoomIn, ZoomOut, Maximize2, Eye, ImageIcon, Columns2, ScanEye } from 'lucide-react'

interface Props {
  originalUrl: string | null
  overlayUrl: string | null
}

type Mode = 'overlay' | 'original' | 'compare'

export function ScoreViewer({ originalUrl, overlayUrl }: Props) {
  const [mode, setMode] = useState<Mode>('overlay')
  const [zoom, setZoom] = useState(1)
  const [split, setSplit] = useState(50)
  const compareRef = useRef<HTMLDivElement>(null)
  const dragging = useRef(false)

  function moveSplit(clientX: number) {
    const el = compareRef.current
    if (!el) return
    const rect = el.getBoundingClientRect()
    const ratio = ((clientX - rect.left) / rect.width) * 100
    setSplit(Math.max(0, Math.min(100, ratio)))
  }

  const single = mode === 'overlay' ? overlayUrl : originalUrl

  return (
    <div className="panel">
      <div className="panel-head">
        <div className="ttl">
          <ScanEye className="ic" size={17} /> Score viewer
        </div>
        <div className="seg">
          <button className={`seg-btn ${mode === 'overlay' ? 'on' : ''}`} onClick={() => setMode('overlay')}>
            <Eye size={13} style={{ verticalAlign: '-2px', marginRight: 5 }} />
            Overlay
          </button>
          <button className={`seg-btn ${mode === 'original' ? 'on' : ''}`} onClick={() => setMode('original')}>
            <ImageIcon size={13} style={{ verticalAlign: '-2px', marginRight: 5 }} />
            Original
          </button>
          <button className={`seg-btn ${mode === 'compare' ? 'on' : ''}`} onClick={() => setMode('compare')}>
            <Columns2 size={13} style={{ verticalAlign: '-2px', marginRight: 5 }} />
            Compare
          </button>
        </div>
      </div>

      {mode === 'compare' ? (
        <div
          className="compare"
          ref={compareRef}
          onPointerDown={(event) => {
            dragging.current = true
            moveSplit(event.clientX)
          }}
          onPointerMove={(event) => dragging.current && moveSplit(event.clientX)}
          onPointerUp={() => (dragging.current = false)}
          onPointerLeave={() => (dragging.current = false)}
        >
          {originalUrl && <img src={originalUrl} alt="Original score" />}
          <div className="after" style={{ width: `${split}%` }}>
            {overlayUrl && <img src={overlayUrl} alt="Detected overlay" />}
          </div>
          <span className="compare-tag" style={{ left: 10 }}>
            Original
          </span>
          <span className="compare-tag" style={{ right: 10 }}>
            Detected
          </span>
          <div className="compare-handle" style={{ left: `${split}%` }}>
            <div className="compare-knob">
              <Columns2 size={16} />
            </div>
          </div>
        </div>
      ) : (
        <div className="viewer-stage">
          {single ? (
            <img src={single} alt="Score" style={{ transform: `scale(${zoom})` }} />
          ) : (
            <div className="osmd-fallback">Image not available.</div>
          )}
        </div>
      )}

      {mode !== 'compare' && (
        <div className="viewer-toolbar">
          <span className="subtle">
            {mode === 'overlay' ? 'Detected notes, rests & pitches' : 'Uploaded source page'}
          </span>
          <div className="zoom-controls">
            <button className="icon-btn" onClick={() => setZoom((z) => Math.max(0.5, +(z - 0.25).toFixed(2)))}>
              <ZoomOut size={15} />
            </button>
            <span className="subtle" style={{ minWidth: 42, textAlign: 'center' }}>
              {Math.round(zoom * 100)}%
            </span>
            <button className="icon-btn" onClick={() => setZoom((z) => Math.min(3, +(z + 0.25).toFixed(2)))}>
              <ZoomIn size={15} />
            </button>
            <button className="icon-btn" onClick={() => setZoom(1)} title="Reset zoom">
              <Maximize2 size={15} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
