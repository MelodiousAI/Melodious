type UploadPanelProps = {
  message: string
}

export function UploadPanel({ message }: UploadPanelProps) {
  return (
    <section className="relative overflow-hidden rounded-[32px] border border-dashed border-stone-300 bg-[linear-gradient(135deg,rgba(255,251,235,0.96),rgba(245,245,244,0.96))] p-8 shadow-[0_24px_55px_rgba(120,113,108,0.12)]">
      <div className="absolute -right-10 top-0 h-44 w-44 rounded-full bg-amber-200/40 blur-3xl" />
      <div className="absolute left-4 top-20 h-28 w-28 rounded-full bg-orange-200/30 blur-2xl" />

      <div className="relative space-y-5">
        <div className="inline-flex rounded-full border border-stone-300 bg-white/70 px-4 py-1 text-xs uppercase tracking-[0.28em] text-stone-600">
          Upload Coming Soon
        </div>
        <div className="space-y-3">
          <h2 className="font-serif text-3xl text-stone-900">Bring your own score next.</h2>
          <p className="max-w-2xl text-sm leading-7 text-stone-700">{message}</p>
        </div>

        <div className="grid gap-3 md:grid-cols-[1fr_auto]">
          <div className="rounded-[24px] border border-stone-300 bg-white/70 px-5 py-4 text-sm text-stone-500">
            Drag-and-drop upload will appear here once the detector-side image pipeline is wired in.
          </div>
          <button
            type="button"
            disabled
            className="rounded-full bg-stone-300 px-5 py-4 text-sm font-medium text-stone-600"
          >
            Upload Sheet Music
          </button>
        </div>
      </div>
    </section>
  )
}
