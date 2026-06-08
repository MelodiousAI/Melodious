"""Run the local Melodious V2 API."""

from __future__ import annotations

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "melodious_v2.api.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        # Only watch source code so generated upload artifacts under runs/ never
        # trigger reloads while a long extraction job is running.
        reload_dirs=["src"],
    )

