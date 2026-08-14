"""
SERA Remote Operations — Execute commands and file operations on LAN machines.
MERGED FROM JULIUS → SERA PLATFORM
Supports SMB (Windows admin shares), WinRM/PowerShell Remoting, SSH, and PsExec.
"""

import os
import uuid
import logging
import socket
import subprocess
import platform
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, AsyncGenerator

# Add Sera paths
SERA_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SERA_ROOT))

# Sera-specific imports
try:
    from config import settings
    SERA_CONFIG = settings
except ImportError:
    SERA_CONFIG = None

try:
    from database.db import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Setup Sera logging
LOG_DIR = SERA_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'sera_remote_ops.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sera_remote_ops")

# ── Stored Credentials for Remote Targets ──
_CREDS_FILE = SERA_ROOT / "database" / "remote_creds.json"
_CREDS_FILE.parent.mkdir(exist_ok=True)

def get_stored_credentials(target: str) -> tuple:
    """Get stored username/password for a target IP."""
    try:
        if _CREDS_FILE.exists():
            with open(_CREDS_FILE, "r") as f:
                creds = json.load(f)
            if target in creds:
                return creds[target].get("username"), creds[target].get("password")
            if "*" in creds:
                return creds["*"].get("username"), creds["*"].get("password")
    except Exception:
        pass
    return None, None

def store_credentials(target: str, username: str, password: str) -> bool:
    """Store credentials for a target IP."""
    try:
        creds: Dict[str, Any] = {}
        if _CREDS_FILE.exists():
            with open(_CREDS_FILE, "r") as f:
                creds = json.load(f)
        creds[target] = {"username": username, "password": password}
        with open(_CREDS_FILE, "w") as f:
            json.dump(creds, f, indent=2)
        logger.info(f"Stored credentials for {target}")
        
        # Audit log
        audit_file = LOG_DIR / f"remote_creds_{datetime.now().strftime('%Y%m%d')}.log"
        with open(audit_file, 'a') as f:
            f.write(json.dumps({
                "action": "store_creds",
                "target": target,
                "timestamp": datetime.now().isoformat()
            }) + '\n')
        return True
    except Exception as e:
        logger.warning(f"Failed to store credentials: {e}")
        return False

def _resolve_credentials(target: str, username: Optional[str] = None, 
                         password: Optional[str] = None) -> tuple:
    """Resolve credentials: use provided ones, fall back to stored."""
    if username and password:
        return username, password
    stored_user, stored_pass = get_stored_credentials(target)
    return (username or stored_user, password or stored_pass)

def safe_strip(text: str) -> str:
    """Safely strip whitespace from string"""
    if not text:
        return ""
    return str(text).strip()

# ── WinRM Setup ──
_winrm_setup_done = False

def _ensure_local_winrm():
    """Ensure WinRM is configured on THIS machine."""
    global _winrm_setup_done
    if _winrm_setup_done:
        return
    try:
        if platform.system() == "Windows":
            # Check if WinRM service is running
            svc_check = subprocess.run(
                ["sc", "query", "WinRM"], capture_output=True, text=True, timeout=5
            )
            if "RUNNING" not in svc_check.stdout:
                subprocess.run(["sc", "start", "WinRM"], capture_output=True, text=True, timeout=10)
                logger.info("WinRM service started")

            # Set TrustedHosts
            subprocess.run(
                ["winrm", "set", "winrm/config/client", '@{TrustedHosts="*"}'],
                capture_output=True, text=True, timeout=10
            )
            logger.info("Local WinRM TrustedHosts configured")
        _winrm_setup_done = True
    except Exception as e:
        logger.debug(f"WinRM local setup skipped: {e}")
        _winrm_setup_done = True

# ── Remote Operations ──

def execute_winrm(target_ip: str, username: str, password: str, 
                  command: str, timeout: int = 60) -> Dict[str, Any]:
    """
    Execute a command on a remote machine via WinRM.
    """
    result = {
        "success": False,
        "output": "",
        "error": "",
        "method": "WinRM",
        "target": target_ip
    }

    if not all([target_ip, username, password, command]):
        result["error"] = "Missing required parameter"
        return result

    try:
        import winrm
    except ImportError:
        result["error"] = "winrm library not installed. Run: pip install pywinrm"
        return result

    target_ip = safe_strip(target_ip)
    username = safe_strip(username)
    command = safe_strip(command)

    # Try multiple WinRM authentication methods
    methods = [
        ("ntlm", "http"),
        ("basic", "http"),
        ("ntlm", "https"),
    ]

    errors = []
    for auth, protocol in methods:
        try:
            session = winrm.Session(
                f"{protocol}://{target_ip}:5985/wsman",
                auth=(username, password),
                transport=auth,
                read_timeout_sec=timeout,
                operation_timeout_sec=timeout - 5
            )
            response = session.run_ps(command)

            stdout = safe_strip(response.std_out) if response else ""
            stderr = safe_strip(response.std_err) if response else ""

            if response and response.status_code == 0:
                result["success"] = True
                result["output"] = stdout
                result["method"] = f"WinRM_{auth}"
                logger.info(f"WinRM {auth} succeeded on {target_ip}")
                return result
            else:
                errors.append(f"{auth}: exit {response.status_code if response else 'None'}")
        except Exception as e:
            errors.append(f"{auth}: {str(e)}")
            continue

    result["error"] = " | ".join(errors)
    return result

