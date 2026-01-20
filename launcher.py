import tkinter as tk
from tkinter import scrolledtext, messagebox
from PIL import Image, ImageTk 
import threading
import subprocess
import time
import webbrowser
import sys
import os
import msal
import ctypes
from dotenv import load_dotenv

PIPELINE_INTERVAL_SECONDS = 3600
OPEN_BROWSER = True             

class WhySoSeriousLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Why So Serious? - System Monitor")
        self.root.geometry("700x800")
        self.root.configure(bg="#1a1a1a")

        try:
            myappid = 'hp.scds.whysoserious.launcher.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except:
            pass
        
        try:
            image_path = os.path.join("img", "logo.jpg")
            if not os.path.exists(image_path):
                image_path = "logo.jpg" 

            if os.path.exists(image_path):
                img_raw = Image.open(image_path)
                
                icon_photo = ImageTk.PhotoImage(img_raw)
                self.root.iconphoto(True, icon_photo)
                
                img_resized = img_raw.resize((150, 150), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img_resized)
                tk.Label(root, image=self.logo_img, bg="#1a1a1a").pack(pady=20)
        except Exception as e:
            print(f"Image load error: {e}")

        tk.Label(root, text="WHY SO SERIOUS?", font=("Chiller", 36, "bold"), 
                 fg="#e74c3c", bg="#1a1a1a").pack()
        
        self.status_label = tk.Label(root, text="System Status: INITIALIZING...", 
                                   font=("Arial", 12, "bold"), fg="#f1c40f", bg="#1a1a1a")
        self.status_label.pack(pady=10)

        self.log_area = scrolledtext.ScrolledText(root, width=80, height=25, 
                                                font=("Consolas", 9), 
                                                bg="black", fg="#2ecc71", 
                                                insertbackground="white")
        self.log_area.pack(pady=10, padx=20)

        self.stop_btn = tk.Button(root, text="SHUTDOWN SYSTEM", 
                                command=self.stop_system,
                                font=("Arial", 12, "bold"),
                                bg="#e74c3c", fg="white", 
                                width=20, height=2, cursor="hand2", relief="flat")
        self.stop_btn.pack(pady=20)

        self.running = True
        
        self.root.after(1000, lambda: threading.Thread(target=self.main_sequence, daemon=True).start())

    def log(self, message):
        def _append():
            self.log_area.insert(tk.END, f">> {message}\n")
            self.log_area.see(tk.END)
        self.root.after(0, _append)

    def load_environment_variables(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_env = os.path.join(current_dir, 'Backend', '.env')
        root_env = os.path.join(current_dir, '.env')

        if os.path.exists(backend_env):
            load_dotenv(backend_env)
        elif os.path.exists(root_env):
            load_dotenv(root_env)

    def authenticate_user(self):
        self.load_environment_variables()
        self.log("Checking authentication...")

        CLIENT_ID = os.getenv("AZURE_CLIENT_ID") or os.getenv("CLIENT_ID")
        TENANT_ID = os.getenv("AZURE_TENANT_ID") or os.getenv("TENANT_ID")

        if not CLIENT_ID or not TENANT_ID:
            self.log("Error: Missing Client/Tenant ID in .env")
            return None

        AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
        SCOPES = ["User.Read", "Team.ReadBasic.All", "ChannelMessage.Read.All", "Group.Read.All"]

        app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

        accounts = app.get_accounts()
        if accounts:
            result = app.acquire_token_silent(SCOPES, account=accounts[0])
            if result: 
                self.log("Auto-login successful.")
                return result['access_token']

        self.log("Authentication required. Opening browser...")
        try:
            result = app.acquire_token_interactive(scopes=SCOPES)
        except:
            flow = app.initiate_device_flow(scopes=SCOPES)
            self.log(f"Go to: {flow['verification_uri']}")
            self.log(f"Enter Code: {flow['user_code']}")
            webbrowser.open(flow['verification_uri'])
            result = app.acquire_token_by_device_flow(flow)

        if "access_token" in result:
            self.log("Login successful!")
            return result['access_token']
        else:
            self.log(f"Login failed: {result.get('error_description')}")
            return None

    def run_backend(self):
        self.log("Starting Backend (API)...")
        subprocess.run(["uvicorn", "app.main:app", "--reload"], cwd="Backend", env=os.environ)

    def run_frontend(self):
        self.log("Starting Frontend...")
        subprocess.run(["npm", "run", "dev"], cwd="Frontend", shell=True)

    def execute_pipeline_script(self):
        try:
            self.log("Running message analysis...")
            result = subprocess.run(
                ["python", "run_pipeline.py"], 
                cwd="Backend",
                capture_output=True,
                text=True,
                env=os.environ
            )
            
            if result.returncode == 0:
                self.log("Analysis completed successfully.")
                return True
            else:
                self.log("Analysis error:")
                self.log(result.stderr)
                return False
        except Exception as e:
            self.log(f"Critical error: {e}")
            return False

    def run_pipeline_loop(self):
        self.log(f"Pipeline loop started (Interval: {PIPELINE_INTERVAL_SECONDS}s)")
        time.sleep(PIPELINE_INTERVAL_SECONDS)
        
        while self.running:
            self.execute_pipeline_script()
            self.log(f"Waiting {PIPELINE_INTERVAL_SECONDS}s...")
            time.sleep(PIPELINE_INTERVAL_SECONDS)

    def main_sequence(self):
        token = self.authenticate_user()
        if token:
            os.environ["HEADLESS_TOKEN"] = token
        else:
            self.log("Starting in OFFLINE mode (No Teams connection).")

        self.status_label.config(text="System Status: STARTING...", fg="#f39c12")

        threading.Thread(target=self.run_backend, daemon=True).start()
        
        self.log("Waiting 5s for Backend initialization...")
        time.sleep(5)

        self.log("Performing INITIAL ANALYSIS...")
        self.execute_pipeline_script()

        threading.Thread(target=self.run_frontend, daemon=True).start()

        threading.Thread(target=self.run_pipeline_loop, daemon=True).start()

        self.status_label.config(text="System Status: RUNNING", fg="#2ecc71")

        if OPEN_BROWSER:
            time.sleep(3)
            self.log("Opening Dashboard...")
            webbrowser.open("http://localhost:5173")

    def stop_system(self):
        if messagebox.askokcancel("Shutdown", "Stop all services and exit?"):
            self.running = False
            self.log("The show is over... for now. Smile")
            self.root.after(1000, lambda: sys.exit(0))

if __name__ == "__main__":
    root = tk.Tk()
    app = WhySoSeriousLauncher(root)
    root.mainloop()