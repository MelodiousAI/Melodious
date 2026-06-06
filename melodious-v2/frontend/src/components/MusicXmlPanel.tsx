import { useState } from 'react'
import { Code2, Copy, Check, Download } from 'lucide-react'

interface Props {
  musicXml: string | null
  downloadUrl: string
}

export function MusicXmlPanel({ musicXml, downloadUrl }: Props) {
  const [copied, setCopied] = useState(false)

  async function copy() {
    if (!musicXml) return
    try {
      await navigator.clipboard.writeText(musicXml)
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    } catch {
      /* clipboard may be blocked; ignore */
    }
  }

  return (
    <div className="panel">
      <div className="panel-head">
        <div className="ttl">
          <Code2 className="ic" size={17} /> MusicXML
        </div>
        <div className="row">
          <button className="btn btn--ghost btn--sm" onClick={copy} disabled={!musicXml}>
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? 'Copied' : 'Copy'}
          </button>
          <a className="btn btn--ghost btn--sm" href={downloadUrl}>
            <Download size={14} /> Download
          </a>
        </div>
      </div>
      <div className="panel-body flush">
        <pre className="code-block">{musicXml ?? 'Loading MusicXML…'}</pre>
      </div>
    </div>
  )
}
