import { useMemo, useState } from 'react'
import { Table2, Search } from 'lucide-react'
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

function Dot({ on }: { on: boolean }) {
  return <span className={`flagdot ${on ? 'flag-on' : 'flag-off'}`} />
}

export function NoteTable({ events }: Props) {
  const [filter, setFilter] = useState<Filter>('all')
  const [query, setQuery] = useState('')

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

  return (
    <div className="panel">
      <div className="panel-head">
        <div className="ttl">
          <Table2 className="ic" size={17} /> Note &amp; event table
        </div>
        <span className="subtle">
          {filtered.length} of {events.length} events
        </span>
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
            {filtered.map((event) => (
              <tr key={event.order}>
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
            ))}
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
