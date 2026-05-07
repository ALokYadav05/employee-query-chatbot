import logging
import subprocess
import sys
import time


def run_servers():
    """
    Runs both frontend and backend servers concurrently.
    The backend is started first, followed by the frontend.
    If the frontend is closed, the backend process is terminated.
    """
    # Start the Backend (FastAPI via Uvicorn)
    print("Starting Backend Server on Port 8000...")
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app:app",
        "--host", "0.0.0.0", "--port", "8000"
    ])

    # Wait a moment for backend to initialize
    time.sleep(3)

    # start the Frontend (Streamlit)
    print("Starting Streamlit UI...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "frontend/app.py"
        ])
    except KeyboardInterrupt:
        logging.error("\nStopping servers...")
    finally:
        # Kill the backend when the frontend is closed
        backend_process.terminate()


if __name__ == '__main__':
    run_servers()
