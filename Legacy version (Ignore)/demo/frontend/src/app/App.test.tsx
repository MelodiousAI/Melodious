import { render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import App from './App'

const configResponse = {
  app_name: 'Melodious',
  stage: 'v0.5',
  active_experience: 'sample_first',
  upload_status_message: 'Upload is coming later.',
  feature_flags: {
    image_upload_enabled: false,
    attention_overlay_enabled: false,
    llm_explainer_enabled: false,
  },
}

const samplesResponse = {
  items: [
    {
      id: 'CVC-MUSCIMA_W-01_N-10_D-ideal',
      title: 'Handwritten Study 10',
      subtitle: 'Writer 01 · MUSCIMA++ sample',
      document_name: 'CVC-MUSCIMA_W-01_N-10_D-ideal',
      preview_image_url: '/product/samples/CVC-MUSCIMA_W-01_N-10_D-ideal/image',
      description: 'A demo sample.',
      tags: ['Handwritten', 'MUSCIMA++', 'Demo'],
    },
  ],
}

const transcriptionResponse = {
  sample: samplesResponse.items[0],
  score_preview: {
    image_url: '/product/samples/CVC-MUSCIMA_W-01_N-10_D-ideal/image',
    alt_text: 'Preview image for Handwritten Study 10',
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
    message: 'Qualitative only.',
    calibrated: false,
  },
  explainability: {
    state: 'placeholder',
    title: 'Attention Overlay',
    message: 'Reserved for later.',
  },
  downloads: {
    musicxml: {
      ready: true,
      url: '/product/samples/CVC-MUSCIMA_W-01_N-10_D-ideal/downloads/musicxml',
      file_name: 'sample.musicxml',
      content_type: 'application/vnd.recordare.musicxml+xml',
    },
    midi: {
      ready: true,
      url: '/product/samples/CVC-MUSCIMA_W-01_N-10_D-ideal/downloads/midi',
      file_name: 'sample.mid',
      content_type: 'audio/midi',
    },
  },
  audio: {
    playable: true,
    source_url: '/product/samples/CVC-MUSCIMA_W-01_N-10_D-ideal/downloads/midi',
    format: 'midi',
    message: 'Playback ready.',
  },
  feature_flags: configResponse.feature_flags,
  notices: [],
}

describe('App', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('renders the sample-first experience and shows transcription results', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)

      if (url.endsWith('/product/config')) {
        return new Response(JSON.stringify(configResponse), { status: 200 })
      }

      if (url.endsWith('/product/samples')) {
        return new Response(JSON.stringify(samplesResponse), { status: 200 })
      }

      if (url.endsWith('/product/transcribe') && init?.method === 'POST') {
        return new Response(JSON.stringify(transcriptionResponse), { status: 200 })
      }

      return new Response(JSON.stringify({ message: 'not found' }), { status: 404 })
    })

    vi.stubGlobal('fetch', fetchMock)

    window.history.pushState({}, '', '/workspace/CVC-MUSCIMA_W-01_N-10_D-ideal')

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText(/Ready to transcribe/i)).toBeInTheDocument()
    })

    expect(screen.getAllByText(/Nocturne in E-flat Major/i).length).toBeGreaterThan(0)
    expect(screen.getByText(/About this piece/i)).toBeInTheDocument()

    screen.getByRole('button', { name: /Transcribe this score/i }).click()

    await waitFor(() => {
    expect(screen.getByText(/Promising preview/i)).toBeInTheDocument()
  })

    expect(screen.getByText(/MusicXML/i)).toBeInTheDocument()
    expect(screen.getByText(/^MIDI$/i)).toBeInTheDocument()
    expect(screen.getByText(/Ask Melodious/i)).toBeInTheDocument()
  })
})
