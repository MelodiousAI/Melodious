import type { PropsWithChildren } from 'react'

type StatusPanelProps = PropsWithChildren<{
  title: string
  eyebrow?: string
  body: string
  tone?: 'default' | 'muted' | 'warm' | 'danger'
}>

const toneStyles: Record<NonNullable<StatusPanelProps['tone']>, string> = {
  default: 'border-stone-200 bg-white/88',
  muted: 'border-stone-200/70 bg-stone-50/70',
  warm: 'border-amber-200 bg-amber-50/90',
  danger: 'border-rose-200 bg-rose-50/90',
}

export function StatusPanel({
  title,
  eyebrow,
  body,
  tone = 'default',
  children,
}: StatusPanelProps) {
  return (
    <section className={`rounded-[24px] border p-5 shadow-[0_16px_35px_rgba(120,113,108,0.10)] ${toneStyles[tone]}`}>
      {eyebrow ? (
        <p className="text-[11px] uppercase tracking-[0.28em] text-stone-500">{eyebrow}</p>
      ) : null}
      <h3 className="mt-2 font-serif text-2xl text-stone-950">{title}</h3>
      <p className="mt-3 text-sm leading-7 text-stone-700">{body}</p>
      {children}
    </section>
  )
}
