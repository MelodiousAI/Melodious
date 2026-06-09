import type { ReactNode } from 'react'

type InfoCardProps = {
  eyebrow: string
  title: string
  body: string
  tone?: 'default' | 'warm' | 'ink'
  children?: ReactNode
}

export function InfoCard({
  eyebrow,
  title,
  body,
  tone = 'default',
  children,
}: InfoCardProps) {
  const toneClasses = {
    default: 'border-stone-200 bg-white text-stone-900',
    warm: 'border-amber-200 bg-amber-50 text-stone-900',
    ink: 'border-stone-900 bg-stone-950 text-stone-50',
  }

  return (
    <section
      className={`rounded-[28px] border p-6 shadow-[0_20px_45px_rgba(120,113,108,0.12)] ${toneClasses[tone]}`}
    >
      <p className={`text-xs uppercase tracking-[0.28em] ${tone === 'ink' ? 'text-amber-200' : 'text-amber-700'}`}>
        {eyebrow}
      </p>
      <h3 className="mt-3 font-serif text-2xl">{title}</h3>
      <p className={`mt-3 text-sm leading-6 ${tone === 'ink' ? 'text-stone-300' : 'text-stone-700'}`}>
        {body}
      </p>
      {children}
    </section>
  )
}
