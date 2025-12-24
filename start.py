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

REDIS_PORT = "6380"
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
    # Use CREATE_NEW_CONSOLE flag on Windows if possible to separate logs? 
    # For now, keep in same console but rely on log levels.
    return subprocess.Popen(cmd_str, cwd=cwd, env=env, shell=True)

def main():
    print("===================================================")
    print("🚀 Krapter Proxy Tool - Robust Launcher")
    print("===================================================")
    
    # 0. Check/Create Venv
    if not os.path.exists(PYTHON_EXE):
        print("⚠️ Virtual environment not found. Initializing...")
        try:
            setup_venv()
        except Exception as e:
            print(f"❌ Critical Setup Error: {e}")
            print("Your Python installation might be broken. Please reinstall Python from python.org")
            input("Press Enter to exit...")
            return

    # 1. Start Redis (Docker) - REMOVED
    # print("\n[1/4] Checking Redis (Docker)...")
    # try:
    #     subprocess.run("docker-compose up -d redis", shell=True, check=True)
    # except subprocess.CalledProcessError:
    #     print("❌ Failed to start Redis. Is Docker Desktop running?")
    #     return

    processes = []
    
    try:
        # 2. Start Backend
        print(f"\n[1/3] Starting Backend (Port {BACKEND_PORT})...")
        p_backend = run_service(
            [f'"{PYTHON_EXE}"', "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", BACKEND_PORT, "--reload", "--log-level", "warning"],
            cwd="backend"
        )
        processes.append(p_backend)
        time.sleep(2)
        
        # 3. Start Worker
        print("\n[2/3] Starting Worker...")
        p_worker = run_service(
            [f'"{PYTHON_EXE}"', "scheduler.py"],
            cwd="worker"
        )
        processes.append(p_worker)
        
        # 4. Start Frontend
        print(f"\n[3/3] Starting Frontend (Port {FRONTEND_PORT})...")
        p_frontend = run_service(
            [f'"{PYTHON_EXE}"', "app.py"],
            cwd="frontend",
            env_vars={"BACKEND_URL": f"http://127.0.0.1:{BACKEND_PORT}"}
        )
        processes.append(p_frontend)
        
        print("\n✅ All services are running from Virtual Environment!")
        print(f"👉 Dashboard: http://localhost:{FRONTEND_PORT}")
        print("Press Ctrl+C to stop.")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        for p in processes:
            p.terminate()
        print("Done.")

if __name__ == "__main__":
    main()
