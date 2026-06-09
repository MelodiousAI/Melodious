import type {
  ProductConfig,
  ProductSample,
  ProductTranscriptionResult,
} from '../types/product'

export const mockConfig: ProductConfig = {
  app_name: 'Melodious',
  stage: 'v0.5',
  active_experience: 'sample_first',
  upload_status_message:
    'Raw sheet-music upload is reserved for a later detector integration. Week 5 focuses on polished sample-based demos.',
  feature_flags: {
    image_upload_enabled: false,
    attention_overlay_enabled: false,
    llm_explainer_enabled: false,
  },
}

export const mockSamples: ProductSample[] = [
  {
    id: 'CVC-MUSCIMA_W-01_N-10_D-ideal',
    title: 'Handwritten Study 10',
    subtitle: 'Writer 01 · MUSCIMA++ sample',
    document_name: 'CVC-MUSCIMA_W-01_N-10_D-ideal',
    preview_image_url: '/product/samples/CVC-MUSCIMA_W-01_N-10_D-ideal/image',
    description: 'A clean handwritten study page with dense note clusters and clear staff structure.',
    tags: ['Handwritten', 'MUSCIMA++', 'Demo'],
  },
  {
    id: 'CVC-MUSCIMA_W-01_N-14_D-ideal',
    title: 'Handwritten Study 14',
    subtitle: 'Writer 01 · MUSCIMA++ sample',
    document_name: 'CVC-MUSCIMA_W-01_N-14_D-ideal',
    preview_image_url: '/product/samples/CVC-MUSCIMA_W-01_N-14_D-ideal/image',
    description: 'A balanced page for showing the full transcription and export flow.',
    tags: ['Handwritten', 'MUSCIMA++', 'Demo'],
  },
  {
    id: 'CVC-MUSCIMA_W-02_N-06_D-ideal',
    title: 'Handwritten Study 06',
    subtitle: 'Writer 02 · MUSCIMA++ sample',
    document_name: 'CVC-MUSCIMA_W-02_N-06_D-ideal',
    preview_image_url: '/product/samples/CVC-MUSCIMA_W-02_N-06_D-ideal/image',
    description: 'A more varied sample for previewing confidence and explainability placeholders.',
    tags: ['Handwritten', 'MUSCIMA++', 'Demo'],
  },
]

export const mockTranscriptionResult: ProductTranscriptionResult = {
  sample: mockSamples[0],
  score_preview: {
    image_url: mockSamples[0].preview_image_url,
    alt_text: `Preview image for ${mockSamples[0].title}`,
  },
  transcription_summary: {
    detection_count: 478,
    note_count: 248,
    clef_count: 9,
    rest_count: 17,
    unmatched_count: 23,
  },
  confidence_indicator: {
    tone: 'medium',
    label: 'Promising preview',
    message:
      'This is a qualitative Week 5 cue based on current assembly coverage. It is not a calibrated model probability.',
    calibrated: false,
  },
  explainability: {
    state: 'placeholder',
    title: 'Attention Overlay',
    message: 'Attention preview is reserved for the future GNN checkpoint integration.',
  },
  downloads: {
    musicxml: {
      ready: true,
      url: '/product/samples/CVC-MUSCIMA_W-01_N-10_D-ideal/downloads/musicxml',
      file_name: 'CVC-MUSCIMA_W-01_N-10_D-ideal.musicxml',
      content_type: 'application/vnd.recordare.musicxml+xml',
    },
    midi: {
      ready: true,
      url: '/product/samples/CVC-MUSCIMA_W-01_N-10_D-ideal/downloads/midi',
      file_name: 'CVC-MUSCIMA_W-01_N-10_D-ideal.mid',
      content_type: 'audio/midi',
    },
  },
  audio: {
    playable: true,
    source_url: '/product/samples/CVC-MUSCIMA_W-01_N-10_D-ideal/downloads/midi',
    format: 'midi',
    message: 'MIDI playback uses the exported demo file for this sample.',
  },
  feature_flags: mockConfig.feature_flags,
  notices: [],
}
