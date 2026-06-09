import type { ProductSample } from '../types/product'

type SampleCardProps = {
  sample: ProductSample
  imageUrl: string
  isActive: boolean
  onSelect: (sampleId: string) => void
}

export function SampleCard({
  sample,
  imageUrl,
  isActive,
  onSelect,
}: SampleCardProps) {
  return (
    <article
      className={`overflow-hidden rounded-[28px] border transition duration-200 ${
        isActive
          ? 'border-stone-900 bg-stone-950 text-stone-50 shadow-[0_28px_60px_rgba(28,25,23,0.18)]'
          : 'border-stone-200 bg-white/90 text-stone-900 shadow-[0_20px_45px_rgba(120,113,108,0.14)]'
      }`}
    >
      <div className="aspect-[4/3] overflow-hidden bg-stone-200">
        <img
          src={imageUrl}
          alt={sample.title}
          className="h-full w-full object-cover transition duration-500 hover:scale-[1.03]"
        />
      </div>

      <div className="space-y-4 p-6">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.28em] text-amber-700">
            Curated Sample
          </p>
          <h3 className="font-serif text-2xl">{sample.title}</h3>
          <p className={`${isActive ? 'text-stone-300' : 'text-stone-600'}`}>
            {sample.subtitle}
          </p>
        </div>

        <p className={`text-sm leading-6 ${isActive ? 'text-stone-300' : 'text-stone-700'}`}>
          {sample.description}
        </p>

        <div className="flex flex-wrap gap-2">
          {sample.tags.map((tag) => (
            <span
              key={tag}
              className={`rounded-full px-3 py-1 text-xs ${
                isActive ? 'bg-stone-800 text-stone-100' : 'bg-amber-100 text-amber-900'
              }`}
            >
              {tag}
            </span>
          ))}
        </div>

        <button
          type="button"
          onClick={() => onSelect(sample.id)}
          className={`w-full rounded-full px-4 py-3 text-sm font-medium transition ${
            isActive
              ? 'bg-amber-300 text-stone-950 hover:bg-amber-200'
              : 'bg-stone-900 text-stone-50 hover:bg-stone-700'
          }`}
        >
          Transcribe This Sample
        </button>
      </div>
    </article>
  )
}
