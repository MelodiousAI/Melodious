# Melodious

> **Use this folder:** [`Current-Version (Use this)/`](Current-Version%20(Use%20this)/) — active product (API, UI, tests, docs).  
> **Ignore:** [`Legacy version (Ignore)/`](Legacy%20version%20(Ignore)/) — archived snapshots and earlier code only.

Optical music recognition for sheet music: detect symbols, assemble relationships, and export MusicXML/MIDI with a polished web app.

| | |
|---|---|
| **Live demo** | https://melodious.website |
| **Product (start here)** | [`Current-Version (Use this)/`](Current-Version%20(Use%20this)/) |
| **Full README** | [`Current-Version (Use this)/README.md`](Current-Version%20(Use%20this)/README.md) |

---

## Repository layout

```
Melodious/
├── Current-Version (Use this)/   ← develop and run here
├── Legacy version (Ignore)/      ← reference only
└── README.md                     ← you are here
```

---

## Quick start

**Backend**

```powershell
cd "Current-Version (Use this)"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "src"
python scripts\run_api.py
```

**Frontend**

```powershell
cd "Current-Version (Use this)/frontend"
npm install
npm run dev
```

See [`Current-Version (Use this)/README.md`](Current-Version%20(Use%20this)/README.md) for architecture, metrics, and deployment.
