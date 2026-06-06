import React from 'react'
import { createRoot } from 'react-dom/client'
// Registers the <midi-player> and <midi-visualizer> custom elements.
import 'html-midi-player'
import './styles.css'
import { App } from './App'

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
