import { fetchProductSamples, transcribeImage, transcribeSample } from '../lib/api'
import type { ProductSample, ProductTranscriptionResult } from '../types/product'

type SamplePreset = {
  title: string
  subtitle: string
  icon: string
  tags: string[]
  description: string
  instrument: string
  era: string
  featured?: boolean
}

export type DisplaySample = ProductSample & {
  icon: string
  instrument: string
  era: string
  featured?: boolean
}

export type DisplayTranscriptionResult = {
  title: string
  sampleId: string
  resultSummary: string
  summary: {
    noteCount: number
    clefCount: number
    restCount: number
    reviewCount: number
  }
  confidenceIndicator: {
    tone: 'high' | 'moderate' | 'low'
    label: string
    message: string
    calibrated: boolean
  }
  explainability: {
    state: 'unavailable' | 'available'
    title: string
    message: string
  }
  downloads: {
    musicxmlReady: boolean
    midiReady: boolean
    musicxmlUrl: string
    midiUrl: string
  }
  audio: {
    playable: boolean
    sourceUrl: string
  }
}

const SAMPLE_PRESETS: SamplePreset[] = [
  {
    title: 'Nocturne in E-flat Major',
    subtitle: 'Chopin, Op. 9 No. 2',
    icon: '♪',
    tags: ['Lyrical', 'Expressive'],
    instrument: 'Piano',
    era: 'Romantic',
    description:
      "One of Chopin's most beloved nocturnes, reframed here as the featured Melodious sample experience.",
    featured: true,
  },
  {
    title: 'Partita No. 2 in D Minor',
    subtitle: 'J.S. Bach, BWV 1004',
    icon: '♩',
    tags: ['Polyphonic', 'Solo'],
    instrument: 'Violin',
    era: 'Baroque',
    description:
      'A denser single-line sample that keeps the library visually close to the Lovable concept while still using your repo-local preview assets.',
  },
  {
    title: 'Sonata in C Major',
    subtitle: 'Mozart, K. 545',
    icon: '♫',
    tags: ['Elegant', 'Pedagogical'],
    instrument: 'Piano',
    era: 'Classical',
    description:
      'A clean score profile that fits the lighter, classical sample card from the Lovable design.',
  },
  {
    title: 'Arabesque No. 1',
    subtitle: 'Debussy, L. 66',
    icon: '♬',
    tags: ['Flowing', 'Complex harmonies'],
    instrument: 'Piano',
    era: 'Impressionist',
    description:
      'A more intricate sample slot for the richer confidence and review states in the workspace design.',
  },
]

export const supportedFormats = ['PNG', 'JPG', 'JPEG', 'TIFF']

export async function fetchDisplaySamples(): Promise<DisplaySample[]> {
  const response = await fetchProductSamples()

  return response.items.slice(0, SAMPLE_PRESETS.length).map((sample, index) => {
    const preset = SAMPLE_PRESETS[index] ?? SAMPLE_PRESETS[SAMPLE_PRESETS.length - 1]

    return {
      ...sample,
      title: preset.title,
      subtitle: preset.subtitle,
      description: preset.description,
      tags: preset.tags,
      icon: preset.icon,
      instrument: preset.instrument,
      era: preset.era,
      featured: preset.featured,
    }
  })
}

function buildResultSummary(result: ProductTranscriptionResult): string {
  const { note_count, clef_count, unmatched_count } = result.transcription_summary

  if (unmatched_count <= 2) {
    return `Melodious recognized ${note_count} notes across ${clef_count} clefs with very few symbols flagged for review.`
  }

  if (unmatched_count <= 8) {
    return `Melodious recognized ${note_count} notes across ${clef_count} clefs. A few symbols still deserve a quick review pass.`
  }

  return `Melodious recognized ${note_count} notes across ${clef_count} clefs, but denser passages still warrant review before export.`
}

export function adaptProductSample(sample: DisplaySample | ProductSample): DisplaySample {
  const presetIndex = SAMPLE_PRESETS.findIndex((preset) => preset.title === sample.title)
  const fallbackPreset =
    SAMPLE_PRESETS[presetIndex >= 0 ? presetIndex : 0] ?? SAMPLE_PRESETS[0]

  return {
    ...sample,
    icon: 'icon' in sample ? sample.icon : fallbackPreset.icon,
    instrument: 'instrument' in sample ? sample.instrument : fallbackPreset.instrument,
    era: 'era' in sample ? sample.era : fallbackPreset.era,
    featured: 'featured' in sample ? sample.featured : fallbackPreset.featured,
  }
}

export async function transcribeDisplaySample(sample: DisplaySample): Promise<DisplayTranscriptionResult> {
  const result = await transcribeSample(sample.id)
  return adaptProductTranscriptionResult(result, sample)
}

export async function transcribeDisplayUpload(file: File): Promise<DisplayTranscriptionResult> {
  const result = await transcribeImage(file)
  return adaptProductTranscriptionResult(result)
}

export function adaptProductTranscriptionResult(
  result: ProductTranscriptionResult,
  sample: DisplaySample | ProductSample = result.sample,
): DisplayTranscriptionResult {
  const tone = result.confidence_indicator.tone === 'medium' ? 'moderate' : result.confidence_indicator.tone

  return {
    title: sample.title,
    sampleId: sample.id,
    resultSummary: buildResultSummary(result),
    summary: {
      noteCount: result.transcription_summary.note_count,
      clefCount: result.transcription_summary.clef_count,
      restCount: result.transcription_summary.rest_count,
      reviewCount: result.transcription_summary.unmatched_count,
    },
    confidenceIndicator: {
      tone,
      label: result.confidence_indicator.label,
      message: result.confidence_indicator.message,
      calibrated: result.confidence_indicator.calibrated,
    },
    explainability: {
      state: result.explainability.state === 'available' ? 'available' : 'unavailable',
      title: result.explainability.title,
      message: result.explainability.message,
    },
    downloads: {
      musicxmlReady: result.downloads.musicxml.ready,
      midiReady: result.downloads.midi.ready,
      musicxmlUrl: result.downloads.musicxml.url,
      midiUrl: result.downloads.midi.url,
    },
    audio: {
      playable: result.audio.playable,
      sourceUrl: result.audio.source_url,
    },
  }
}
