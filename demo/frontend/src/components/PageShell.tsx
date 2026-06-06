import type { PropsWithChildren } from 'react'

type PageShellProps = PropsWithChildren<{
  className?: string
}>

export function PageShell({ children, className = '' }: PageShellProps) {
  return (
    <main className={`mx-auto flex w-full max-w-7xl flex-1 flex-col px-6 py-10 lg:px-10 ${className}`.trim()}>
      {children}
    </main>
  )
}
