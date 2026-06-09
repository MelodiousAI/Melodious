import { Music } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

import { cn } from '../lib/utils'

export function Navbar() {
  const location = useLocation()

  const links = [
    { to: '/', label: 'Home' },
    { to: '/samples', label: 'Library' },
    { to: '/upload', label: 'Upload' },
  ]

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-card/80 backdrop-blur-sm">
      <div className="container mx-auto flex h-16 items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2.5 group">
          <Music className="h-5 w-5 text-primary" />
          <span className="font-display text-xl font-semibold tracking-tight text-foreground">
            Melodious
          </span>
        </Link>

        <nav className="flex items-center gap-6 md:gap-8">
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={cn(
                'text-sm font-sans font-medium transition-colors',
                location.pathname === link.to || (link.to !== '/' && location.pathname.startsWith(link.to))
                  ? 'text-foreground'
                  : 'text-muted-foreground hover:text-foreground',
              )}
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  )
}
