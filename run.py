import subprocess
import os
import sys
from concurrent.futures import ThreadPoolExecutor
import signal
import time

# Application entry point that starts the frontend and backend and spawns subprocesses for them.

# TODO: Still not implemented, to run use two seperate process and run the frontend and backend separately
class ApplicationHandler:
    def __init__(self):
        self.frontend_dir = "src/frontend"
        self.backend_dir = "src/backend"
        self.root_dir = os.getcwd()
        self.processes = []

    def run_frontend(self):
        """Run the frontend application."""
        os.chdir(self.frontend_dir)
        try:
            # Install dependencies if node_modules doesn't exist
            if not os.path.exists("node_modules"):
                subprocess.run(["npm", "install"], check=True)
            
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(("frontend", process))
            print("Frontend started successfully")
            return process
        except subprocess.CalledProcessError as e:
            print(f"Frontend Error: {e}")
        finally:
            os.chdir(self.root_dir)

    def run_backend(self):
        """Run the backend application."""
        os.chdir(self.backend_dir)
        try:
            process = subprocess.Popen(
                ["uvicorn", "main:app", "--reload", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(("backend", process))
            print("Backend started successfully")
            return process
        except subprocess.CalledProcessError as e:
            print(f"Backend Error: {e}")
        finally:
            os.chdir(self.root_dir)

    def run_application(self):
        """Run the application."""
        # Create uploads directory if it doesn't exist
        if not os.path.exists("uploads"):
            os.makedirs("uploads")

        # Start both processes in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            frontend = executor.submit(self.run_frontend)
            backend = executor.submit(self.run_backend)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_application()

    def stop_application(self):
        """Stop the application."""
        print("\nStopping application...")
        for name, process in self.processes:
            if process.poll() is None:  # If process is still running
                print(f"Stopping {name}...")
                if os.name == 'nt':  # Windows
                    process.send_signal(signal.CTRL_C_EVENT)
                else:  # Unix
                    process.send_signal(signal.SIGTERM)
                process.wait()
        print("Application stopped")

if __name__ == "__main__":
    app = ApplicationHandler()
    try:
        app.run_application()
    except KeyboardInterrupt:
        app.stop_application()