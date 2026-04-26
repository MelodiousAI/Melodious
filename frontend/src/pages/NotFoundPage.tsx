import { Link } from 'react-router-dom'

import { PageShell } from '../components/PageShell'

export function NotFoundPage() {
  return (
    <PageShell className="items-center justify-center">
      <div className="max-w-xl rounded-[32px] border border-stone-200 bg-white/88 px-8 py-12 text-center shadow-[0_24px_60px_rgba(120,113,108,0.12)]">
        <p className="text-[11px] uppercase tracking-[0.32em] text-stone-500">404</p>
        <h1 className="mt-3 font-serif text-4xl text-stone-950">This page does not exist in Melodious.</h1>
        <p className="mt-4 text-base leading-8 text-stone-700">
          The routed frontend keeps only the public Week 5 experience: home, library, workspace, and the upload placeholder.
        </p>
        <Link
          to="/"
          className="mt-8 inline-flex items-center justify-center rounded-full bg-stone-950 px-7 py-3 text-sm font-medium text-stone-50 transition hover:bg-stone-800"
        >
          Back to home
        </Link>
      </div>
    </PageShell>
  )
}
