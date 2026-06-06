type MetricCardProps = {
  label: string
  value: number
  accent?: string
}

export function MetricCard({ label, value, accent = 'text-stone-900' }: MetricCardProps) {
  return (
    <div className="rounded-[24px] border border-stone-200 bg-white px-5 py-4 shadow-[0_16px_35px_rgba(120,113,108,0.12)]">
      <p className="text-xs uppercase tracking-[0.26em] text-stone-500">{label}</p>
      <p className={`mt-3 font-serif text-3xl ${accent}`}>{value}</p>
    </div>
  )
}
