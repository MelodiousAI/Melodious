import { resolveAssetUrl } from '../lib/api'

type MidiPlaybackCardProps = {
  sourceUrl: string
  title: string
  message: string
}

export function MidiPlaybackCard({
  sourceUrl,
  title,
  message,
}: MidiPlaybackCardProps) {
  const resolvedSourceUrl = resolveAssetUrl(sourceUrl)

  return (
    <section className="rounded-[28px] border border-stone-900 bg-stone-950 p-6 text-stone-50 shadow-[0_26px_55px_rgba(28,25,23,0.24)]">
      <p className="text-xs uppercase tracking-[0.28em] text-amber-200">Playback</p>
      <h3 className="mt-3 font-serif text-2xl">{title}</h3>
      <p className="mt-3 text-sm leading-6 text-stone-300">{message}</p>

      <div className="mt-5 space-y-4 rounded-[24px] bg-stone-900/90 p-4">
        <midi-player
          src={resolvedSourceUrl}
          soundFont="https://storage.googleapis.com/magentadata/js/soundfonts/sgm_plus"
          className="block w-full"
        />
        <p className="text-xs leading-5 text-stone-400">
          If your browser does not support inline MIDI playback, use the download button below.
        </p>
      </div>
    </section>
  )
}
