from src.main import app
from uvicorn import run

if __name__ == "__main__":
    run(app, host="localhost", port=5000, reload=False)
