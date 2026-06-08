// JSX typings for the html-midi-player web components.
import type { DetailedHTMLProps, HTMLAttributes } from 'react'

type MidiPlayerProps = DetailedHTMLProps<HTMLAttributes<HTMLElement>, HTMLElement> & {
  src?: string
  'sound-font'?: string
  visualizer?: string
  loop?: boolean
}

type MidiVisualizerProps = DetailedHTMLProps<HTMLAttributes<HTMLElement>, HTMLElement> & {
  src?: string
  type?: string
}

// React 19's automatic runtime resolves intrinsic elements from React.JSX, so
// augment the react module's JSX namespace as well as the legacy global one.
declare module 'react' {
  namespace JSX {
    interface IntrinsicElements {
      'midi-player': MidiPlayerProps
      'midi-visualizer': MidiVisualizerProps
    }
  }
}

declare global {
  namespace JSX {
    interface IntrinsicElements {
      'midi-player': MidiPlayerProps
      'midi-visualizer': MidiVisualizerProps
    }
  }
}

export {}
