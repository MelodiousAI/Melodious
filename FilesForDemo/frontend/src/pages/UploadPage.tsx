import { useEffect, useMemo, useRef, useState } from 'react'

import {
  AlignCenter,
  AlertCircle,
  BarChart3,
  Camera,
  CheckCircle,
  EyeOff,
  FileImage,
  Info,
  Lightbulb,
  Loader2,
  Maximize,
  Music2,
  Sun,
  Upload as UploadIcon,
  X,
} from 'lucide-react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

import { classifyScoreImage } from '../lib/api'
import { useIsMobile } from '../hooks/use-mobile'
import type { ProductImageClassificationResult } from '../types/product'

type InputMode = 'upload' | 'camera'
type UploadState = 'idle' | 'drag-active' | 'processing' | 'result' | 'unsupported' | 'error'

const supportedImageFormats = ['PNG', 'JPG', 'JPEG', 'TIFF']

const tips = [
  { icon: Sun, title: 'Good lighting', description: 'Use even, bright lighting without harsh shadows across the page.' },
  { icon: Maximize, title: 'Keep it flat', description: 'Lay the page flat on a surface and avoid curled edges or folds.' },
  { icon: EyeOff, title: 'Avoid shadows', description: "Make sure your hand or phone does not cast a shadow on the score." },
  { icon: AlignCenter, title: 'Keep it straight', description: 'Align the page squarely in the frame for the best read.' },
]

function formatConfidence(value: number): string {
  return `${Math.round(value * 100)}%`
}

