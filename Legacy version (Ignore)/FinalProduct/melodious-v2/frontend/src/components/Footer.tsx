import { ExternalLink } from 'lucide-react'

export function Footer() {
  return (
    <footer className="footer">
      <span>© {new Date().getFullYear()} Melodious — Sheet music, understood.</span>
      <a href="https://github.com/MelodiousAI/Melodious" target="_blank" rel="noreferrer">
        <ExternalLink size={14} style={{ verticalAlign: '-2px', marginRight: 6 }} />
        MelodiousAI/Melodious
      </a>
    </footer>
  )
}
