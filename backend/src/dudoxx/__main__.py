import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "dudoxx.app:app",
        host=os.getenv("HOST", default="0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", default=8000)),
        reload=os.getenv("RELOAD", default=True),
    )
