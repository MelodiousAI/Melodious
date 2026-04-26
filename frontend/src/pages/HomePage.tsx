import { ArrowRight, FileText, Headphones, Music, Upload } from 'lucide-react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

const steps = [
  {
    icon: Music,
    title: 'Choose a score',
    description: 'Pick from our curated library or upload your own sheet music - PDF, image, or photo.',
  },
  {
    icon: FileText,
    title: 'Melodious transcribes it',
    description: 'Our model reads the notation - notes, rests, clefs, dynamics - and produces a clean digital version.',
  },
  {
    icon: Headphones,
    title: 'Listen, review, export',
    description: 'Play it back, inspect the results, and download as MusicXML or MIDI.',
  },
]

const waysToStart = [
  {
    icon: Music,
    title: 'Try a sample',
    description: 'Start with a curated piece from our library - no upload needed.',
    to: '/samples',
    iconBg: 'bg-primary/10',
    iconColor: 'text-primary',
    gradient: 'bg-gradient-to-br from-card to-[hsl(38,50%,93%)]',
  },
  {
    icon: Upload,
    title: 'Upload a score',
    description: 'Bring your own sheet music as a PDF, image, or photo.',
    to: '/upload',
    iconBg: 'bg-[hsl(15,30%,92%)]',
    iconColor: 'text-[hsl(15,40%,45%)]',
    gradient: 'bg-gradient-to-br from-card to-[hsl(15,25%,93%)]',
  },
]

