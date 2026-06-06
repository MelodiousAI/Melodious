import { ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'

import { fetchDisplaySamples, type DisplaySample } from '../data/lovableAdapter'

export function LibraryPage() {
  const [samples, setSamples] = useState<DisplaySample[]>([])
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true

    async function load() {
      try {
        const loaded = await fetchDisplaySamples()
        if (isMounted) {
          setSamples(loaded)
        }
      } catch (error) {
        if (isMounted) {
          setErrorMessage(error instanceof Error ? error.message : 'Failed to load samples.')
        }
      }
    }

    void load()

    return () => {
      isMounted = false
    }
  }, [])

  const featured = samples.find((sample) => sample.featured) ?? samples[0]
  const rest = samples.filter((sample) => sample.id !== featured?.id)

  return (
    <main className="container mx-auto px-6 py-12 md:py-20">
      <div className="mx-auto max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-10"
        >
          <h1 className="mb-2 font-display text-3xl font-bold tracking-tight text-foreground md:text-4xl">
            Sample Library
          </h1>
          <p className="max-w-lg font-body text-base text-muted-foreground">
            Choose a piece to transcribe. Each score is curated to showcase different aspects of Melodious.
          </p>
        </motion.div>

        {errorMessage ? (
          <div className="rounded-xl border border-destructive/30 bg-card p-6 text-sm text-muted-foreground">
            {errorMessage}
          </div>
        ) : null}

        {featured ? (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.5 }}
            className="mb-8"
          >
            <Link
              to={`/workspace/${featured.id}`}
              className="group relative block overflow-hidden rounded-xl border border-border bg-card p-7 transition-all hover:border-primary/60 hover:bg-[hsl(38,40%,97%)] hover:shadow-md active:scale-[0.998] active:shadow-sm md:p-8"
            >
              <div className="absolute left-0 top-0 h-full w-1 rounded-l-xl bg-primary/60" />

              <span className="mb-3 block pl-3 text-[11px] font-sans font-semibold uppercase tracking-widest text-primary">
                Featured
              </span>
              <div className="flex flex-col gap-5 pl-3 md:flex-row md:items-start">
                <div className="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-lg bg-accent">
                  <span className="text-3xl">{featured.icon}</span>
                </div>
                <div className="flex-1">
                  <h2 className="mb-0.5 font-display text-xl font-bold text-foreground transition-colors group-hover:text-primary">
                    {featured.title}
                  </h2>
                  <p className="mb-2 font-sans text-sm text-muted-foreground">{featured.subtitle}</p>
                  <p className="mb-3 font-body text-sm leading-relaxed text-muted-foreground">
                    {featured.description}
                  </p>
                  <div className="mb-4 flex flex-wrap gap-1.5">
                    <span className="rounded-full bg-accent px-2.5 py-0.5 text-[11px] font-sans font-medium text-foreground/65">
                      {featured.instrument}
                    </span>
                    <span className="rounded-full bg-accent px-2.5 py-0.5 text-[11px] font-sans font-medium text-foreground/65">
                      {featured.era}
                    </span>
                    {featured.tags.map((tag) => (
                      <span
                        key={tag}
                        className="rounded-full bg-accent px-2 py-0.5 text-[11px] font-sans text-muted-foreground"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <span className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-sans font-semibold text-primary-foreground shadow-sm transition-shadow group-hover:shadow">
                    Open workspace <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
                  </span>
                </div>
              </div>
            </Link>
          </motion.div>
        ) : null}

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          {rest.map((sample, i) => (
            <motion.div
              key={sample.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 + i * 0.08, duration: 0.5 }}
            >
              <Link
                to={`/workspace/${sample.id}`}
                className="group relative block h-full rounded-xl border border-border bg-card p-6 transition-all hover:border-primary/60 hover:bg-[hsl(38,40%,97%)] hover:shadow-md active:scale-[0.995] active:shadow-sm"
              >
                <div className="mb-3 flex items-start gap-3.5">
                  <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-lg bg-accent transition-colors group-hover:bg-primary/10">
                    <span className="text-xl">{sample.icon}</span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="mb-0.5 font-display text-base font-semibold text-foreground transition-colors group-hover:text-primary">
                      {sample.title}
                    </h3>
                    <p className="font-sans text-sm text-muted-foreground">{sample.subtitle}</p>
                  </div>
                </div>
                <p className="mb-3 line-clamp-2 font-body text-sm leading-relaxed text-muted-foreground">
                  {sample.description}
                </p>
                <div className="mb-3 flex flex-wrap gap-1.5">
                  <span className="rounded-full bg-accent px-2.5 py-0.5 text-[11px] font-sans font-medium text-foreground/65">
                    {sample.instrument}
                  </span>
                  <span className="rounded-full bg-accent px-2.5 py-0.5 text-[11px] font-sans font-medium text-foreground/65">
                    {sample.era}
                  </span>
                  {sample.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-accent px-2 py-0.5 text-[11px] font-sans text-muted-foreground"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                <span className="inline-flex items-center gap-1.5 text-sm font-sans font-medium text-primary">
                  Open workspace <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
                </span>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </main>
  )
}
