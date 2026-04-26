import { useEffect, useState } from 'react'

import {
  AlertCircle,
  ArrowLeft,
  CheckCircle,
  Clock,
  Download,
  Eye,
  FileText,
  Loader2,
  MessageCircle,
  Music2,
  Pause,
  Play,
} from 'lucide-react'
import { AnimatePresence, motion } from 'framer-motion'
import { Link, useParams } from 'react-router-dom'

import { fetchDisplaySamples, transcribeDisplaySample, type DisplaySample, type DisplayTranscriptionResult } from '../data/lovableAdapter'
import { resolveAssetUrl } from '../lib/api'

type WorkspaceState = 'empty' | 'loading' | 'success' | 'error'

const toneStyle = {
  high: {
    bg: 'bg-[hsl(145,30%,95%)]',
    border: 'border-[hsl(145,25%,82%)]',
    icon: CheckCircle,
    color: 'text-[hsl(145,40%,32%)]',
  },
  moderate: {
    bg: 'bg-[hsl(38,50%,95%)]',
    border: 'border-[hsl(38,40%,80%)]',
    icon: AlertCircle,
    color: 'text-[hsl(38,55%,35%)]',
  },
  low: {
    bg: 'bg-[hsl(0,40%,95%)]',
    border: 'border-[hsl(0,35%,82%)]',
    icon: AlertCircle,
    color: 'text-[hsl(0,50%,42%)]',
  },
} as const

const metricLabels = [
  { key: 'noteCount', label: 'Notes recognized', icon: Music2 },
  { key: 'clefCount', label: 'Clefs detected', icon: FileText },
  { key: 'restCount', label: 'Rests detected', icon: Clock },
  { key: 'reviewCount', label: 'Needs review', icon: AlertCircle },
] as const

function Progress({ value }: { value: number }) {
  return (
    <div className="h-1.5 overflow-hidden rounded-full bg-secondary">
      <div
        className="h-full rounded-full bg-primary transition-[width] duration-300"
        style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
      />
    </div>
  )
}

