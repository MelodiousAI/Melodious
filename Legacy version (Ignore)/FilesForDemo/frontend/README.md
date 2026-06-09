# Melodious Frontend

This folder contains the Week 5 public product frontend for Melodious.

## Purpose

- Keep the public demo UI separate from the internal/debug Streamlit MVP.
- Host the integrated Lovable-based React experience inside the repo.
- Talk only to the musician-facing `/product/*` backend facade instead of the engineering routes.

## Current shape

- `src/app/App.tsx`
  Routed Week 5 public app with home, library, workspace, and upload placeholder pages.
- `src/components/`
  Shared public-product UI such as navigation, footer, and route support pieces.
- `src/pages/`
  Lovable-derived route implementations adapted to the current Melodious backend reality.
- `src/data/lovableAdapter.ts`
  Thin adapter layer that maps the real `/product/*` responses into the Lovable page model.
- `src/lib/api.ts`
  Typed client for `/product/*` plus mock fallbacks.
- `src/hooks/`
  Small frontend-only hooks used by the Lovable pages.
- `src/types/`
  Public product DTOs.
- `LOVABLE_PROMPT.md`
  The exact prompt to use when generating the polished UI in Lovable.

## Commands

```powershell
npm install
npm run dev
npm test
npm run build
```

## Backend expectation

The frontend expects the FastAPI backend to expose:

- `GET /product/config`
- `GET /product/samples`
- `GET /product/samples/{sample_id}/image`
- `POST /product/transcribe`
- `GET /product/samples/{sample_id}/downloads/{format}`

By default the frontend uses `http://127.0.0.1:8000` as the backend base URL.
Override it with `VITE_API_BASE_URL` if needed.
