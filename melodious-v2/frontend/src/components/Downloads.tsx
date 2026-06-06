import { FileMusic, FileAudio, ImageDown, FileJson, Network, Package, Download } from 'lucide-react'
import { artifactUrl, type ProductTranscription } from '../lib/api'

interface Props {
  job: ProductTranscription
  instrument: string
}

export function Downloads({ job, instrument }: Props) {
  const items = [
    { name: 'musicxml', label: 'MusicXML', sub: 'Notation', icon: <FileMusic size={18} />, show: !!job.musicxml_url },
    {
      name: 'midi',
      label: 'MIDI',
      sub: instrument,
      icon: <FileAudio size={18} />,
      show: !!job.midi_url,
      extra: { instrument },
    },
    { name: 'overlay', label: 'Overlay PNG', sub: 'Annotated', icon: <ImageDown size={18} />, show: !!job.overlay_image_url },
    { name: 'notes', label: 'Notes JSON', sub: 'All events', icon: <FileJson size={18} />, show: !!job.notes_json_url },
    {
      name: 'detector_payload',
      label: 'Detector payload',
      sub: 'V2 contract',
      icon: <FileJson size={18} />,
      show: !!job.detector_payload_url,
    },
    {
      name: 'relationships',
      label: 'Relationships',
      sub: 'Symbol links',
      icon: <Network size={18} />,
      show: !!job.relationships_url,
    },
    { name: 'bundle', label: 'Full bundle', sub: 'ZIP of all', icon: <Package size={18} />, show: !!job.bundle_url },
  ]

  return (
    <div className="panel">
      <div className="panel-head">
        <div className="ttl">
          <Download className="ic" size={17} /> Downloads
        </div>
      </div>
      <div className="panel-body">
        <div className="downloads">
          {items
            .filter((item) => item.show)
            .map((item) => (
              <a
                key={item.name}
                className="dl"
                href={artifactUrl(job.job_id, item.name, { download: true, ...(item.extra ?? {}) })}
              >
                <span className="ic">{item.icon}</span>
                <span>
                  {item.label}
                  <span className="sub" style={{ display: 'block' }}>
                    {item.sub}
                  </span>
                </span>
              </a>
            ))}
        </div>
      </div>
    </div>
  )
}
