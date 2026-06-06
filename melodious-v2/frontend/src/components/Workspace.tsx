import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle2 } from 'lucide-react'
import { absoluteUrl, artifactUrl, type ProductTranscription } from '../lib/api'
import { ScoreViewer } from './ScoreViewer'
import { EngravedScore } from './EngravedScore'
import { MusicXmlPanel } from './MusicXmlPanel'
import { PlaybackPanel } from './PlaybackPanel'
import { NoteTable } from './NoteTable'
import { Downloads } from './Downloads'
import { CountsPanel, ProvenancePanel, QualityPanel, ReviewPanel } from './InsightPanels'

interface Props {
  job: ProductTranscription
  instrument: string
  instruments: string[]
  onInstrument: (value: string) => void
}

const fade = {
  initial: { opacity: 0, y: 18 },
  animate: { opacity: 1, y: 0 },
}

export function Workspace({ job, instrument, instruments, onInstrument }: Props) {
  const [xml, setXml] = useState<string | null>(null)

  useEffect(() => {
    const url = absoluteUrl(job.musicxml_url)
    if (!url) return
    let cancelled = false
    fetch(url)
      .then((response) => response.text())
      .then((text) => !cancelled && setXml(text))
      .catch(() => !cancelled && setXml(null))
    return () => {
      cancelled = true
    }
  }, [job.musicxml_url])

  return (
    <motion.div className="workspace" initial="initial" animate="animate" transition={{ staggerChildren: 0.06 }}>
      <motion.div className="ws-head" variants={fade} transition={{ duration: 0.4 }}>
        <div>
          <span className="section-eyebrow">
            <CheckCircle2 size={12} style={{ verticalAlign: '-1px', marginRight: 6 }} />
            Transcription complete
          </span>
          <h2>{job.filename ?? 'Score transcription'}</h2>
          <div className="file">
            {job.counts.notes} notes · {job.counts.staff_systems} staff systems · {job.counts.relationship_count} GNN
            links · {job.model_provenance.extractor_mode}
          </div>
        </div>
      </motion.div>

      <motion.div className="ws-grid" variants={fade} transition={{ duration: 0.45 }}>
        <div className="col">
          <ScoreViewer
            originalUrl={absoluteUrl(job.original_image_url)}
            overlayUrl={absoluteUrl(job.overlay_image_url)}
          />
          <EngravedScore musicXml={xml} />
          <MusicXmlPanel musicXml={xml} downloadUrl={artifactUrl(job.job_id, 'musicxml', { download: true })} />
        </div>

        <div className="col">
          <QualityPanel quality={job.quality} />
          <PlaybackPanel
            jobId={job.job_id}
            instrument={instrument}
            instruments={instruments}
            onInstrument={onInstrument}
          />
          <CountsPanel counts={job.counts} />
          <ProvenancePanel
            provenance={job.model_provenance}
            availability={job.model_availability}
            keyFifths={job.key_fifths}
            width={job.image_width}
            height={job.image_height}
          />
          <ReviewPanel warnings={job.warnings} />
        </div>
      </motion.div>

      <motion.div variants={fade} transition={{ duration: 0.45 }}>
        <NoteTable events={job.note_events} />
      </motion.div>

      <motion.div variants={fade} transition={{ duration: 0.45 }}>
        <Downloads job={job} instrument={instrument} />
      </motion.div>
    </motion.div>
  )
}
