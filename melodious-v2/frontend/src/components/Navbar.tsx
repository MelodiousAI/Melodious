import { Music } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

export function Navbar() {
  const location = useLocation()

  const links = [
    { to: '/', label: 'Home' },
    { to: '/library', label: 'Library' },
    { to: '/upload', label: 'Upload' },
  ]

  function isActive(path: string) {
    if (path === '/') return location.pathname === '/'
    return location.pathname.startsWith(path)
  }

  return (
    <header className="navbar">
      <Link to="/" className="navbar-brand">
        <Music className="brand-icon" size={22} />
        <span className="brand-name">Melodious</span>
      </Link>
      <nav className="navbar-links">
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`navbar-link${isActive(link.to) ? ' active' : ''}`}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </header>
  )
}