function FloatingScore() {
  return (
    <div className="relative h-full w-full">
      <motion.div
        initial={{ opacity: 0, y: 20, rotate: 0 }}
        animate={{ opacity: 1, y: 0, rotate: -2 }}
        transition={{ delay: 0.3, duration: 0.9, ease: 'easeOut' }}
        className="absolute right-0 top-6 w-[85%] md:w-[90%]"
      >
        <div className="rounded-sm border border-border/40 bg-[hsl(36,30%,97%)] p-5 pb-8 shadow-[0_8px_40px_-12px_hsl(var(--foreground)/0.12)]">
          <svg viewBox="0 0 360 180" className="w-full" xmlns="http://www.w3.org/2000/svg">
            {[40, 48, 56, 64, 72].map((y, i) => (
              <motion.line
                key={`s1-${i}`}
                x1="20"
                y1={y}
                x2="340"
                y2={y}
                stroke="hsl(var(--foreground))"
                strokeWidth="0.6"
                opacity="0.35"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ delay: 0.6 + i * 0.04, duration: 0.7 }}
              />
            ))}
            <motion.text
              x="26"
              y="68"
              fontSize="24"
              fill="hsl(var(--foreground))"
              opacity="0.55"
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.55 }}
              transition={{ delay: 1.0 }}
            >
              C
            </motion.text>
            <motion.g initial={{ opacity: 0 }} animate={{ opacity: 0.5 }} transition={{ delay: 1.1 }}>
              <text x="52" y="58" fontSize="11" fontWeight="bold" fill="hsl(var(--foreground))">
                4
              </text>
              <text x="52" y="70" fontSize="11" fontWeight="bold" fill="hsl(var(--foreground))">
                4
              </text>
            </motion.g>
            {[
              { x: 80, y: 64, type: 'quarter' },
              { x: 108, y: 56, type: 'quarter' },
              { x: 136, y: 52, type: 'half' },
              { x: 176, y: 60, type: 'quarter' },
              { x: 204, y: 68, type: 'quarter' },
              { x: 232, y: 56, type: 'quarter' },
              { x: 260, y: 48, type: 'half' },
              { x: 300, y: 60, type: 'quarter' },
            ].map((note, i) => (
              <motion.g
                key={`n1-${i}`}
                initial={{ opacity: 0, y: 3 }}
                animate={{ opacity: 0.7, y: 0 }}
                transition={{ delay: 1.2 + i * 0.07, duration: 0.4 }}
              >
                <ellipse
                  cx={note.x}
                  cy={note.y}
                  rx="4.5"
                  ry="3"
                  fill="hsl(var(--foreground))"
                  transform={`rotate(-8 ${note.x} ${note.y})`}
                />
                <line
                  x1={note.x + 4}
                  y1={note.y}
                  x2={note.x + 4}
                  y2={note.y - 20}
                  stroke="hsl(var(--foreground))"
                  strokeWidth="0.8"
                />
                {note.type === 'half' ? (
                  <ellipse
                    cx={note.x}
                    cy={note.y}
                    rx="3.5"
                    ry="2"
                    fill="hsl(36,30%,97%)"
                    transform={`rotate(-8 ${note.x} ${note.y})`}
                  />
                ) : null}
              </motion.g>
            ))}
            {[160, 288].map((x, i) => (
              <motion.line
                key={`bar-${i}`}
                x1={x}
                y1="40"
                x2={x}
                y2="72"
                stroke="hsl(var(--foreground))"
                strokeWidth="0.7"
                opacity="0.25"
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.25 }}
                transition={{ delay: 1.5 + i * 0.1 }}
              />
            ))}
            {[110, 118, 126, 134, 142].map((y, i) => (
              <motion.line
                key={`s2-${i}`}
                x1="20"
                y1={y}
                x2="340"
                y2={y}
                stroke="hsl(var(--foreground))"
                strokeWidth="0.6"
                opacity="0.35"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ delay: 0.8 + i * 0.04, duration: 0.7 }}
              />
            ))}
            <motion.text
              x="26"
              y="136"
              fontSize="18"
              fill="hsl(var(--foreground))"
              opacity="0.55"
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.55 }}
              transition={{ delay: 1.2 }}
            >
              F
            </motion.text>
            {[
              { x: 80, y: 134, type: 'half' },
              { x: 136, y: 126, type: 'quarter' },
              { x: 176, y: 130, type: 'quarter' },
              { x: 232, y: 122, type: 'quarter' },
              { x: 300, y: 130, type: 'half' },
            ].map((note, i) => (
              <motion.g
                key={`n2-${i}`}
                initial={{ opacity: 0, y: 3 }}
                animate={{ opacity: 0.65, y: 0 }}
                transition={{ delay: 1.4 + i * 0.07, duration: 0.4 }}
              >
                <ellipse
                  cx={note.x}
                  cy={note.y}
                  rx="4.5"
                  ry="3"
                  fill="hsl(var(--foreground))"
                  transform={`rotate(-8 ${note.x} ${note.y})`}
                />
                <line
                  x1={note.x + 4}
                  y1={note.y}
                  x2={note.x + 4}
                  y2={note.y - 18}
                  stroke="hsl(var(--foreground))"
                  strokeWidth="0.8"
                />
                {note.type === 'half' ? (
                  <ellipse
                    cx={note.x}
                    cy={note.y}
                    rx="3.5"
                    ry="2"
                    fill="hsl(36,30%,97%)"
                    transform={`rotate(-8 ${note.x} ${note.y})`}
                  />
                ) : null}
              </motion.g>
            ))}
            <motion.text
              x="70"
              y="162"
              fontSize="10"
              fontStyle="italic"
              fill="hsl(var(--primary))"
              opacity="0.6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.6 }}
              transition={{ delay: 2.0 }}
            >
              mp espressivo
            </motion.text>
          </svg>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.1, duration: 0.8 }}
        className="absolute left-0 top-0 w-[55%] md:w-[50%]"
      >
        <div className="rotate-[3deg] rounded-sm border border-border/30 bg-[hsl(38,35%,95%)] p-4 shadow-[0_4px_20px_-8px_hsl(var(--foreground)/0.08)]">
          <svg viewBox="0 0 200 70" className="w-full opacity-50" xmlns="http://www.w3.org/2000/svg">
            {[15, 23, 31, 39, 47].map((y, i) => (
              <line
                key={`f-${i}`}
                x1="10"
                y1={y}
                x2="190"
                y2={y}
                stroke="hsl(var(--foreground))"
                strokeWidth="0.5"
                opacity="0.4"
              />
            ))}
            <text x="16" y="42" fontSize="18" fill="hsl(var(--foreground))" opacity="0.5">
              C
            </text>
            {[50, 75, 100, 130, 160].map((x, i) => (
              <ellipse
                key={`fn-${i}`}
                cx={x}
                cy={31 + (i % 3) * 8 - 4}
                rx="4"
                ry="2.5"
                fill="hsl(var(--foreground))"
                opacity="0.35"
                transform={`rotate(-8 ${x} ${31 + (i % 3) * 8 - 4})`}
              />
            ))}
          </svg>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 0.15, scale: 1 }}
        transition={{ delay: 1.5, duration: 0.8 }}
        className="absolute right-[5%] top-[15%] h-20 w-20 rounded-full bg-primary blur-2xl"
      />
    </div>
  )
}

