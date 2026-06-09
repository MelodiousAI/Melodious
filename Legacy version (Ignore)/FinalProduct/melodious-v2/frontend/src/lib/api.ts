// Typed client for the Melodious V2 product API.
// Mirrors the Pydantic models in src/melodious_v2/api/product_models.py.

export const API_BASE: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://127.0.0.1:8000'

export type JobStatus = 'queued' | 'processing' | 'complete' | 'failed'

export interface ProductCounts {
  staff_systems: number
  events: number
  notes: number
  rests: number
  dotted_notes: number
  stem_confirmed_notes: number
  slur_starts: number
  tie_starts: number
  relationship_count: number
}

export interface ModelProvenance {
  extractor_mode: string
  detector_checkpoint: string | null
  thin_symbol_checkpoint: string | null
  gnn_checkpoint: string | null
  assembly_mode: string
}

export interface ModelAvailability {
  full_page_detector: boolean
  tiled_detector: boolean
  gnn: boolean
}

export interface QualitySummary {
  label: 'high' | 'review' | 'low'
  score: number
  headline: string
  reasons: string[]
}

export interface NoteEvent {
  order: number
  event_type: 'note' | 'rest'
  staff_index: number
  onset_quarter: number
  quarter_length: number
  dotted: boolean
  rhythm_source: string
  source: string
  confidence: number
  step: string | null
  octave: number | null
  alter: number
  midi_pitch: number | null
  pitch_label: string | null
  pitch_source: string | null
  stem_detected: boolean
  slur_start_count: number
  slur_stop_count: number
  tie_start_count: number
  tie_stop_count: number
}

export interface ProductTranscription {
  job_id: string
  status: JobStatus
  stage: string
  stage_label: string
  progress: number
  filename: string | null
  created_at: number
  updated_at: number
  original_image_url: string | null
  overlay_image_url: string | null
  musicxml_url: string | null
  midi_url: string | null
  notes_json_url: string | null
  detector_payload_url: string | null
  relationships_url: string | null
  bundle_url: string | null
  image_width: number | null
  image_height: number | null
  key_fifths: number
  counts: ProductCounts
  model_provenance: ModelProvenance
  model_availability: ModelAvailability
  quality: QualitySummary
  note_events: NoteEvent[]
  warnings: string[]
  error: string | null
  metric_claim: string
  disclaimer: string
}

export interface ProductSample {
  sample_id: string
  title: string
  subtitle: string
  description: string
  available: boolean
}

export interface ModelsInfo {
  availability: ModelAvailability
  instruments: string[]
  ready: boolean
  note: string
}

async function jsonOrThrow<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const body = await response.json()
      if (body?.detail) detail = body.detail
    } catch {
      /* ignore parse errors */
    }
    throw new Error(detail)
  }
  return (await response.json()) as T
}

export async function getModels(): Promise<ModelsInfo> {
  return jsonOrThrow<ModelsInfo>(await fetch(`${API_BASE}/product/models`))
}

export async function getSamples(): Promise<ProductSample[]> {
  return jsonOrThrow<ProductSample[]>(await fetch(`${API_BASE}/product/samples`))
}

export async function transcribeImage(file: File, instrument: string): Promise<ProductTranscription> {
  const form = new FormData()
  form.append('file', file)
  form.append('instrument', instrument)
  return jsonOrThrow<ProductTranscription>(
    await fetch(`${API_BASE}/product/transcribe-image`, { method: 'POST', body: form }),
  )
}

export async function transcribeSample(sampleId: string, instrument: string): Promise<ProductTranscription> {
  const form = new FormData()
  form.append('sample_id', sampleId)
  form.append('instrument', instrument)
  return jsonOrThrow<ProductTranscription>(
    await fetch(`${API_BASE}/product/transcribe-sample`, { method: 'POST', body: form }),
  )
}

export async function getJob(jobId: string): Promise<ProductTranscription> {
  return jsonOrThrow<ProductTranscription>(await fetch(`${API_BASE}/product/jobs/${jobId}`))
}

export interface ArtifactOptions {
  download?: boolean
  instrument?: string
  tempoBpm?: number
}

export function artifactUrl(
  jobId: string,
  name: string,
  options: ArtifactOptions = {},
): string {
  const params = new URLSearchParams()
  if (options.download) params.set('download', 'true')
  if (options.instrument) params.set('instrument', options.instrument)
  if (options.tempoBpm) params.set('tempo_bpm', String(options.tempoBpm))
  const query = params.toString()
  return `${API_BASE}/product/jobs/${jobId}/artifacts/${name}${query ? `?${query}` : ''}`
}

// Absolute URL helper for artifact urls already returned by the API.
export function absoluteUrl(pathOrUrl: string | null): string | null {
  if (!pathOrUrl) return null
  if (pathOrUrl.startsWith('http')) return pathOrUrl
  return `${API_BASE}${pathOrUrl}`
}
