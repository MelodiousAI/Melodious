# Week 5 Lovable Prompt

Use this prompt in Lovable for the public Melodious frontend:

```text
Design a polished, demo-ready public web app for “Melodious”, a musician-facing sheet music transcription product.

Important: this is NOT an admin dashboard, dev console, or backend test UI. It should feel like a real product for musicians and music students.

Tech target:
- React + TypeScript
- Vite-friendly structure
- Tailwind CSS
- Responsive on desktop and mobile
- Clean component structure that can be integrated into an existing repo
- No backend implementation; use mock data and reusable components

Product constraints:
- Current public Week 5 flow is sample-first
- Show a polished “Upload sheet music” area, but make it clearly “Coming soon”
- The real active CTA is choosing a bundled sample and transcribing it
- Do not expose payloads, assembly modes, backend URLs, graph tensors, staff regions, or API jargon
- Include placeholders for future attention visualization and future LLM music explanation

Visual direction:
- Warm paper / ink / studio aesthetic
- Elegant and modern, not corporate SaaS
- Avoid purple-heavy AI styling and avoid dark-mode-only design
- Think musicians, notation, paper texture, recital-program refinement
- Use expressive typography and clear hierarchy
- The app should feel premium and demo-worthy

Main screen requirements:
1. Hero section
   - Product name: Melodious
   - Short value prop: transcribe sheet music, preview the result, play it back, and understand it
   - Primary CTA: Try a sample
   - Secondary CTA: Upload sheet music (Coming soon)

2. Sample library section
   - 3 to 5 sample cards
   - Each card shows title, short subtitle, thumbnail/score preview, and a Transcribe button

3. Transcription result experience
   - Large score preview panel
   - Summary cards for transcription results
   - MIDI playback area
   - Download MusicXML button
   - Download MIDI button
   - Simple confidence cue card
   - Explainability card for attention overlay placeholder
   - Future “Ask Melodious” card for music explanation/chat placeholder

4. States
   - Empty state before selecting a sample
   - Loading/transcribing state
   - Success state
   - Graceful unavailable/placeholder state for explainability and upload
   - Error state

Use this mock data shape in the UI:
- config: { appName, stage, featureFlags }
- sample: { id, title, subtitle, thumbnailUrl, tags }
- transcription result: {
    title,
    sampleId,
    scorePreviewUrl,
    summary: { noteCount, clefCount, restCount, unmatchedCount },
    confidenceIndicator: { tone, label, message, calibrated },
    explainability: { state, title, message },
    downloads: { musicxmlReady, midiReady },
    audio: { playable },
    featureFlags: { attentionOverlayEnabled, llmExplainerEnabled }
  }

Copy/style guidance:
- Use plain language for musicians
- Avoid technical terminology
- Explainability copy should say the attention overlay is reserved for a future model upgrade
- Confidence copy should be qualitative, simple, and honest
- LLM/music explanation card should be framed as “Coming soon”

Output:
- A complete frontend UI with well-structured React components
- Mock data included
- Clean sections and reusable cards/buttons/panels
- No backend code
```
