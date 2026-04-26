import { Link } from 'react-router-dom'

import { resolveAssetUrl } from '../lib/api'
import type { ProductSample } from '../types/product'

type SampleTileProps = {
  sample: ProductSample
  featured?: boolean
}

export function SampleTile({ sample, featured = false }: SampleTileProps) {
  return (
    <Link
      to={`/workspace/${sample.id}`}
      className={`group block overflow-hidden rounded-[28px] border border-stone-200/90 bg-white/88 shadow-[0_20px_45px_rgba(120,113,108,0.12)] transition duration-200 hover:-translate-y-0.5 hover:border-amber-400/70 hover:shadow-[0_26px_60px_rgba(120,113,108,0.18)] ${
        featured ? 'lg:grid lg:grid-cols-[1.1fr_0.9fr]' : ''
      }`}
    >
      <div className={`overflow-hidden bg-stone-200 ${featured ? 'min-h-[18rem]' : 'aspect-[4/3]'}`}>
        <img
          src={resolveAssetUrl(sample.preview_image_url)}
          alt={sample.title}
          className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.03]"
        />
      </div>

      <div className="space-y-4 p-6 md:p-7">
        <div className="space-y-2">
          <p className="text-[11px] uppercase tracking-[0.32em] text-amber-700">
            {featured ? 'Featured sample' : 'Curated sample'}
          </p>
          <h3 className={`${featured ? 'text-3xl' : 'text-2xl'} font-serif text-stone-950`}>
            {sample.title}
          </h3>
          <p className="text-sm text-stone-500">{sample.subtitle}</p>
        </div>

        <p className="text-sm leading-7 text-stone-700">{sample.description}</p>

        <div className="flex flex-wrap gap-2">
          {sample.tags.map((tag) => (
            <span key={tag} className="rounded-full bg-amber-100 px-3 py-1 text-xs text-amber-900">
              {tag}
            </span>
          ))}
        </div>

        <span className="inline-flex items-center gap-2 text-sm font-medium text-stone-950">
          Open workspace
          <span aria-hidden="true" className="transition-transform group-hover:translate-x-1">
            →
          </span>
        </span>
      </div>
    </Link>
  )
}