def execute_ssh(target_ip: str, username: str, password: str, 
                command: str, port: int = 22) -> Dict[str, Any]:
    """Execute command via SSH."""
    result = {
        "success": False,
        "output": "",
        "error": "",
        "method": "SSH",
        "target": target_ip
    }

    try:
        import paramiko
    except ImportError:
        result["error"] = "paramiko not installed. Run: pip install paramiko"
        return result

    if not all([target_ip, username, password, command]):
        result["error"] = "Missing required parameter"
        return result

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=safe_strip(target_ip),
            port=port,
            username=safe_strip(username),
            password=password,
            timeout=30
        )

        stdin, stdout, stderr = client.exec_command(safe_strip(command), timeout=60)

        output = safe_strip(stdout.read().decode('utf-8', errors='ignore'))
        error = safe_strip(stderr.read().decode('utf-8', errors='ignore'))
        exit_code = stdout.channel.recv_exit_status()

        client.close()

        if exit_code == 0:
            result["success"] = True
            result["output"] = output
        else:
            result["error"] = error or f"Exit code: {exit_code}"

    except Exception as e:
        result["error"] = f"SSH: {str(e)}"

    return result

def execute_on_remote(target_ip: str, username: str, password: str, 
                      command: str) -> Dict[str, Any]:
    """
    Master function: Try all methods to execute a command on a remote machine.
    """
    if not target_ip:
        return {"success": False, "error": "Target IP is None or empty", 
                "output": "", "method": "none"}

    # Try WinRM first (Windows targets)
    _ensure_local_winrm()
    winrm_result = execute_winrm(target_ip, username, password, command)
    if winrm_result["success"]:
        return winrm_result

    # Try SSH as fallback
    ssh_result = execute_ssh(target_ip, username, password, command)
    if ssh_result["success"]:
        return ssh_result

    # All methods failed
    return {
        "success": False,
        "output": "",
        "error": f"All methods failed on {target_ip}: WinRM: {winrm_result['error']} | SSH: {ssh_result['error']}",
        "method": "none",
        "target": target_ip
    }

def create_remote_folder(target: str, remote_path: str, 
                         username: Optional[str] = None, 
                         password: Optional[str] = None) -> Dict[str, Any]:
    """Create a folder on a remote machine."""
    username, password = _resolve_credentials(target, username, password)
    
    if not username or not password:
        return {"success": False, "error": "Credentials required for remote folder creation"}
    
    ps_cmd = f'New-Item -Path "{remote_path}" -ItemType Directory -Force -ErrorAction Stop | Out-Null'
    result = execute_on_remote(target, username, password, ps_cmd)
    
    if result["success"]:
        # Verify folder exists
        verify_cmd = f'Test-Path "{remote_path}"'
        verify_result = execute_on_remote(target, username, password, verify_cmd)
        if verify_result["success"] and verify_result["output"].strip().lower() == "true":
            return {"success": True, "path": remote_path, "method": result.get("method", "unknown")}
    
    return result

def execute_remote_command(target: str, command: str, 
                          username: Optional[str] = None, 
                          password: Optional[str] = None) -> Dict[str, Any]:
    """Execute a command on a remote machine."""
    username, password = _resolve_credentials(target, username, password)
    return execute_on_remote(target, username, password, command)