function WorkspaceScorePreview({ title }: { title: string }) {
  return (
    <div className="relative flex h-full w-full flex-col bg-[hsl(var(--card))]">
      <div
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
        }}
      />

      <div className="border-b border-border/50 px-8 pb-4 pt-6">
        <p className="text-center font-display text-lg font-semibold text-foreground/70">{title}</p>
      </div>

      <div className="flex-1 overflow-hidden p-6">
        <svg viewBox="0 0 520 400" className="h-full w-full" xmlns="http://www.w3.org/2000/svg">
          {[50, 58, 66, 74, 82].map((y, i) => (
            <line key={`t1-${i}`} x1="20" y1={y} x2="500" y2={y} stroke="hsl(var(--foreground))" strokeWidth="0.5" opacity="0.2" />
          ))}
          <text x="24" y="78" fontSize="26" fill="hsl(var(--foreground))" opacity="0.35">C</text>
          <text x="55" y="68" fontSize="12" fontWeight="bold" fill="hsl(var(--foreground))" opacity="0.3">3</text>
          <text x="55" y="80" fontSize="12" fontWeight="bold" fill="hsl(var(--foreground))" opacity="0.3">4</text>
          {[
            { x: 85, y: 74 }, { x: 110, y: 66 }, { x: 135, y: 62 }, { x: 165, y: 70 },
            { x: 200, y: 78 }, { x: 225, y: 66 }, { x: 255, y: 58 }, { x: 280, y: 66 },
            { x: 315, y: 74 }, { x: 340, y: 62 }, { x: 370, y: 70 }, { x: 400, y: 58 },
            { x: 430, y: 66 }, { x: 460, y: 74 },
          ].map((note, i) => (
            <g key={`n1-${i}`} opacity="0.4">
              <ellipse cx={note.x} cy={note.y} rx="4.5" ry="3.2" fill="hsl(var(--foreground))" transform={`rotate(-10 ${note.x} ${note.y})`} />
              <line x1={note.x + 4} y1={note.y} x2={note.x + 4} y2={note.y - 22} stroke="hsl(var(--foreground))" strokeWidth="0.8" />
            </g>
          ))}
          {[170, 290, 410].map((x) => (
            <line key={`b1-${x}`} x1={x} y1="50" x2={x} y2="82" stroke="hsl(var(--foreground))" strokeWidth="0.6" opacity="0.2" />
          ))}
          {[100, 108, 116, 124, 132].map((y, i) => (
            <line key={`b1s-${i}`} x1="20" y1={y} x2="500" y2={y} stroke="hsl(var(--foreground))" strokeWidth="0.5" opacity="0.2" />
          ))}
          <text x="24" y="126" fontSize="20" fill="hsl(var(--foreground))" opacity="0.35">F</text>
          {[
            { x: 85, y: 124 }, { x: 135, y: 116 }, { x: 200, y: 120 },
            { x: 255, y: 108 }, { x: 315, y: 124 }, { x: 370, y: 116 }, { x: 430, y: 120 },
          ].map((note, i) => (
            <g key={`n1b-${i}`} opacity="0.35">
              <ellipse cx={note.x} cy={note.y} rx="4.5" ry="3.2" fill="hsl(var(--foreground))" transform={`rotate(-10 ${note.x} ${note.y})`} />
              <line x1={note.x + 4} y1={note.y} x2={note.x + 4} y2={note.y - 20} stroke="hsl(var(--foreground))" strokeWidth="0.8" />
            </g>
          ))}
          <path d="M 22 50 Q 12 91, 22 132" fill="none" stroke="hsl(var(--foreground))" strokeWidth="1.2" opacity="0.25" />

          {[180, 188, 196, 204, 212].map((y, i) => (
            <line key={`t2-${i}`} x1="20" y1={y} x2="500" y2={y} stroke="hsl(var(--foreground))" strokeWidth="0.5" opacity="0.2" />
          ))}
          <text x="24" y="208" fontSize="26" fill="hsl(var(--foreground))" opacity="0.35">C</text>
          {[
            { x: 85, y: 204 }, { x: 115, y: 196 }, { x: 145, y: 188 }, { x: 180, y: 200 },
            { x: 215, y: 208 }, { x: 245, y: 196 }, { x: 280, y: 192 }, { x: 310, y: 200 },
            { x: 345, y: 188 }, { x: 380, y: 196 }, { x: 415, y: 204 }, { x: 450, y: 192 },
          ].map((note, i) => (
            <g key={`n2-${i}`} opacity="0.4">
              <ellipse cx={note.x} cy={note.y} rx="4.5" ry="3.2" fill="hsl(var(--foreground))" transform={`rotate(-10 ${note.x} ${note.y})`} />
              <line x1={note.x + 4} y1={note.y} x2={note.x + 4} y2={note.y - 22} stroke="hsl(var(--foreground))" strokeWidth="0.8" />
            </g>
          ))}
          {[230, 238, 246, 254, 262].map((y, i) => (
            <line key={`b2s-${i}`} x1="20" y1={y} x2="500" y2={y} stroke="hsl(var(--foreground))" strokeWidth="0.5" opacity="0.2" />
          ))}
          <text x="24" y="256" fontSize="20" fill="hsl(var(--foreground))" opacity="0.35">F</text>
          {[
            { x: 85, y: 254 }, { x: 145, y: 246 }, { x: 215, y: 250 },
            { x: 280, y: 238 }, { x: 345, y: 254 }, { x: 415, y: 246 },
          ].map((note, i) => (
            <g key={`n2b-${i}`} opacity="0.35">
              <ellipse cx={note.x} cy={note.y} rx="4.5" ry="3.2" fill="hsl(var(--foreground))" transform={`rotate(-10 ${note.x} ${note.y})`} />
              <line x1={note.x + 4} y1={note.y} x2={note.x + 4} y2={note.y - 20} stroke="hsl(var(--foreground))" strokeWidth="0.8" />
            </g>
          ))}
          <path d="M 22 180 Q 12 221, 22 262" fill="none" stroke="hsl(var(--foreground))" strokeWidth="1.2" opacity="0.25" />

          {[310, 318, 326, 334, 342].map((y, i) => (
            <line key={`t3-${i}`} x1="20" y1={y} x2="500" y2={y} stroke="hsl(var(--foreground))" strokeWidth="0.5" opacity="0.2" />
          ))}
          <text x="24" y="338" fontSize="26" fill="hsl(var(--foreground))" opacity="0.35">C</text>
          {[
            { x: 85, y: 334 }, { x: 120, y: 326 }, { x: 155, y: 318 }, { x: 195, y: 330 },
            { x: 230, y: 338 }, { x: 270, y: 322 }, { x: 310, y: 330 }, { x: 350, y: 318 },
            { x: 390, y: 326 }, { x: 430, y: 334 },
          ].map((note, i) => (
            <g key={`n3-${i}`} opacity="0.4">
              <ellipse cx={note.x} cy={note.y} rx="4.5" ry="3.2" fill="hsl(var(--foreground))" transform={`rotate(-10 ${note.x} ${note.y})`} />
              <line x1={note.x + 4} y1={note.y} x2={note.x + 4} y2={note.y - 22} stroke="hsl(var(--foreground))" strokeWidth="0.8" />
            </g>
          ))}
          {[360, 368, 376, 384, 392].map((y, i) => (
            <line key={`b3s-${i}`} x1="20" y1={y} x2="500" y2={y} stroke="hsl(var(--foreground))" strokeWidth="0.5" opacity="0.2" />
          ))}
          <text x="24" y="386" fontSize="20" fill="hsl(var(--foreground))" opacity="0.35">F</text>
          {[
            { x: 85, y: 384 }, { x: 155, y: 376 }, { x: 230, y: 380 }, { x: 310, y: 372 }, { x: 390, y: 384 },
          ].map((note, i) => (
            <g key={`n3b-${i}`} opacity="0.35">
              <ellipse cx={note.x} cy={note.y} rx="4.5" ry="3.2" fill="hsl(var(--foreground))" transform={`rotate(-10 ${note.x} ${note.y})`} />
              <line x1={note.x + 4} y1={note.y} x2={note.x + 4} y2={note.y - 20} stroke="hsl(var(--foreground))" strokeWidth="0.8" />
            </g>
          ))}
          <path d="M 22 310 Q 12 351, 22 392" fill="none" stroke="hsl(var(--foreground))" strokeWidth="1.2" opacity="0.25" />

          <text x="80" y="148" fontSize="10" fontStyle="italic" fill="hsl(var(--primary))" opacity="0.4">mp</text>
          <text x="270" y="278" fontSize="10" fontStyle="italic" fill="hsl(var(--primary))" opacity="0.4">cresc.</text>
        </svg>
      </div>
    </div>
  )
}

