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

const containerVariants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.08
    }
  }
}

const fade = {
  initial: { opacity: 0, y: 22 },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: {
      type: 'spring' as const,
      stiffness: 70,
      damping: 14
    }
  },
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
    <motion.div 
      className="workspace" 
      variants={containerVariants}
      initial="initial" 
      animate="animate"
    >
      <motion.div className="ws-head" variants={fade}>
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

      <div className="ws-grid">
        <div className="col">
          <motion.div variants={fade}>
            <ScoreViewer
              originalUrl={absoluteUrl(job.original_image_url)}
              overlayUrl={absoluteUrl(job.overlay_image_url)}
            />
          </motion.div>
          <motion.div variants={fade}>
            <EngravedScore musicXml={xml} />
          </motion.div>
          <motion.div variants={fade}>
            <MusicXmlPanel musicXml={xml} downloadUrl={artifactUrl(job.job_id, 'musicxml', { download: true })} />
          </motion.div>
        </div>

        <div className="col">
          <motion.div variants={fade}>
            <QualityPanel quality={job.quality} />
          </motion.div>
          <motion.div variants={fade}>
            <PlaybackPanel
              jobId={job.job_id}
              instrument={instrument}
              instruments={instruments}
              onInstrument={onInstrument}
            />
          </motion.div>
          <motion.div variants={fade}>
            <CountsPanel counts={job.counts} />
          </motion.div>
          <motion.div variants={fade}>
            <ProvenancePanel
              provenance={job.model_provenance}
              availability={job.model_availability}
              keyFifths={job.key_fifths}
              width={job.image_width}
              height={job.image_height}
            />
          </motion.div>
          <motion.div variants={fade}>
            <ReviewPanel warnings={job.warnings} />
          </motion.div>
        </div>
      </div>

      <motion.div variants={fade}>
        <NoteTable events={job.note_events} />
      </motion.div>

      <motion.div variants={fade}>
        <Downloads job={job} instrument={instrument} />
      </motion.div>
    </motion.div>
  )
}
