import { useState } from 'react'

import {
  AlignCenter,
  AlertCircle,
  Camera,
  CheckCircle,
  EyeOff,
  FileImage,
  FileText,
  Info,
  Lightbulb,
  Maximize,
  Sun,
  Upload as UploadIcon,
  X,
} from 'lucide-react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

import { supportedFormats } from '../data/lovableAdapter'
import { useIsMobile } from '../hooks/use-mobile'

type InputMode = 'upload' | 'camera'
type UploadState = 'idle' | 'drag-active' | 'file-selected' | 'unsupported' | 'error'
type CameraState = 'idle' | 'preview'

const tips = [
  { icon: Sun, title: 'Good lighting', description: 'Use even, bright lighting without harsh shadows across the page.' },
  { icon: Maximize, title: 'Keep it flat', description: 'Lay the page flat on a surface - avoid curled edges or folds.' },
  { icon: EyeOff, title: 'Avoid shadows', description: "Make sure your hand or phone doesn't cast a shadow on the score." },
  { icon: AlignCenter, title: 'Keep it straight', description: 'Align the page squarely in the frame for the best read.' },
]

export function UploadPage() {
  const isMobile = useIsMobile()
  const [mode, setMode] = useState<InputMode>('upload')
  const [uploadState, setUploadState] = useState<UploadState>('idle')
  const [cameraState, setCameraState] = useState<CameraState>('idle')
  const [fileName, setFileName] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  const isSupported = (name: string) => {
    const extension = name.split('.').pop()?.toUpperCase() ?? ''
    return supportedFormats.includes(extension)
  }

  const handleFile = (file: File) => {
    setFileName(file.name)

    if (isSupported(file.name)) {
      setUploadState('file-selected')
    } else {
      setUploadState('unsupported')
      setErrorMessage(`"${file.name}" is not a supported format. Please use PDF, PNG, JPG, or TIFF.`)
    }
  }

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault()
    const file = event.dataTransfer.files[0]
    if (file) {
      handleFile(file)
    }
  }

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault()
    setUploadState('drag-active')
  }

  const handleDragLeave = () => {
    setUploadState('idle')
  }

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      handleFile(file)
    }
  }

  const resetUpload = () => {
    setUploadState('idle')
    setFileName('')
    setErrorMessage('')
  }

  const resetCamera = () => {
    setCameraState('idle')
  }

  return (
    <main className="container mx-auto px-6 py-12 md:py-20">
      <div className="mx-auto max-w-2xl">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="mb-2 font-display text-3xl font-bold tracking-tight text-foreground md:text-4xl">
            Bring in your score
          </h1>
          <p className="max-w-lg font-body text-base text-muted-foreground">
            Upload a file or take a photo of your sheet music. Melodious will read it and produce a digital transcription.
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

        {mode === 'upload' ? (
          <motion.div key="upload" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              className={`relative rounded-xl border-2 border-dashed p-12 text-center transition-all ${
                uploadState === 'drag-active'
                  ? 'border-primary bg-primary/5'
                  : uploadState === 'file-selected'
                    ? 'border-[hsl(var(--success))] bg-[hsl(145,30%,97%)]'
                    : uploadState === 'unsupported' || uploadState === 'error'
                      ? 'border-destructive/50 bg-destructive/5'
                      : 'border-border bg-card hover:border-primary/40'
              }`}
            >
              {uploadState === 'idle' || uploadState === 'drag-active' ? (
                <>
                  <UploadIcon
                    className={`mx-auto mb-4 h-10 w-10 ${uploadState === 'drag-active' ? 'text-primary' : 'text-muted-foreground'}`}
                  />
                  <p className="mb-1 font-display text-lg font-semibold text-foreground">
                    {uploadState === 'drag-active' ? 'Drop your file here' : 'Drag & drop your score'}
                  </p>
                  <p className="mb-4 font-body text-sm text-muted-foreground">or choose a file from your device</p>
                  <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg bg-primary px-6 py-2.5 font-sans text-sm font-semibold text-primary-foreground shadow-sm transition-opacity hover:opacity-90">
                    <FileImage className="h-4 w-4" />
                    Choose file
                    <input
                      type="file"
                      className="hidden"
                      accept=".pdf,.png,.jpg,.jpeg,.tiff"
                      onChange={handleInputChange}
                    />
                  </label>
                  <p className="mt-4 font-sans text-xs text-muted-foreground">
                    Supported: {supportedFormats.join(', ')}
                  </p>
                </>
              ) : uploadState === 'file-selected' ? (
                <>
                  <CheckCircle className="mx-auto mb-4 h-10 w-10 text-[hsl(var(--success))]" />
                  <p className="mb-1 font-display text-lg font-semibold text-foreground">File selected</p>
                  <div className="mb-5 flex items-center justify-center gap-2 font-sans text-sm text-muted-foreground">
                    <FileText className="h-4 w-4" />
                    {fileName}
                    <button onClick={resetUpload} className="text-muted-foreground transition-colors hover:text-foreground">
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="inline-flex items-center gap-3 rounded-lg border border-border bg-card px-5 py-3">
                    <Info className="h-4 w-4 flex-shrink-0 text-primary" />
                    <div className="text-left">
                      <p className="font-sans text-sm font-medium text-foreground">Upload processing is in development</p>
                      <p className="font-body text-xs text-muted-foreground">
                        This feature is coming soon. For now, try one of our{' '}
                        <Link to="/samples" className="text-primary hover:underline">
                          sample scores
                        </Link>
                        .
                      </p>
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <AlertCircle className="mx-auto mb-4 h-10 w-10 text-destructive" />
                  <p className="mb-1 font-display text-lg font-semibold text-foreground">Unsupported file</p>
                  <p className="mb-4 font-body text-sm text-muted-foreground">{errorMessage}</p>
                  <button
                    onClick={resetUpload}
                    className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 font-sans text-sm font-semibold text-primary-foreground shadow-sm transition-opacity hover:opacity-90"
                  >
                    Try another file
                  </button>
                </>
              )}
            </div>
          </motion.div>
        ) : (
          <motion.div key="camera" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            {cameraState === 'idle' ? (
              <div className="overflow-hidden rounded-xl border border-border bg-card">
                <div className="relative aspect-[4/3] bg-foreground/5 flex items-center justify-center">
                  <div className="absolute inset-6 rounded-lg border-2 border-dashed border-primary/25" />
                  <div className="text-center">
                    <Camera className="mx-auto mb-3 h-12 w-12 text-muted-foreground" />
                    <p className="mb-1 font-display font-semibold text-foreground">
                      {isMobile ? 'Position your score' : 'Camera capture'}
                    </p>
                    <p className="mx-auto max-w-xs font-body text-sm text-muted-foreground">
                      {isMobile
                        ? 'Align the page within the frame, then tap capture'
                        : 'Open Melodious on your phone for the best camera experience'}
                    </p>
                  </div>
                </div>
                <div className="p-5">
                  <button
                    onClick={() => setCameraState('preview')}
                    className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-6 py-3 font-sans text-sm font-semibold text-primary-foreground shadow-sm transition-opacity hover:opacity-90"
                  >
                    <Camera className="h-4 w-4" />
                    {isMobile ? 'Capture' : 'Take a photo'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="rounded-xl border border-border bg-card p-8 text-center">
                <Info className="mx-auto mb-3 h-8 w-8 text-primary" />
                <h2 className="mb-1 font-display text-lg font-semibold text-foreground">Camera capture is in development</h2>
                <p className="mx-auto mb-5 max-w-sm font-body text-sm text-muted-foreground">
                  This feature is coming soon. For now, try uploading a file or start with a sample score.
                </p>
                <div className="flex flex-col justify-center gap-2 sm:flex-row">
                  <button
                    onClick={() => {
                      resetCamera()
                      setMode('upload')
                    }}
                    className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-6 py-2.5 font-sans text-sm font-semibold text-primary-foreground shadow-sm transition-opacity hover:opacity-90"
                  >
                    <UploadIcon className="h-4 w-4" /> Upload a file
                  </button>
                  <Link
                    to="/samples"
                    className="inline-flex items-center justify-center gap-2 rounded-lg border border-border px-6 py-2.5 font-sans text-sm font-medium text-foreground transition-colors hover:bg-accent"
                  >
                    Try a sample
                  </Link>
                </div>
              </div>
            )}
          </motion.div>
        )}

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
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
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