async def execute_remote_command_stream(target: str, command: str,
                                        username: Optional[str] = None,
                                        password: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Execute a command on a remote machine and stream output."""
    username, password = _resolve_credentials(target, username, password)
    _ensure_local_winrm()

    if username and password:
        ps_script = (
            f'$ErrorActionPreference = "Stop"; '
            f'$pw = ConvertTo-SecureString "{password}" -AsPlainText -Force; '
            f'$cred = New-Object System.Management.Automation.PSCredential("{username}", $pw); '
            f'Invoke-Command -ComputerName {target} -Credential $cred '
            f'-Authentication Negotiate -ScriptBlock {{ {command} }} | Out-String -Stream'
        )
    else:
        ps_script = (
            f'$ErrorActionPreference = "Stop"; '
            f'Invoke-Command -ComputerName {target} -ScriptBlock {{ {command} }} | Out-String -Stream'
        )

    try:
        process = await asyncio.create_subprocess_exec(
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if process.stdout:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                yield line.decode('utf-8', errors='replace')

        if process.stderr:
            err = await process.stderr.read()
            if err:
                yield err.decode('utf-8', errors='replace')

        await process.wait()
    except Exception as e:
        yield f"Stream Execution Error: {str(e)}\n"

def verify_remote_path(target: str, remote_path: str,
                      username: Optional[str] = None,
                      password: Optional[str] = None) -> Dict[str, Any]:
    """Check if a file or folder exists on a remote machine."""
    username, password = _resolve_credentials(target, username, password)
    
    if not username or not password:
        return {"exists": False, "error": "Credentials required"}
    
    ps_cmd = f'Test-Path "{remote_path}"'
    result = execute_on_remote(target, username, password, ps_cmd)
    
    if result["success"]:
        exists = result["output"].strip().lower() == "true"
        return {"exists": exists, "path": remote_path}
    
    return {"exists": False, "error": result.get("error", "Verification failed")}

def list_remote_folder(target: str, remote_path: str,
                      username: Optional[str] = None,
                      password: Optional[str] = None) -> Dict[str, Any]:
    """List contents of a folder on a remote machine."""
    username, password = _resolve_credentials(target, username, password)
    
    if not username or not password:
        return {"success": False, "error": "Credentials required"}
    
    ps_cmd = f'Get-ChildItem -Path "{remote_path}" -Force | Select-Object Name, Mode, Length, LastWriteTime | Format-Table -AutoSize | Out-String -Width 200'
    result = execute_on_remote(target, username, password, ps_cmd)
    
    if result["success"]:
        return {"success": True, "contents": result.get("output", "(empty)")}
    
    return {"success": False, "error": result.get("error", "List failed")}

def launch_interactive_app_on_remote(target: str, username: str, password: str,
                                    app_command: str) -> Dict[str, Any]:
    """Launch a GUI application on a remote machine's interactive desktop."""
    if not app_command:
        return {"success": False, "error": "App command is empty"}
    
    username, password = _resolve_credentials(target, username, password)
    
    if not username or not password:
        return {"success": False, "error": "Credentials required"}
    
    task_name = f"JuliusLaunch_{uuid.uuid4().hex[:8]}"
    
    ps_command = f'''
$cmd = '{app_command}'
$tn = "{task_name}"
$user = "{username}"
$pass = "{password}"

# Browser path detection
if ($cmd -ilike "brave*") {{
    $paths = @(
        "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
        "C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
        "$env:LOCALAPPDATA\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
    )
    foreach ($p in $paths) {{ if (Test-Path $p) {{ $cmd = $p; break }} }}
}}
elseif ($cmd -ilike "chrome*") {{
    $paths = @(
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "$env:LOCALAPPDATA\\Google\\Chrome\\Application\\chrome.exe"
    )
    foreach ($p in $paths) {{ if (Test-Path $p) {{ $cmd = $p; break }} }}
}}
elseif ($cmd -ilike "edge*") {{
    $paths = @(
        "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
        "$env:LOCALAPPDATA\\Microsoft\\Edge\\Application\\msedge.exe"
    )
    foreach ($p in $paths) {{ if (Test-Path $p) {{ $cmd = $p; break }} }}
}}

# Create interactive task
$trValue = "`"$cmd`""
$create = & schtasks /create /f /sc ONCE /st 00:00 /tn $tn /tr $trValue /ru $user /rp $pass /it
if ($LASTEXITCODE -ne 0) {{ 
    Write-Error "Failed to create interactive task"
    exit 1 
}}

$run = & schtasks /run /tn $tn
if ($LASTEXITCODE -ne 0) {{ 
    schtasks /delete /f /tn $tn | Out-Null
    Write-Error "Failed to run interactive task"
    exit 1 
}}

Start-Sleep -s 3
$procName = [System.IO.Path]::GetFileNameWithoutExtension($cmd)
$proc = Get-Process $procName -ErrorAction SilentlyContinue | Select-Object -First 1

if ($proc) {{
    Write-Output "SUCCESS: $cmd is running (PID: $($proc.Id))"
}} else {{
    Write-Output "WARNING: Task reported success, but process not found"
}}

schtasks /delete /f /tn $tn | Out-Null
'''
    
    result = execute_on_remote(target, username, password, ps_command)
    return result

# Sera API Functions
def get_remote_status(target: str) -> Dict[str, Any]:
    """Check if remote machine is reachable"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((target, 445))  # SMB port
        sock.close()
        
        if result == 0:
            return {"status": "online", "port": 445, "service": "SMB"}
        else:
            return {"status": "offline", "error": "Port 445 not reachable"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    print("Sera Remote Operations loaded")
