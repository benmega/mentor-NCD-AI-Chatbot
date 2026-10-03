import subprocess
import sys
import os
import time

def main():
    print("========================================")
    print("Starting Mentor NCD AI Chatbot Servers")
    print("========================================")

    # 1. Determine the correct python executable to use (checks for .venv)
    venv_python = os.path.join(".venv", "Scripts", "python.exe") if os.name == 'nt' else os.path.join(".venv", "bin", "python")
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable

    print(f"[INFO] Using Python executable: {python_exe}")

    # Set flag to spawn a new terminal window on Windows
    creation_flags = subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0

    # 2. Start the Backend (FastAPI via Uvicorn)
    print("[STARTING] Backend Server (Port 8000)... (Opening in new window)")
    backend_process = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd="backend",
        creationflags=creation_flags
    )

    # 3. Start the Frontend (Simple HTTP Server)
    print("[STARTING] Frontend Server (Port 5500)... (Opening in new window)")
    frontend_process = subprocess.Popen(
        [python_exe, "-m", "http.server", "5500", "--directory", "frontend"],
        creationflags=creation_flags
    )

    print("========================================")
    print("All servers are running in separate terminal windows!")
    print("Local access (this computer): http://localhost:5500")
    print("Network access (other devices): Use your computer's local IP on port 5500")
    print("Close the new windows or press Ctrl+C here to stop both servers.")
    print("========================================")

    # 4. Wait indefinitely until interrupted
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOPPING] Shutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("[STOPPED] Both servers have been stopped gracefully.")

if __name__ == "__main__":
    main()
