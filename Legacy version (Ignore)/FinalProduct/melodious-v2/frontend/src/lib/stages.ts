// Maps backend extraction stages onto the 5-step frontend progress timeline.

export interface TimelineStep {
  id: string
  label: string
  note: string
  stages: string[]
}

export const TIMELINE_STEPS: TimelineStep[] = [
  {
    id: 'upload',
    label: 'Uploading',
    note: 'Receiving the page and reading pixels',
    stages: ['queued', 'uploading', 'reading_image'],
  },
  {
    id: 'detect',
    label: 'Detecting symbols',
    note: 'Staff systems, noteheads & tiled thin symbols',
    stages: ['detecting_staff', 'detecting_symbols', 'detecting_thin_symbols'],
  },
  {
    id: 'graph',
    label: 'Building note graph',
    note: 'GNN relationships for stems & beams',
    stages: ['building_graph'],
  },
  {
    id: 'export',
    label: 'Exporting MusicXML',
    note: 'Assembling events & writing MusicXML/MIDI',
    stages: ['assembling_events', 'exporting'],
  },
  {
    id: 'render',
    label: 'Rendering playback',
    note: 'Engraving the score & preparing audio',
    stages: ['complete'],
  },
]

const STAGE_ORDER = [
  'queued',
  'uploading',
  'reading_image',
  'detecting_staff',
  'detecting_symbols',
  'detecting_thin_symbols',
  'building_graph',
  'assembling_events',
  'exporting',
  'complete',
]

export function activeStepIndex(stage: string, status: string): number {
  if (status === 'complete') return TIMELINE_STEPS.length - 1
  const idx = TIMELINE_STEPS.findIndex((step) => step.stages.includes(stage))
  return idx >= 0 ? idx : 0
}

export function stageOrder(stage: string): number {
  const idx = STAGE_ORDER.indexOf(stage)
  return idx >= 0 ? idx : 0
}
