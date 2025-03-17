import subprocess
import os
from warnings import catch_warnings


# Application entry point that starts the frontend and backend and spawns subprocesses for them.

class ApplicationHandler:
    def __init__(self):
        self.frontend_dir = "src/frontend"
        self.backend_dir = "src/backend"
        self.root_dir = os.getcwd()
        self.backend_process = None
        self.frontend_process = None

    def run_frontend(self):
        """Run the frontend application."""
        os.chdir(self.frontend_dir)
        print(os.getcwd())
        try:
            # subprocess.run(["npm", "install"], check=True)
            # self.frontend_process = subprocess.run(["npm", "run", "build"], check=True)
            print("test frontend")
        except subprocess.CalledProcessError as e:
            print(e)
        finally:
            os.chdir(self.root_dir)

    def run_backend(self):
        """Run the backend application."""
        os.chdir(self.backend_dir)
        
        print(os.getcwd())
        try:
            # self.backend_process = subprocess.run(["python", "main.py"], check=True)
            print("test")
        except subprocess.CalledProcessError as e:
            print(e)
        finally:
            os.chdir(self.root_dir)

    def run_application(self):
        """Run the application."""
        try:
            self.run_frontend()
            self.run_backend()
        except KeyboardInterrupt:
            self.stop_application()
        

    def stop_application(self):
        """Stop the application."""
        os.chdir(self.root_dir)
        print(os.getcwd())
        if self.frontend_process:
            self.frontend_process.kill()
        if self.backend_process:
            self.backend_process.kill()



if __name__ == "__main__":
    app = ApplicationHandler()
    try:
        app.run_application()
    except KeyboardInterrupt:
        app.stop_application()