export function UploadPage() {
  const isMobile = useIsMobile()
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const cameraInputRef = useRef<HTMLInputElement | null>(null)
  const [mode, setMode] = useState<InputMode>('upload')
  const [uploadState, setUploadState] = useState<UploadState>('idle')
  const [fileName, setFileName] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [previewUrl, setPreviewUrl] = useState('')
  const [result, setResult] = useState<ProductImageClassificationResult | null>(null)

  const topClasses = useMemo(() => result?.class_counts.slice(0, 8) ?? [], [result])
  const overlayDetections = useMemo(() => result?.detections.slice(0, 40) ?? [], [result])

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  const isSupported = (file: File) => {
    const extension = file.name.split('.').pop()?.toUpperCase() ?? ''
    return file.type.startsWith('image/') && supportedImageFormats.includes(extension)
  }

  const resetUpload = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }
    setUploadState('idle')
    setFileName('')
    setErrorMessage('')
    setPreviewUrl('')
    setResult(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    if (cameraInputRef.current) {
      cameraInputRef.current.value = ''
    }
  }

  const handleFile = async (file: File) => {
    setFileName(file.name)
    setErrorMessage('')
    setResult(null)

    if (!isSupported(file)) {
      setUploadState('unsupported')
      setErrorMessage(`"${file.name}" is not supported. Use PNG, JPG, JPEG, or TIFF for live detector mode.`)
      return
    }

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }

    setPreviewUrl(URL.createObjectURL(file))
    setUploadState('processing')

    try {
      const classification = await classifyScoreImage(file)
      setResult(classification)
      setUploadState('result')
    } catch (error) {
      setUploadState('error')
      setErrorMessage(error instanceof Error ? error.message : 'The detector could not process this image.')
    }
  }

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault()
    const file = event.dataTransfer.files[0]
    if (file) {
      void handleFile(file)
    }
  }

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault()
    if (uploadState !== 'processing') {
      setUploadState('drag-active')
    }
  }

  const handleDragLeave = () => {
    if (uploadState === 'drag-active') {
      setUploadState('idle')
    }
  }

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      void handleFile(file)
    }
  }

  return (
    <main className="container mx-auto px-6 py-12 md:py-20">
      <div className="mx-auto max-w-5xl">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="mb-2 font-display text-3xl font-bold tracking-tight text-foreground md:text-4xl">
            Classify your score
          </h1>
          <p className="max-w-2xl font-body text-base text-muted-foreground">
            Upload a score image or take a photo on your phone. Melodious runs the packaged YOLOv8 detector and returns
            detected music symbols with confidence scores.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05, duration: 0.5 }}
          className="mb-6"
        >
          <div className="inline-flex gap-1 rounded-lg bg-accent p-1">
            <button
              onClick={() => setMode('upload')}
              className={`inline-flex items-center gap-2 rounded-md px-5 py-2 text-sm font-sans font-medium transition-all ${
                mode === 'upload'
                  ? 'bg-card text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <UploadIcon className="h-4 w-4" />
              Upload file
            </button>
            <button
              onClick={() => setMode('camera')}
              className={`inline-flex items-center gap-2 rounded-md px-5 py-2 text-sm font-sans font-medium transition-all ${
                mode === 'camera'
                  ? 'bg-card text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Camera className="h-4 w-4" />
              Take a picture
            </button>
          </div>
        </motion.div>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.25fr)_minmax(320px,0.75fr)]">
          <motion.section
            key={mode}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="rounded-xl border border-border bg-card"
          >
            <div
              onDrop={mode === 'upload' ? handleDrop : undefined}
              onDragOver={mode === 'upload' ? handleDragOver : undefined}
              onDragLeave={mode === 'upload' ? handleDragLeave : undefined}
              className={`relative min-h-[420px] overflow-hidden rounded-xl border-2 border-dashed p-6 transition-all ${
                uploadState === 'drag-active'
                  ? 'border-primary bg-primary/5'
                  : uploadState === 'result'
                    ? 'border-[hsl(var(--success))] bg-[hsl(145,30%,97%)]'
                    : uploadState === 'unsupported' || uploadState === 'error'
                      ? 'border-destructive/50 bg-destructive/5'
                      : 'border-border bg-card'
              }`}
            >
              {previewUrl ? (
                <div className="relative mx-auto max-h-[620px] max-w-full overflow-hidden rounded-lg border border-border bg-white">
                  <img src={previewUrl} alt={`Uploaded score ${fileName}`} className="block w-full object-contain" />
                  {uploadState === 'result'
                    ? overlayDetections.map((detection, index) => {
                        const { bbox } = detection
                        return (
                          <div
                            key={`${detection.class_name}-${index}`}
                            className="absolute border-2 border-primary/85 bg-primary/10"
                            style={{
                              left: `${(bbox.x_center - bbox.width / 2) * 100}%`,
                              top: `${(bbox.y_center - bbox.height / 2) * 100}%`,
                              width: `${bbox.width * 100}%`,
                              height: `${bbox.height * 100}%`,
                            }}
                            title={`${detection.class_name} ${formatConfidence(detection.confidence)}`}
                          />
                        )
                      })
                    : null}
                </div>
              ) : (
                <div className="flex min-h-[360px] flex-col items-center justify-center text-center">
                  {mode === 'upload' ? (
                    <UploadIcon
                      className={`mb-4 h-12 w-12 ${uploadState === 'drag-active' ? 'text-primary' : 'text-muted-foreground'}`}
                    />
                  ) : (
                    <Camera className="mb-4 h-12 w-12 text-muted-foreground" />
                  )}
                  <p className="mb-1 font-display text-lg font-semibold text-foreground">
                    {mode === 'upload'
                      ? uploadState === 'drag-active'
                        ? 'Drop your image here'
                        : 'Choose a score image'
                      : isMobile
                        ? 'Open your camera'
                        : 'Use a phone or choose a photo'}
                  </p>
                  <p className="mb-5 max-w-sm font-body text-sm text-muted-foreground">
                    {mode === 'upload'
                      ? 'The detector supports PNG, JPG, JPEG, and TIFF images.'
                      : 'On a phone, this button opens the camera so you can capture a score and classify it.'}
                  </p>
                  {mode === 'upload' ? (
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 font-sans text-sm font-semibold text-primary-foreground shadow-sm transition-opacity hover:opacity-90"
                    >
                      <FileImage className="h-4 w-4" />
                      Choose image
                    </button>
                  ) : (
                    <button
                      onClick={() => cameraInputRef.current?.click()}
                      className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 font-sans text-sm font-semibold text-primary-foreground shadow-sm transition-opacity hover:opacity-90"
                    >
                      <Camera className="h-4 w-4" />
                      Take photo and classify
                    </button>
                  )}
                </div>
              )}

              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".png,.jpg,.jpeg,.tiff,image/png,image/jpeg,image/tiff"
                onChange={handleInputChange}
              />
              <input
                ref={cameraInputRef}
                type="file"
                className="hidden"
                accept="image/*"
                capture="environment"
                onChange={handleInputChange}
              />
            </div>

            <div className="flex flex-col gap-3 border-t border-border p-5 sm:flex-row sm:items-center sm:justify-between">
              <div className="min-w-0">
                <p className="truncate font-sans text-sm font-medium text-foreground">
                  {fileName || 'No image selected'}
                </p>
                <p className="font-body text-xs text-muted-foreground">
                  Detector mode returns symbol classes only. Use samples for MusicXML/MIDI export.
                </p>
              </div>
              <button
                onClick={resetUpload}
                disabled={uploadState === 'processing' && !previewUrl}
                className="inline-flex items-center justify-center gap-2 rounded-lg border border-border px-4 py-2 font-sans text-sm font-medium text-foreground transition-colors hover:bg-accent disabled:cursor-not-allowed disabled:opacity-50"
              >
                <X className="h-4 w-4" />
                Reset
              </button>
            </div>
          </motion.section>

          <motion.aside
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08, duration: 0.3 }}
            className="space-y-4"
          >
            <section className="rounded-xl border border-border bg-card p-5">
              <div className="mb-3 flex items-center gap-2">
                {uploadState === 'processing' ? (
                  <Loader2 className="h-5 w-5 animate-spin text-primary" />
                ) : uploadState === 'result' ? (
                  <CheckCircle className="h-5 w-5 text-[hsl(var(--success))]" />
                ) : uploadState === 'error' || uploadState === 'unsupported' ? (
                  <AlertCircle className="h-5 w-5 text-destructive" />
                ) : (
                  <Music2 className="h-5 w-5 text-primary" />
                )}
                <h2 className="font-display text-lg font-semibold text-foreground">Detector result</h2>
              </div>

              {uploadState === 'processing' ? (
                <p className="font-body text-sm leading-6 text-muted-foreground">
                  Loading the YOLOv8 model and classifying your score image. The first run can take a little longer.
                </p>
              ) : uploadState === 'result' && result ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-lg border border-border bg-background p-3">
                      <p className="font-sans text-xs text-muted-foreground">Detections</p>
                      <p className="font-display text-2xl font-semibold text-foreground">{result.detection_count}</p>
                    </div>
                    <div className="rounded-lg border border-border bg-background p-3">
                      <p className="font-sans text-xs text-muted-foreground">Classes</p>
                      <p className="font-display text-2xl font-semibold text-foreground">{result.class_counts.length}</p>
                    </div>
                  </div>

                  <div>
                    <div className="mb-2 flex items-center gap-2">
                      <BarChart3 className="h-4 w-4 text-primary" />
                      <p className="font-sans text-sm font-semibold text-foreground">Top classes</p>
                    </div>
                    <div className="space-y-2">
                      {topClasses.map((item) => (
                        <div key={item.class_name} className="flex items-center justify-between rounded-lg bg-accent/60 px-3 py-2">
                          <span className="font-sans text-sm text-foreground">{item.class_name}</span>
                          <span className="font-sans text-sm font-semibold text-foreground">{item.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <p className="mb-2 font-sans text-sm font-semibold text-foreground">Highest-confidence symbols</p>
                    <div className="max-h-64 space-y-2 overflow-auto pr-1">
                      {result.detections.slice(0, 12).map((detection, index) => (
                        <div key={`${detection.class_name}-${index}`} className="flex items-center justify-between rounded-lg border border-border px-3 py-2">
                          <span className="font-sans text-sm text-foreground">{detection.class_name}</span>
                          <span className="font-sans text-sm font-semibold text-primary">{formatConfidence(detection.confidence)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : uploadState === 'error' || uploadState === 'unsupported' ? (
                <p className="font-body text-sm leading-6 text-destructive">{errorMessage}</p>
              ) : (
                <p className="font-body text-sm leading-6 text-muted-foreground">
                  Select an image or take a photo to run live symbol detection with the packaged model.
                </p>
              )}
            </section>

            {result?.notices.length ? (
              <section className="rounded-xl border border-amber-200 bg-amber-50/90 p-4">
                <div className="mb-2 flex items-center gap-2">
                  <Info className="h-4 w-4 text-amber-700" />
                  <h3 className="font-sans text-sm font-semibold text-amber-950">Demo note</h3>
                </div>
                <ul className="space-y-2">
                  {result.notices.map((notice) => (
                    <li key={notice} className="font-body text-xs leading-5 text-amber-900">
                      {notice}
                    </li>
                  ))}
                </ul>
                <Link to="/samples" className="mt-3 inline-block font-sans text-xs font-semibold text-primary hover:underline">
                  Open sample transcription flow
                </Link>
              </section>
            ) : null}
          </motion.aside>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.5 }}
          className="mt-8"
        >
          <div className="mb-4 flex items-center gap-2">
            <Lightbulb className="h-4 w-4 text-primary" />
            <h2 className="font-display text-base font-semibold text-foreground">Tips for best results</h2>
          </div>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {tips.map((tip) => {
              const TipIcon = tip.icon
              return (
                <div key={tip.title} className="flex items-start gap-3 rounded-xl border border-border bg-card p-4">
                  <TipIcon className="mt-0.5 h-4 w-4 flex-shrink-0 text-primary/60" />
                  <div>
                    <h3 className="mb-0.5 font-sans text-sm font-medium text-foreground">{tip.title}</h3>
                    <p className="font-body text-xs leading-relaxed text-muted-foreground">{tip.description}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </motion.div>
      </div>
    </main>
  )
}
