import { useEffect, useRef, useState } from 'react'
import { OpenSheetMusicDisplay } from 'opensheetmusicdisplay'
import { ScrollText, Loader2 } from 'lucide-react'

interface Props {
  musicXml: string | null
}

export function EngravedScore({ musicXml }: Props) {
  const hostRef = useRef<HTMLDivElement>(null)
  const osmdRef = useRef<OpenSheetMusicDisplay | null>(null)
  const [status, setStatus] = useState<'idle' | 'loading' | 'ok' | 'error'>('idle')

  useEffect(() => {
    let cancelled = false
    if (!musicXml || !hostRef.current) return

    async function render() {
      setStatus('loading')
      try {
        if (!osmdRef.current && hostRef.current) {
          osmdRef.current = new OpenSheetMusicDisplay(hostRef.current, {
            autoResize: true,
            backend: 'svg',
            drawingParameters: 'compact',
            drawTitle: false,
            drawPartNames: false,
          })
        }
        const osmd = osmdRef.current!
        await osmd.load(musicXml as string)
        if (cancelled) return
        osmd.render()
        if (!cancelled) setStatus('ok')
      } catch (error) {
        console.warn('OSMD render failed', error)
        if (!cancelled) setStatus('error')
      }
    }

    void render()
    return () => {
      cancelled = true
    }
  }, [musicXml])

  return (
    <div className="panel">
      <div className="panel-head">
        <div className="ttl">
          <ScrollText className="ic" size={17} /> Engraved score
        </div>
        <span className="subtle">Rendered from MusicXML</span>
      </div>
      <div className="panel-body">
        {status === 'loading' && (
          <div className="osmd-fallback">
            <Loader2 size={18} className="spin-ic" /> Engraving…
          </div>
        )}
        {status === 'error' && (
          <div className="osmd-fallback">
            Could not engrave this score in the browser. The overlay, MusicXML, and MIDI below are still
            available.
          </div>
        )}
        <div className="osmd-host" ref={hostRef} style={{ display: status === 'ok' ? 'block' : 'none' }} />
      </div>
    </div>
  )
}
