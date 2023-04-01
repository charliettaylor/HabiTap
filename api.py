import os

from src.main import app
from uvicorn import run

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    run(app, host="0.0.0.0", port=port, reload=False)
