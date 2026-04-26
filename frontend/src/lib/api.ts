import { mockConfig, mockSamples, mockTranscriptionResult } from '../mocks/product'
import type {
  ProductConfig,
  ProductSamplesResponse,
  ProductTranscriptionResult,
} from '../types/product'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '')

function withBaseUrl(path: string): string {
  if (/^https?:\/\//.test(path)) {
    return path
  }

  return `${API_BASE_URL}${path}`
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(withBaseUrl(path), init)

  if (!response.ok) {
    throw new Error(`Request failed for ${path}: ${response.status}`)
  }

  return response.json() as Promise<T>
}

export function resolveAssetUrl(path: string): string {
  return withBaseUrl(path)
}

export async function fetchProductConfig(): Promise<ProductConfig> {
  try {
    return await requestJson<ProductConfig>('/product/config')
  } catch {
    return mockConfig
  }
}

export async function fetchProductSamples(): Promise<ProductSamplesResponse> {
  try {
    return await requestJson<ProductSamplesResponse>('/product/samples')
  } catch {
    return { items: mockSamples }
  }
}

export async function transcribeSample(sampleId: string): Promise<ProductTranscriptionResult> {
  try {
    return await requestJson<ProductTranscriptionResult>('/product/transcribe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ sample_id: sampleId }),
    })
  } catch {
    const selectedSample =
      mockSamples.find((sample) => sample.id === sampleId) ?? mockTranscriptionResult.sample

    return {
      ...mockTranscriptionResult,
      sample: selectedSample,
      score_preview: {
        image_url: selectedSample.preview_image_url,
        alt_text: `Preview image for ${selectedSample.title}`,
      },
    }
  }
}

export async function transcribeImage(file: File): Promise<ProductTranscriptionResult> {
  const formData = new FormData()
  formData.append('file', file)

  return requestJson<ProductTranscriptionResult>('/product/transcribe-image', {
    method: 'POST',
    body: formData,
  })
}
