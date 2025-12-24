import subprocess
import time
import os
import sys

# Configuration
VENV_DIR = os.path.abspath("venv")
if os.name == 'nt':
    PYTHON_EXE = os.path.join(VENV_DIR, "Scripts", "python.exe")
else:
    PYTHON_EXE = os.path.join(VENV_DIR, "bin", "python")

# Render provides PORT env var
PORT = os.getenv("PORT", "8000")

def run_command(cmd, cwd=None):
    try:
        subprocess.check_call(cmd, cwd=cwd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {cmd}")
        raise e

def setup_venv():
    print("🔧 Setting up Virtual Environment (venv)...")
    
    # 1. Create venv
    if not os.path.exists(VENV_DIR):
        print("   Creating venv folder...")
        try:
            run_command("py -m venv venv")
        except:
            run_command("python -m venv venv")
    
    # 2. Install dependencies
    print("   Installing dependencies into venv...")
    try:
        run_command(f'"{PYTHON_EXE}" -m pip install --upgrade pip')
    except:
        pass
        
    run_command(f'"{PYTHON_EXE}" -m pip install -r requirements.txt')
    print("✅ Setup complete.")

def run_service(command_args, cwd, env_vars=None):
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    
    cmd_str = " ".join(command_args)
    return subprocess.Popen(cmd_str, cwd=cwd, env=env, shell=True)

def main():
    print("===================================================")
    print("🚀 Krapter Proxy Tool - Render Launcher")
    print("===================================================")
    
    # 0. Check/Create Venv (Only if not on Render/Docker where env is pre-built)
    # On Render, we usually use the system python or pre-installed deps.
    # But for local consistency, we keep this check.
    if not os.path.exists(PYTHON_EXE) and os.name == 'nt':
         # Only auto-setup on Windows/Local. On Render, pip install is done via build command.
        print("⚠️ Virtual environment not found. Initializing...")
        try:
            setup_venv()
        except Exception as e:
            print(f"❌ Critical Setup Error: {e}")
            return

    # Use system python if venv python doesn't exist (e.g. on Render)
    python_cmd = f'"{PYTHON_EXE}"' if os.path.exists(PYTHON_EXE) else "python"

    processes = []
    
    try:
        # 1. Start Worker
        print("\n[1/2] Starting Worker...")
        p_worker = run_service(
            [python_cmd, "scheduler.py"],
            cwd="worker"
        )
        processes.append(p_worker)
        
        # 2. Start Backend (which serves Frontend)
        print(f"\n[2/2] Starting Backend & Frontend (Port {PORT})...")
        # On Render, we must bind to 0.0.0.0:$PORT
        p_backend = run_service(
            [python_cmd, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", PORT],
            cwd="backend"
        )
        processes.append(p_backend)
        
        print(f"\n✅ Services running! Access at http://localhost:{PORT}")
        print("Press Ctrl+C to stop.")
        
        # Wait for processes
        p_backend.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        for p in processes:
            p.terminate()
        print("Done.")

if __name__ == "__main__":
    main()
