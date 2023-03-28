import sys

from src.main import app
from uvicorn import run

if __name__ == "__main__":
    host, port = sys.argv[1], int(sys.argv[2])
    run(app, host=host, port=port, reload=False)
