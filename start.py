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

BACKEND_PORT = "8000"
FRONTEND_PORT = "8080"

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
    print("🚀 Krapter Proxy Tool - Local Launcher")
    print("===================================================")
    
    # 0. Check/Create Venv
    if not os.path.exists(PYTHON_EXE):
        print("⚠️ Virtual environment not found. Initializing...")
        try:
            setup_venv()
        except Exception as e:
            print(f"❌ Critical Setup Error: {e}")
            return

    # Use system python if venv python doesn't exist
    python_cmd = f'"{PYTHON_EXE}"' if os.path.exists(PYTHON_EXE) else "python"

    processes = []
    
    try:
        # 1. Start Backend
        print(f"\n[1/3] Starting Backend (Port {BACKEND_PORT})...")
        p_backend = run_service(
            [python_cmd, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", BACKEND_PORT, "--reload"],
            cwd="backend"
        )
        processes.append(p_backend)
        time.sleep(2)
        
        # 2. Start Worker
        print("\n[2/3] Starting Worker...")
        p_worker = run_service(
            [python_cmd, "scheduler.py"],
            cwd="worker"
        )
        processes.append(p_worker)
        
        # 3. Start Frontend
        print(f"\n[3/3] Starting Frontend (Port {FRONTEND_PORT})...")
        p_frontend = run_service(
            [python_cmd, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", FRONTEND_PORT, "--reload"],
            cwd="frontend"
        )
        processes.append(p_frontend)
        
        print("\n✅ All services are running!")
        print(f"👉 Dashboard: http://localhost:{FRONTEND_PORT}")
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