export function WorkspacePage() {
  const { sampleId } = useParams<{ sampleId: string }>()
  const [samples, setSamples] = useState<DisplaySample[]>([])
  const [state, setState] = useState<WorkspaceState>('empty')
  const [result, setResult] = useState<DisplayTranscriptionResult | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [loadingProgress, setLoadingProgress] = useState(0)

  useEffect(() => {
    let isMounted = true

    async function load() {
      const loadedSamples = await fetchDisplaySamples()
      if (isMounted) {
        setSamples(loadedSamples)
      }
    }

    void load()

    return () => {
      isMounted = false
    }
  }, [])

  const sample = samples.find((entry) => entry.id === sampleId)

  async function handleTranscribe() {
    if (!sample) {
      return
    }

    setState('loading')
    setLoadingProgress(0)

    const interval = window.setInterval(() => {
      setLoadingProgress((previous) => {
        if (previous >= 90) {
          window.clearInterval(interval)
          return 90
        }
        return previous + Math.random() * 15 + 5
      })
    }, 300)

    try {
      const loadedResult = await transcribeDisplaySample(sample)
      window.clearInterval(interval)
      setLoadingProgress(100)
      window.setTimeout(() => {
        setResult(loadedResult)
        setState('success')
      }, 400)
    } catch {
      window.clearInterval(interval)
      setState('error')
    }
  }

  if (!sample) {
    return (
      <main className="container mx-auto px-6 py-32 text-center">
        <AlertCircle className="mx-auto mb-6 h-10 w-10 text-muted-foreground" />
        <h1 className="mb-3 font-display text-2xl font-bold text-foreground">Sample not found</h1>
        <p className="mb-8 font-body text-muted-foreground">We couldn't find this piece in our library.</p>
        <Link to="/samples" className="inline-flex items-center gap-2 font-sans text-sm font-medium text-primary hover:underline">
          <ArrowLeft className="h-4 w-4" /> Back to library
        </Link>
      </main>
    )
  }

  return (
    <main className="container mx-auto px-6 py-6 md:py-10">
      <div className="mb-6 flex items-center gap-4">
        <Link
          to="/samples"
          className="inline-flex items-center gap-1.5 font-sans text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Library
        </Link>
        <span className="text-border">|</span>
        <div className="min-w-0 flex-1">
          <h1 className="truncate font-display text-xl font-bold tracking-tight text-foreground md:text-2xl">
            {sample.title}
          </h1>
        </div>
        <span className="hidden font-sans text-xs text-muted-foreground sm:block">
          {sample.subtitle} - {sample.instrument}
        </span>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <div
            className="sticky top-20 overflow-hidden rounded-xl border border-border bg-card shadow-sm"
            style={{ minHeight: '480px' }}
          >
            <WorkspaceScorePreview title={sample.title} />
          </div>
        </div>

        <div className="space-y-4 lg:col-span-2">
          <AnimatePresence mode="wait">
            {state === 'empty' ? (
              <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
                <div className="rounded-xl border border-border bg-card p-6">
                  <h3 className="mb-2 font-display text-base font-semibold text-foreground">Ready to transcribe</h3>
                  <p className="mb-5 font-body text-sm leading-relaxed text-muted-foreground">
                    Melodious will read this score and produce a digital version you can play back and export.
                  </p>
                  <button
                    onClick={handleTranscribe}
                    className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-8 py-3 font-sans text-sm font-semibold text-primary-foreground shadow-sm transition-opacity hover:opacity-90"
                  >
                    Transcribe this score
                  </button>
                </div>

                <div className="rounded-xl border border-border bg-card p-5">
                  <div className="mb-2 flex items-center gap-2">
                    <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                    <h3 className="font-sans text-xs font-medium text-foreground/70">About this piece</h3>
                  </div>
                  <p className="mb-2 font-body text-sm leading-relaxed text-muted-foreground">{sample.description}</p>
                  <div className="flex flex-wrap gap-1.5">
                    <span className="rounded-full bg-accent px-2.5 py-0.5 text-[11px] font-sans font-medium text-foreground/60">{sample.instrument}</span>
                    <span className="rounded-full bg-accent px-2.5 py-0.5 text-[11px] font-sans font-medium text-foreground/60">{sample.era}</span>
                    {sample.tags.map((tag) => (
                      <span key={tag} className="rounded-full bg-accent px-2 py-0.5 text-[11px] font-sans text-muted-foreground">{tag}</span>
                    ))}
                  </div>
                </div>

                <div className="rounded-xl border border-border bg-card p-5">
                  <div className="mb-2 flex items-center gap-2">
                    <Download className="h-3.5 w-3.5 text-muted-foreground" />
                    <h3 className="font-sans text-xs font-medium text-foreground/70">What you'll get</h3>
                  </div>
                  <ul className="space-y-1.5 font-body text-sm text-muted-foreground">
                    <li className="flex items-center gap-2"><CheckCircle className="h-3 w-3 text-muted-foreground/50" /> MusicXML file for notation software</li>
                    <li className="flex items-center gap-2"><CheckCircle className="h-3 w-3 text-muted-foreground/50" /> MIDI file for playback and editing</li>
                    <li className="flex items-center gap-2"><CheckCircle className="h-3 w-3 text-muted-foreground/50" /> Confidence and quality summary</li>
                  </ul>
                </div>
              </motion.div>
            ) : null}

            {state === 'loading' ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="rounded-xl border border-border bg-card p-6"
              >
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                    <Loader2 className="h-4 w-4 animate-spin text-primary" />
                  </div>
                  <div>
                    <h3 className="font-display text-base font-semibold text-foreground">Transcribing...</h3>
                    <p className="font-body text-xs text-muted-foreground">Reading the score and recognizing symbols</p>
                  </div>
                </div>
                <Progress value={loadingProgress} />
              </motion.div>
            ) : null}

            {state === 'error' ? (
              <motion.div
                key="error"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="rounded-xl border border-destructive/30 bg-card p-6 text-center"
              >
                <AlertCircle className="mx-auto mb-3 h-7 w-7 text-destructive" />
                <h3 className="mb-1.5 font-display text-base font-semibold text-foreground">Something went wrong</h3>
                <p className="mb-5 font-body text-sm text-muted-foreground">We couldn't complete the transcription.</p>
                <button
                  onClick={handleTranscribe}
                  className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 font-sans text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
                >
                  Try again
                </button>
              </motion.div>
            ) : null}

            {state === 'success' && result ? (
              <motion.div
                key="success"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="space-y-3"
              >
                <div className="rounded-xl border border-border bg-card p-5">
                  <div className="flex items-start gap-3">
                    <CheckCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-[hsl(var(--success))]" />
                    <p className="font-body text-sm leading-relaxed text-foreground">{result.resultSummary}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  {metricLabels.map(({ key, label, icon: Icon }) => (
                    <div key={key} className="rounded-xl border border-border bg-card p-3.5">
                      <div className="mb-0.5 flex items-center gap-1.5">
                        <Icon className="h-3 w-3 text-muted-foreground" />
                        <span className="font-sans text-[11px] text-muted-foreground">{label}</span>
                      </div>
                      <span className="font-display text-xl font-bold text-foreground">
                        {result.summary[key]}
                      </span>
                    </div>
                  ))}
                </div>

                <div className="rounded-xl border border-border bg-card p-5">
                  <h3 className="mb-3 font-display text-sm font-semibold">Playback</h3>
                  {result.audio.playable ? (
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => setIsPlaying(!isPlaying)}
                        className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-sm transition-opacity hover:opacity-90"
                      >
                        {isPlaying ? <Pause className="h-3.5 w-3.5" /> : <Play className="ml-0.5 h-3.5 w-3.5" />}
                      </button>
                      <div className="flex-1">
                        <div className="h-1.5 overflow-hidden rounded-full bg-secondary">
                          <div className="h-full w-1/3 rounded-full bg-primary" />
                        </div>
                        <p className="mt-1 font-sans text-[11px] text-muted-foreground">0:00 / 2:34</p>
                      </div>
                    </div>
                  ) : (
                    <p className="font-body text-sm text-muted-foreground">Playback not available for this piece.</p>
                  )}
                </div>

                <div className="rounded-xl border border-border bg-card p-5">
                  <h3 className="mb-3 font-display text-sm font-semibold">Downloads</h3>
                  <div className="flex gap-3">
                    <a
                      href={resolveAssetUrl(result.downloads.musicxmlUrl)}
                      className={`flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg px-4 py-2.5 font-sans text-xs font-medium ${
                        result.downloads.musicxmlReady
                          ? 'bg-primary text-primary-foreground shadow-sm transition-opacity hover:opacity-90'
                          : 'cursor-not-allowed bg-card text-foreground opacity-40'
                      }`}
                    >
                      <Download className="h-3.5 w-3.5" /> MusicXML
                    </a>
                    <a
                      href={resolveAssetUrl(result.downloads.midiUrl)}
                      className={`flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg border px-4 py-2.5 font-sans text-xs font-medium ${
                        result.downloads.midiReady
                          ? 'border-border bg-card text-foreground transition-colors hover:bg-accent'
                          : 'cursor-not-allowed border-border bg-card text-foreground opacity-40'
                      }`}
                    >
                      <Download className="h-3.5 w-3.5" /> MIDI
                    </a>
                  </div>
                </div>

                {(() => {
                  const tone = toneStyle[result.confidenceIndicator.tone]
                  const ToneIcon = tone.icon
                  return (
                    <div className={`rounded-xl border p-5 ${tone.bg} ${tone.border}`}>
                      <div className="mb-1.5 flex items-center gap-2">
                        <ToneIcon className={`h-3.5 w-3.5 ${tone.color}`} />
                        <h3 className={`font-display text-sm font-semibold ${tone.color}`}>
                          {result.confidenceIndicator.label}
                        </h3>
                      </div>
                      <p className="font-body text-xs leading-relaxed text-foreground/60">
                        {result.confidenceIndicator.message}
                      </p>
                    </div>
                  )
                })()}

                <div className="rounded-xl border border-border/50 bg-card p-4 opacity-60">
                  <div className="mb-1 flex items-center gap-2">
                    <Eye className="h-3.5 w-3.5 text-muted-foreground" />
                    <h3 className="font-sans text-xs font-medium text-muted-foreground">{result.explainability.title}</h3>
                    <span className="ml-auto rounded-full bg-accent px-2 py-0.5 font-sans text-[10px] text-muted-foreground">
                      Future upgrade
                    </span>
                  </div>
                  <p className="font-body text-[11px] leading-relaxed text-muted-foreground">
                    {result.explainability.message}
                  </p>
                </div>

                <div className="rounded-xl border border-border/50 bg-card p-4 opacity-60">
                  <div className="mb-1 flex items-center gap-2">
                    <MessageCircle className="h-3.5 w-3.5 text-muted-foreground" />
                    <h3 className="font-sans text-xs font-medium text-muted-foreground">Ask Melodious</h3>
                    <span className="ml-auto rounded-full bg-accent px-2 py-0.5 font-sans text-[10px] text-muted-foreground">
                      Coming soon
                    </span>
                  </div>
                  <p className="font-body text-[11px] leading-relaxed text-muted-foreground">
                    Have questions about this piece? Soon you'll be able to ask about key changes, articulations, and more.
                  </p>
                </div>
              </motion.div>
            ) : null}
          </AnimatePresence>
        </div>
      </div>
    </main>
  )
}
