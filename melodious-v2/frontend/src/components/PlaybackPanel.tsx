import { useEffect, useMemo, useState } from 'react'
import { Headphones, Download, Repeat, Gauge, Piano, Loader2 } from 'lucide-react'
import { artifactUrl } from '../lib/api'

interface Props {
  jobId: string
  instrument: string
  instruments: string[]
  onInstrument: (value: string) => void
}

const SOUND_FONT = 'https://storage.googleapis.com/magentadata/js/soundfonts/sgm_plus'
const BASE_BPM = 96

export function PlaybackPanel({ jobId, instrument, instruments, onInstrument }: Props) {
  const [multiplier, setMultiplier] = useState(1)
  const [loop, setLoop] = useState(false)
  const [midiReady, setMidiReady] = useState(false)
  const tempoBpm = Math.round(BASE_BPM * multiplier)

  useEffect(() => {
    let cancelled = false
    import('html-midi-player')
      .then(() => {
        if (!cancelled) setMidiReady(true)
      })
      .catch(() => {
        if (!cancelled) setMidiReady(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const midiSrc = useMemo(
    () => artifactUrl(jobId, 'midi', { instrument, tempoBpm }),
    [jobId, instrument, tempoBpm],
  )
  const visualizerId = `vis-${jobId}`

  return (
    <div className="panel">
      <div className="panel-head">
        <div className="ttl">
          <Headphones className="ic" size={17} /> Playback
        </div>
        <a
          className="btn btn--ghost btn--sm"
          href={artifactUrl(jobId, 'midi', { instrument, tempoBpm, download: true })}
        >
          <Download size={14} /> MIDI
        </a>
      </div>
      <div className="panel-body">
        <div className="playback-body">
          <div className="midi-frame">
            {midiReady ? (
              <>
                {/* key forces a clean reload of the web component when audio source changes */}
                <midi-player
                  key={midiSrc}
                  src={midiSrc}
                  sound-font={SOUND_FONT}
                  visualizer={`#${visualizerId}`}
                  loop={loop || undefined}
                />
                <midi-visualizer id={visualizerId} type="piano-roll" src={midiSrc} />
              </>
            ) : (
              <div className="osmd-fallback">
                <Loader2 size={18} className="spin-ic" /> Loading MIDI player...
              </div>
            )}
          </div>

          <div className="play-controls">
            <div className="field">
              <label htmlFor="pb-instrument">
                <Piano size={12} style={{ verticalAlign: '-1px', marginRight: 5 }} />
                Instrument
              </label>
              <select
                id="pb-instrument"
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

            <div className="field">
              <label>
                <Gauge size={12} style={{ verticalAlign: '-1px', marginRight: 5 }} />
                Tempo · {tempoBpm} BPM
              </label>
              <div className="tempo-row">
                <input
                  type="range"
                  min={0.5}
                  max={1.5}
                  step={0.05}
                  value={multiplier}
                  onChange={(event) => setMultiplier(Number(event.target.value))}
                />
                <span className="tempo-val">{multiplier.toFixed(2)}×</span>
              </div>
            </div>
          </div>

          <button
            className={`btn btn--sm ${loop ? 'btn--accent' : 'btn--ghost'}`}
            onClick={() => setLoop((value) => !value)}
            style={{ alignSelf: 'flex-start' }}
          >
            <Repeat size={14} /> Loop {loop ? 'on' : 'off'}
          </button>

          <p className="subtle">
            Audio uses a General MIDI soundfont; the selected instrument and tempo are written into the
            MIDI so playback and the download match.
          </p>
        </div>
      </div>
    </div>
  )
}
