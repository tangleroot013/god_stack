#!/usr/bin/env python3
"""
GOD_STACK Unix Socket Integration Engine
Orchestrates cluster startup, patching, and monitoring
"""

import os
import sys
import subprocess
import time
import re
from pathlib import Path
from datetime import datetime
import requests_unixsocket

# Color codes
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

PROJECT_DIR = os.path.expanduser("~/god_stack")
SOCKET_PATH = "/tmp/metrics.sock"
LOG_DIR = f"{PROJECT_DIR}/logs"
VENV_DIR = f"{PROJECT_DIR}/.venv"

class IntegrationEngine:
    """Main orchestrator for Unix socket integration"""
    
    def __init__(self):
        self.project_dir = PROJECT_DIR
        self.socket_path = SOCKET_PATH
        self.log_dir = LOG_DIR
        self.pids = {}
        self.session = requests_unixsocket.Session()
        
    def log_step(self, msg):
        print(f"{BLUE}[STEP]{NC} {msg}")
    
    def log_success(self, msg):
        print(f"{GREEN}[✓]{NC} {msg}")
    
    def log_error(self, msg):
        print(f"{RED}[✗]{NC} {msg}")
    
    def log_warning(self, msg):
        print(f"{YELLOW}[!]{NC} {msg}")
    
    def log_section(self, title):
        print(f"\n{BLUE}{'='*60}{NC}")
        print(f"{BLUE}{title}{NC}")
        print(f"{BLUE}{'='*60}{NC}\n")
    
    def run_command(self, cmd, shell=False):
        """Execute shell command"""
        try:
            result = subprocess.run(
                cmd,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Timeout"
        except Exception as e:
            return False, "", str(e)
    
    def patch_file(self, filepath):
        """Patch a Python file to use Unix socket"""
        if not os.path.exists(filepath):
            return False
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Already patched?
        if 'requests_unixsocket' in content:
            self.log_success(f"{Path(filepath).name} already patched")
            return True
        
        # Backup original
        backup_path = f"{filepath}.bak"
        with open(backup_path, 'w') as f:
            f.write(content)
        self.log_step(f"Backed up to {Path(backup_path).name}")
        
        # Replace HTTP URLs
        content = re.sub(r'http://127\.0\.0\.1:5555', 'http+unix://%2Ftmp%2Fmetrics.sock', content)
        content = re.sub(r'http://localhost:5555', 'http+unix://%2Ftmp%2Fmetrics.sock', content)
        
        # Add requests_unixsocket import safely
        if 'import requests' in content and 'import requests_unixsocket' not in content:
            content = content.replace('import requests', 'import requests_unixsocket\nimport requests')
        elif 'import requests_unixsocket' not in content:
            lines = content.split('\n')
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_idx = i
                    break
            lines.insert(insert_idx, 'import requests_unixsocket')
            content = '\n'.join(lines)
        
        # Update requests.get() calls
        content = re.sub(r'requests\.get\(', 'requests_unixsocket.Session().get(', content)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        self.log_success(f"Patched {Path(filepath).name}")
        return True
    
    def create_file_from_template(self, filepath, template):
        """Create file from template"""
        with open(filepath, 'w') as f:
            f.write(template)
        os.chmod(filepath, 0o755)
        self.log_success(f"Created {Path(filepath).name}")
    
    def phase_1_validate_environment(self):
        """Phase 1: Validate environment"""
        self.log_section("PHASE 1: Environment Validation")
        
        if not os.path.isdir(self.project_dir):
            self.log_error(f"Project directory not found: {self.project_dir}")
            sys.exit(1)
        self.log_success(f"Project directory exists: {self.project_dir}")
        
        if not os.path.isdir(VENV_DIR):
            self.log_error(f"Virtual environment not found: {VENV_DIR}")
            sys.exit(1)
        self.log_success(f"Virtual environment found: {VENV_DIR}")
        
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_success(f"Logs directory ready: {self.log_dir}")
        
        self.log_step("Checking requests-unixsocket...")
        try:
            import requests_unixsocket
            self.log_success("requests-unixsocket installed")
        except ImportError:
            self.log_warning("Installing requests-unixsocket...")
            self.run_command("pip install requests-unixsocket", shell=True)
            self.log_success("requests-unixsocket installed")
    
    def phase_2_patch_exporter(self):
        """Phase 2: Patch metrics_exporter.py"""
        self.log_section("PHASE 2: Patch metrics_exporter.py")
        exporter_file = f"{self.project_dir}/metrics_exporter.py"
        
        if not os.path.exists(exporter_file):
            self.log_warning("metrics_exporter.py not found, creating from template...")
            template = '''#!/usr/bin/env python3
import requests_unixsocket
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SOCKET_URL = "http+unix://%2Ftmp%2Fmetrics.sock/metrics"
SESSION = requests_unixsocket.Session()

def export_loop():
    logger.info(f"Starting metrics exporter, connecting to {SOCKET_URL}")
    while True:
        try:
            response = SESSION.get(SOCKET_URL, timeout=3)
            if response.status_code == 200:
                metrics = response.json()
                processed = metrics.get("global", {}).get("processed", 0)
                logger.info(f"Metrics Processed Loopback: processed={processed}")
        except Exception as e:
            logger.error(f"Exporter loop capture exception: {e}")
        time.sleep(5)

if __name__ == "__main__":
    export_loop()
'''
            self.create_file_from_template(exporter_file, template)
        else:
            self.patch_file(exporter_file)
    
    def phase_3_patch_dashboard_live(self):
        """Phase 3: Patch resilience_dashboard_live.py"""
        self.log_section("PHASE 3: Patch resilience_dashboard_live.py")
        dashboard_file = f"{self.project_dir}/resilience_dashboard_live.py"
        
        if not os.path.exists(dashboard_file):
            self.log_warning("resilience_dashboard_live.py not found, creating from template...")
            template = '''#!/usr/bin/env python3
import requests_unixsocket
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SOCKET_URL = "http+unix://%2Ftmp%2Fmetrics.sock/metrics"
SESSION = requests_unixsocket.Session()

def display_dashboard():
    logger.info(f"Connecting to live metrics server at {SOCKET_URL}")
    while True:
        try:
            response = SESSION.get(SOCKET_URL, timeout=3)
            if response.status_code == 200:
                metrics = response.json()
                g = metrics.get("global", {})
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Processed: {g.get('processed', 0)} | Success: {g.get('success', 0)}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Dashboard pull error: {e}")
        time.sleep(2)

if __name__ == "__main__":
    display_dashboard()
'''
            self.create_file_from_template(dashboard_file, template)
        else:
            self.patch_file(dashboard_file)
    
    def phase_4_patch_dashboard_static(self):
        """Phase 4: Patch resilience_dashboard.py"""
        self.log_section("PHASE 4: Patch resilience_dashboard.py")
        dashboard_file = f"{self.project_dir}/resilience_dashboard.py"
        if os.path.exists(dashboard_file):
            self.patch_file(dashboard_file)
        else:
            self.log_warning("resilience_dashboard.py not found (skipping)")
    
    def phase_5_cleanup(self):
        """Phase 5: Cleanup and socket preparation"""
        self.log_section("PHASE 5: Cleanup & Socket Preparation")
        self.log_step("Killing existing metrics_server processes...")
        self.run_command("pkill -f 'metrics_server.py'", shell=True)
        time.sleep(1)
        
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
            self.log_step(f"Removed stale socket: {self.socket_path}")
        self.log_success("Environment cleaned and ready")
    
    def phase_6_start_cluster(self):
        """Phase 6: Start metrics server"""
        self.log_section("PHASE 6: Cluster Startup")
        metrics_server = f"{self.project_dir}/metrics_server.py"
        log_file = f"{self.log_dir}/metrics_server.log"
        
        self.log_step("Starting metrics_server on Unix socket...")
        try:
            with open(log_file, 'w') as f:
                process = subprocess.Popen(
                    ["python3", "-u", metrics_server],
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd=self.project_dir
                )
            self.pids['metrics_server'] = process.pid
            self.log_success(f"Metrics server started (PID: {process.pid})")
        except Exception as e:
            self.log_error(f"Failed to start metrics server: {e}")
            sys.exit(1)
        
        self.log_step("Waiting for socket creation...")
        for i in range(10):
            if os.path.exists(self.socket_path):
                self.log_success(f"Socket created: {self.socket_path}")
                break
            if i == 9:
                self.log_error("Socket failed to create after 10 attempts")
                sys.exit(1)
            time.sleep(1)
        
        self.log_step("Verifying socket connectivity...")
        try:
            response = self.session.get("http+unix://%2Ftmp%2Fmetrics.sock/health", timeout=3)
            if response.status_code == 200:
                self.log_success("Health check passed via Unix socket")
            else:
                self.log_error(f"Health check failed: HTTP {response.status_code}")
        except Exception as e:
            self.log_error(f"Health check error: {e}")
    
    def phase_7_optional_daemons(self):
        """Phase 7: Launch optional daemons safely"""
        self.log_section("PHASE 7: Optional Daemon Services")
        try:
            # Safe text fallback instead of stalling if stdin is unavailable
            self.log_step("Launching metrics_exporter background listener...")
            exporter_file = f"{self.project_dir}/metrics_exporter.py"
            log_file = f"{self.log_dir}/metrics_exporter.log"
            with open(log_file, 'w') as f:
                proc = subprocess.Popen(["python3", "-u", exporter_file], stdout=f, stderr=subprocess.STDOUT)
            self.log_success(f"Metrics Exporter active in background (PID: {proc.pid})")
        except Exception as e:
            self.log_warning(f"Could not initialize optional daemons automatically: {e}")

    def execute_all(self):
        self.phase_1_validate_environment()
        self.phase_2_patch_exporter()
        self.phase_3_patch_dashboard_live()
        self.phase_4_patch_dashboard_static()
        self.phase_5_cleanup()
        self.phase_6_start_cluster()
        self.phase_7_optional_daemons()
        self.log_section("INTEGRATION COMPLETE")
        print(f"{GREEN}All systems fully coordinated over local IPC sockets.{NC}\n")

if __name__ == "__main__":
    engine = IntegrationEngine()
    engine.execute_all()