export function HomePage() {
  return (
    <main>
      <section className="container mx-auto px-6 pb-14 pt-16 md:pb-20 md:pt-24">
        <div className="grid grid-cols-1 items-center gap-10 md:grid-cols-2 md:gap-6">
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <h1 className="mb-5 font-display text-5xl font-bold leading-[1.08] tracking-tight text-foreground md:text-6xl lg:text-7xl">
              Sheet music,
              <br />
              <span className="text-primary">understood.</span>
            </h1>
            <p className="mb-8 max-w-md font-body text-lg leading-relaxed text-muted-foreground">
              Melodious reads your sheet music and turns it into a playable, exportable digital score. No scanning headaches - just music.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link
                to="/samples"
                className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 font-sans text-sm font-semibold text-primary-foreground shadow-sm transition-opacity hover:opacity-90"
              >
                Try a sample <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/upload"
                className="inline-flex items-center gap-2 rounded-lg border border-border px-6 py-3 font-sans text-sm font-medium text-foreground transition-colors hover:bg-accent"
              >
                Upload a score
              </Link>
            </div>
          </motion.div>
          <div className="relative h-72 md:h-[22rem]">
            <FloatingScore />
          </div>
        </div>
      </section>

      <section id="how-it-works" className="border-y border-border bg-card">
        <div className="container mx-auto px-6 py-10 md:py-14">
          <h2 className="mb-6 text-xl font-display font-bold tracking-tight text-foreground md:text-2xl">How it works</h2>
          <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
            {steps.map((step, i) => {
              const StepIcon = step.icon
              return (
                <motion.div
                  key={step.title}
                  initial={{ opacity: 0, y: 12 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.12, duration: 0.5 }}
                  className="flex items-start gap-4"
                >
                  <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <StepIcon className="h-4 w-4 text-primary" />
                  </div>
                  <div>
                    <h3 className="mb-1 font-display text-base font-semibold text-foreground">{step.title}</h3>
                    <p className="font-body text-sm leading-relaxed text-muted-foreground">{step.description}</p>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>
      </section>

      <section className="container mx-auto px-6 py-14 md:py-20">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="mb-2 text-center font-display text-2xl font-bold tracking-tight text-foreground md:text-3xl">Ways to start</h2>
          <p className="mx-auto mb-8 max-w-md text-center font-body text-sm text-muted-foreground">
            Bring your music in however works best for you.
          </p>
          <div className="mx-auto grid max-w-2xl grid-cols-1 gap-5 sm:grid-cols-2">
            {waysToStart.map((way, i) => {
              const WayIcon = way.icon
              return (
                <motion.div
                  key={way.title}
                  initial={{ opacity: 0, y: 12 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1, duration: 0.5 }}
                >
                  <Link
                    to={way.to}
                    className={`group block rounded-xl border border-border p-7 text-center transition-all hover:border-primary/40 hover:shadow-md ${way.gradient}`}
                  >
                    <div className={`mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg ${way.iconBg}`}>
                      <WayIcon className={`h-5 w-5 ${way.iconColor}`} />
                    </div>
                    <h3 className="mb-1.5 font-display text-lg font-semibold text-foreground transition-colors group-hover:text-primary">
                      {way.title}
                    </h3>
                    <p className="font-body text-sm leading-relaxed text-muted-foreground">{way.description}</p>
                  </Link>
                </motion.div>
              )
            })}
          </div>
        </motion.div>
      </section>
    </main>
  )
}
