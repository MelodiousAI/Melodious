import { useMemo, useState } from 'react'
import { Table2, Search, Volume2, VolumeX } from 'lucide-react'
import type { NoteEvent } from '../lib/api'

interface Props {
  events: NoteEvent[]
}

type Filter = 'all' | 'notes' | 'rests' | 'dotted' | 'stem' | 'curves'

const FILTERS: { id: Filter; label: string }[] = [
  { id: 'all', label: 'All' },
  { id: 'notes', label: 'Notes' },
  { id: 'rests', label: 'Rests' },
  { id: 'dotted', label: 'Dotted' },
  { id: 'stem', label: 'Stem-confirmed' },
  { id: 'curves', label: 'Slur / tie' },
]

const PITCH_COLORS: Record<string, string> = {
  C: '#06b6d4', // Cyan
  D: '#8b5cf6', // Violet
  E: '#10b981', // Emerald
  F: '#ec4899', // Pink
  G: '#f59e0b', // Amber
  A: '#3b82f6', // Blue
  B: '#a855f7', // Purple
}

function getPitchColor(pitchLabel: string | null): string {
  if (!pitchLabel) return 'rgba(124, 92, 255, 0.12)'
  const baseNote = pitchLabel.charAt(0).toUpperCase()
  const color = PITCH_COLORS[baseNote]
  return color ? `${color}25` : 'rgba(124, 92, 255, 0.12)' // 25 is hex for ~15% opacity
}

let audioCtx: AudioContext | null = null

export function playMidiPitch(midiPitch: number | null, duration = 0.35) {
  if (midiPitch === null) return
  try {
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext
    if (!AudioContextClass) return
    if (!audioCtx) {
      audioCtx = new AudioContextClass()
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume()
    }
    
    // Pitch frequency calculation: 440 * 2^((midi - 69) / 12)
    const freq = 440 * Math.pow(2, (midiPitch - 69) / 12)
    
    const osc = audioCtx.createOscillator()
    const gainNode = audioCtx.createGain()
    
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime)
    
    // Triangle wave has a nice warm woodwind or soft keyboard sound
    osc.type = 'triangle'
    
    // Quick attack and smooth exponential decay
    gainNode.gain.setValueAtTime(0, audioCtx.currentTime)
    gainNode.gain.linearRampToValueAtTime(0.12, audioCtx.currentTime + 0.04)
    gainNode.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration)
    
    osc.connect(gainNode)
    gainNode.connect(audioCtx.destination)
    
    osc.start()
    osc.stop(audioCtx.currentTime + duration)
  } catch (e) {
    console.warn("Web Audio API not supported or blocked by browser policy", e)
  }
}

function Dot({ on }: { on: boolean }) {
  return <span className={`flagdot ${on ? 'flag-on' : 'flag-off'}`} />
}

export function NoteTable({ events }: Props) {
  const [filter, setFilter] = useState<Filter>('all')
  const [query, setQuery] = useState('')
  const [hoveredOrder, setHoveredOrder] = useState<number | null>(null)
  const [soundOn, setSoundOn] = useState(true)

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return events.filter((event) => {
      if (filter === 'notes' && event.event_type !== 'note') return false
      if (filter === 'rests' && event.event_type !== 'rest') return false
      if (filter === 'dotted' && !event.dotted) return false
      if (filter === 'stem' && !event.stem_detected) return false
      if (filter === 'curves' && event.slur_start_count + event.slur_stop_count + event.tie_start_count + event.tie_stop_count === 0)
        return false
      if (!q) return true
      const haystack = `${event.order} ${event.pitch_label ?? 'rest'} ${event.rhythm_source} ${event.source} ${event.midi_pitch ?? ''}`.toLowerCase()
      return haystack.includes(q)
    })
  }, [events, filter, query])

  const handleMouseEnter = (event: NoteEvent) => {
    setHoveredOrder(event.order)
    if (soundOn && event.event_type === 'note' && event.midi_pitch) {
      playMidiPitch(event.midi_pitch, 0.3)
    }
  }

  const handleMouseLeave = () => {
    setHoveredOrder(null)
  }

  return (
    <div className="panel">
      <div className="panel-head">
        <div className="ttl">
          <Table2 className="ic" size={17} /> Note &amp; event table
        </div>
        <div className="row" style={{ gap: 12 }}>
          <button 
            className={`btn btn--ghost btn--sm ${soundOn ? 'btn--accent' : ''}`}
            onClick={() => setSoundOn(!soundOn)}
            title={soundOn ? 'Mute note hover sounds' : 'Unmute note hover sounds'}
            style={{ padding: '6px 10px', minWidth: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}
          >
            {soundOn ? <Volume2 size={14} /> : <VolumeX size={14} />}
            <span style={{ fontSize: 11.5 }}>Sound {soundOn ? 'On' : 'Off'}</span>
          </button>
          <span className="subtle">
            {filtered.length} of {events.length} events
          </span>
        </div>
      </div>
      <div className="table-toolbar">
        <div className="search-box">
          <Search size={15} style={{ color: 'var(--text-dim)' }} />
          <input
            placeholder="Search pitch, source, rhythm…"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </div>
        <div className="filter-chips">
          {FILTERS.map((item) => (
            <button
              key={item.id}
              className={`chip ${filter === item.id ? 'on' : ''}`}
              onClick={() => setFilter(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
      <div className="note-table-wrap">
        <table className="note-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Type</th>
              <th>Pitch</th>
              <th>MIDI</th>
              <th>Dur</th>
              <th>Onset</th>
              <th>Staff</th>
              <th>Stem</th>
              <th>Slur</th>
              <th>Tie</th>
              <th>Rhythm</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((event) => {
              const isHovered = event.order === hoveredOrder
              const hoverBg = getPitchColor(event.pitch_label)
              return (
                <tr 
                  key={event.order}
                  className={isHovered ? 'hovered-row' : ''}
                  style={isHovered ? { '--row-hover-bg': hoverBg } as any : {}}
                  onMouseEnter={() => handleMouseEnter(event)}
                  onMouseLeave={handleMouseLeave}
                  onClick={() => {
                    if (event.event_type === 'note' && event.midi_pitch) {
                      playMidiPitch(event.midi_pitch, 0.6) // longer duration on click
                    }
                  }}
                >
                  <td>{event.order}</td>
                  <td>
                    <span className={`tag ${event.event_type === 'note' ? 'tag-note' : 'tag-rest'}`}>
                      {event.event_type}
                    </span>
                  </td>
                  <td className="pitch-tag">{event.event_type === 'note' ? event.pitch_label : '—'}</td>
                  <td>{event.midi_pitch ?? '—'}</td>
                  <td>
                    {event.quarter_length}
                    {event.dotted ? ' ·' : ''}
                  </td>
                  <td>{event.onset_quarter}</td>
                  <td>{event.staff_index + 1}</td>
                  <td>
                    <Dot on={event.stem_detected} />
                  </td>
                  <td>
                    <Dot on={event.slur_start_count + event.slur_stop_count > 0} />
                  </td>
                  <td>
                    <Dot on={event.tie_start_count + event.tie_stop_count > 0} />
                  </td>
                  <td className="src-tag">{event.rhythm_source}</td>
                  <td className="src-tag">{event.source}</td>
                </tr>
              )
            })}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={12} style={{ textAlign: 'center', padding: 28, color: 'var(--text-dim)' }}>
                  No events match this filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
