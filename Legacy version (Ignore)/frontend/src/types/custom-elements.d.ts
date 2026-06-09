import type { DetailedHTMLProps, HTMLAttributes } from 'react'

declare module 'react' {
  namespace JSX {
    interface IntrinsicElements {
      'midi-player': DetailedHTMLProps<HTMLAttributes<HTMLElement>, HTMLElement> & {
        src?: string
        soundFont?: string
        visualizer?: string
      }
    }
  }
}
