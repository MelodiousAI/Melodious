export type ProductFeatureFlags = {
  image_upload_enabled: boolean
  attention_overlay_enabled: boolean
  llm_explainer_enabled: boolean
}

export type ProductConfig = {
  app_name: string
  stage: string
  active_experience: 'sample_first'
  upload_status_message: string
  feature_flags: ProductFeatureFlags
}

export type ProductSample = {
  id: string
  title: string
  subtitle: string
  document_name: string
  preview_image_url: string
  description: string
  tags: string[]
}

export type ProductSamplesResponse = {
  items: ProductSample[]
}

export type ProductTranscriptionSummary = {
  detection_count: number
  note_count: number
  clef_count: number
  rest_count: number
  unmatched_count: number
}

export type ProductConfidenceIndicator = {
  tone: 'high' | 'medium' | 'low'
  label: string
  message: string
  calibrated: boolean
}

export type ProductExplainability = {
  state: 'available' | 'placeholder' | 'unavailable'
  title: string
  message: string
}

export type ProductDownload = {
  ready: boolean
  url: string
  file_name: string
  content_type: string
}

export type ProductDownloads = {
  musicxml: ProductDownload
  midi: ProductDownload
}

export type ProductAudio = {
  playable: boolean
  source_url: string
  format: 'midi'
  message: string
}

export type ProductTranscriptionResult = {
  sample: ProductSample
  score_preview: {
    image_url: string
    alt_text: string
  }
  transcription_summary: ProductTranscriptionSummary
  confidence_indicator: ProductConfidenceIndicator
  explainability: ProductExplainability
  downloads: ProductDownloads
  audio: ProductAudio
  feature_flags: ProductFeatureFlags
  notices: string[]
}
