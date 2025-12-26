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
    print("🚀 Krapter Proxy Tool - Launcher")
    print("===================================================")
    print("")
    print("⚠️  IMPORTANT NOTICE ⚠️")
    print("")
    print("The application has been migrated to use Docker with PostgreSQL and Redis.")
    print("You cannot run it using 'python start.py' anymore because it requires these services.")
    print("")
    print("👉 Please run the following command instead:")
    print("")
    print("    docker-compose up --build")
    print("")
    print("===================================================")

if __name__ == "__main__":
    main()
