#!/usr/bin/env python3
"""
linux_shell.py - Built-in Linux terminal capabilities for Sera
MERGED FROM JULIUS → SERA PLATFORM

Features:
- Persistent session with working directory tracking
- Command history with output capture
- Package management (apt, yum, pacman detection)
- Safety guardrails for destructive commands
- Full Sera integration with auth and audit
- Script execution support
"""

import os
import re
import json
import logging
import subprocess
import platform
import time
import uuid
import threading
import shlex
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Add Sera paths
SERA_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SERA_ROOT))

# Sera-specific imports
try:
    from config import settings
    SERA_CONFIG = settings
except ImportError:
    SERA_CONFIG = None

# Setup Sera logging
LOG_DIR = SERA_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'sera_linux_shell.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sera_linux_shell")

# ═══════════════════════════════════════════════════════════════════════════
# Shell Environment Detection (from Julius)
# ═══════════════════════════════════════════════════════════════════════════

_system = platform.system()
_is_windows = _system == "Windows"
_shell_backend = None
_wsl_distro = None

def _find_git_bash() -> Optional[str]:
    """Find Git Bash executable on Windows."""
    paths = [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Git\bin\bash.exe"),
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

# PowerShell translations for Windows fallback
_PS_TRANSLATIONS = {
    "ls": "Get-ChildItem",
    "pwd": "Get-Location",
    "whoami": "$env:USERNAME",
    "hostname": "$env:COMPUTERNAME",
    "cat": "Get-Content",
    "echo": "Write-Output",
    "mkdir": "New-Item -ItemType Directory -Force -Path",
    "rmdir": "Remove-Item -Recurse -Force -Path",
    "cp": "Copy-Item",
    "mv": "Move-Item",
    "rm": "Remove-Item -Force",
    "touch": "New-Item -ItemType File -Force -Path",
    "clear": "Clear-Host",
    "date": "Get-Date",
    "ps": "Get-Process",
    "kill": "Stop-Process -Id",
    "curl": "Invoke-WebRequest -Uri",
    "wget": "Invoke-WebRequest -OutFile",
    "ping": "Test-Connection",
    "ipconfig": "Get-NetIPAddress",
    "ifconfig": "Get-NetIPAddress",
    "netstat": "Get-NetTCPConnection",
    "df": "Get-PSDrive -PSProvider FileSystem",
    "free": "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory",
    "uname": 'Write-Output "Windows $([System.Environment]::OSVersion.Version)"',
    "uptime": "(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime | Format-Table Days,Hours,Minutes",
}

def _translate_to_powershell(command: str) -> str:
    """Translate basic Linux commands to PowerShell equivalents."""
    cmd = safe_strip(command)

    if cmd in _PS_TRANSLATIONS:
        return _PS_TRANSLATIONS[cmd]

    parts = cmd.split(None, 1)
    if parts and parts[0] in _PS_TRANSLATIONS:
        ps_cmd = _PS_TRANSLATIONS[parts[0]]
        args = parts[1] if len(parts) > 1 else ""
        args = re.sub(r'\s*-[a-z]+', '', args)
        return f"{ps_cmd} {args}".strip()

    return cmd

def safe_strip(text: str) -> str:
    """Safely strip whitespace from string"""
    if not text:
        return ""
    return str(text).strip()

def _detect_shell() -> str:
    """Detect the best available Linux shell backend (from Julius)"""
    global _shell_backend, _wsl_distro

    if _is_windows:
        # Check WSL
        try:
            list_result = subprocess.run(
                ["wsl", "--list", "--quiet"],
                capture_output=True, text=True, timeout=5
            )
            raw = safe_strip(list_result.stdout.replace("\x00", ""))
            distros = [safe_strip(d) for d in raw.splitlines() if safe_strip(d)]
            real_distros = [d for d in distros if "docker" not in d.lower()]

            if real_distros:
                try:
                    test = subprocess.run(
                        ["wsl", "-d", real_distros[0], "--", "echo", "julius_ok"],
                        capture_output=True, text=True, timeout=8
                    )
                    if "julius_ok" in test.stdout:
                        _shell_backend = "wsl"
                        _wsl_distro = real_distros[0]
                        logger.info(f"Linux shell: WSL distro '{_wsl_distro}' detected")
                        return "wsl"
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    pass
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Check Git Bash
        git_bash = _find_git_bash()
        if git_bash and os.path.exists(git_bash):
            _shell_backend = "git-bash"
            logger.info(f"Linux shell: Git Bash detected at {git_bash}")
            return "git-bash"

        # PowerShell fallback
        _shell_backend = "powershell"
        logger.info("Linux shell: No WSL/Git Bash found, using PowerShell fallback")
        return "powershell"
    else:
        # Linux/macOS
        if os.path.exists("/bin/bash"):
            _shell_backend = "bash"
        elif os.path.exists("/bin/sh"):
            _shell_backend = "sh"
        else:
            _shell_backend = "sh"
        return _shell_backend

# Auto-detect on import
_detect_shell()

# ═══════════════════════════════════════════════════════════════════════════
# Sera Session Management
# ═══════════════════════════════════════════════════════════════════════════

class SeraShellSession:
    """Tracks a persistent shell session with Sera integration"""
    
    def __init__(self, session_id: str = "default", user_id: Optional[str] = None):
        self.session_id = session_id
        self.user_id = user_id or "system"
        self.cwd = "~"
        self.history: List[Dict[str, Any]] = []
        self.env: Dict[str, str] = {}
        self.created_at = datetime.utcnow().isoformat()
        self.last_used = self.created_at
        self.is_authorized = True
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "cwd": self.cwd,
            "history_count": len(self.history),
            "created_at": self.created_at,
            "last_used": self.last_used,
            "backend": _shell_backend,
            "is_authorized": self.is_authorized
        }

# Session storage with Sera authentication
_sessions: Dict[str, SeraShellSession] = {}

def get_session(session_id: str = "default", user_id: Optional[str] = None) -> SeraShellSession:
    """Get or create a shell session with Sera user context"""
    if session_id not in _sessions:
        _sessions[session_id] = SeraShellSession(session_id, user_id)
    
    session = _sessions[session_id]
    session.last_used = datetime.utcnow().isoformat()
    
    # Update user_id if provided
    if user_id:
        session.user_id = user_id
    
    return session

def get_all_sessions() -> Dict[str, Dict]:
    """Get all active sessions for Sera monitoring"""
    return {sid: session.to_dict() for sid, session in _sessions.items()}

# ═══════════════════════════════════════════════════════════════════════════
# Command Execution with Sera Integration
# ═══════════════════════════════════════════════════════════════════════════

# Dangerous patterns (from Julius)
DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/(?!\S)",
    r"mkfs\.",
    r"dd\s+if=.*of=/dev/",
    r":\(\)\{\s*:\|:\s*&\s*\};:",
    r"chmod\s+-R\s+777\s+/",
    r"shutdown",
    r"reboot",
    r"init\s+0",
]

# Interactive commands that hang (from Julius)
INTERACTIVE_COMMANDS = {
    "su", "sudo su", "sudo -i", "sudo -s", "bash", "sh", "zsh",
    "fish", "csh", "tcsh", "ksh", "dash", "python", "python3",
    "node", "irb", "mysql", "psql", "mongo", "redis-cli",
    "ssh", "telnet", "ftp", "ncat", "nc",
    "msfconsole", "sqlmap", "katoolin3", "sudo katoolin3",
}

def _auto_fix_command(command: str) -> str:
    """Auto-fix commands to be non-interactive (from Julius)"""
    cmd = safe_strip(command)
    if 'add-apt-repository' in cmd and '-y' not in cmd:
        cmd = cmd.replace('add-apt-repository', 'add-apt-repository -y')
    if 'apt-get' in cmd and '-y' not in cmd and 'install' in cmd:
        cmd = cmd.replace('apt-get install', 'apt-get install -y')
    if 'apt install' in cmd and '-y' not in cmd:
        cmd = cmd.replace('apt install', 'apt install -y')
    if 'apt update' in cmd and cmd.endswith('apt update'):
        cmd = cmd.replace('apt update', 'apt update -qq')
    return cmd

def _is_dangerous(command: str) -> Optional[str]:
    """Check if a command is potentially destructive (from Julius)"""
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command):
            return f"Command matches dangerous pattern: {pattern}"
    return None

def execute_linux(command: str, session_id: str = "default",
                  timeout: int = 30, allow_dangerous: bool = False,
                  user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute a Linux command with Sera integration.
    
    On Windows: routes through WSL/Git Bash/PowerShell.
    On Linux/macOS: runs natively via bash.
    """
    session = get_session(session_id, user_id)
    session.last_used = datetime.utcnow().isoformat()
    start_time = time.time()

    result = {
        "command": command,
        "success": False,
        "output": "",
        "error": "",
        "exit_code": -1,
        "backend": _shell_backend,
        "cwd": session.cwd,
        "duration_ms": 0,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": session.user_id,
        "session_id": session_id
    }

    # Safety check (from Julius)
    if not allow_dangerous:
        danger = _is_dangerous(command)
        if danger:
            result["error"] = f"⚠️ BLOCKED: {danger}. Use allow_dangerous=True to override."
            result["exit_code"] = -2
            session.history.append(result)
            return result

    # Block interactive commands (from Julius)
    cmd_stripped = safe_strip(command).rstrip(";")
    if cmd_stripped in INTERACTIVE_COMMANDS:
        result["error"] = (
            f"⚠️ '{cmd_stripped}' opens an interactive shell and cannot run in this terminal.\n"
            f"You are already running as root. Just type your commands directly."
        )
        result["exit_code"] = -2
        session.history.append(result)
        return result

    # Strip sudo prefix if using WSL (from Julius)
    if _shell_backend == "wsl" and safe_strip(command).startswith("sudo "):
        command = safe_strip(command)[5:]

    # Auto-fix interactive prompts (from Julius)
    command = _auto_fix_command(command)

    # Check backend availability
    if _shell_backend is None:
        result["error"] = (
            "No Linux shell available.\n\n"
            "On Windows, install WSL:\n"
            "  1. Open PowerShell as Admin\n"
            "  2. Run: wsl --install\n"
            "  3. Restart your computer\n"
            "  4. Set up a Linux username/password\n\n"
            "Or install Git Bash from: https://git-scm.com/downloads"
        )
        session.history.append(result)
        return result

    try:
        # Build the full command with cd to session's working directory
        cd_match = re.match(r'^\s*cd\s+(.*)', safe_strip(command))

        # Trailer to capture working directory
        _cwd_trailer = '\n_JULIUS_RC=$?; echo "___JULIUS_CWD___"; pwd; exit $_JULIUS_RC'

        if _shell_backend == "wsl":
            full_cmd = f'cd {session.cwd} 2>/dev/null; {command}'
            full_cmd += _cwd_trailer
            wsl_cmd = ["wsl"]
            if _wsl_distro:
                wsl_cmd += ["-d", _wsl_distro]
            wsl_cmd += ["-u", "root"]
            cmd_args = wsl_cmd + ["--", "bash", "-c", full_cmd]

        elif _shell_backend == "git-bash":
            git_bash = _find_git_bash()
            if not git_bash:
                raise FileNotFoundError("Git Bash not found")
            full_cmd = f'cd {session.cwd} 2>/dev/null; {command}'
            full_cmd += _cwd_trailer
            cmd_args = [git_bash, "-c", full_cmd]

        elif _shell_backend == "powershell":
            ps_cmd = _translate_to_powershell(command)
            cmd_args = ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd]

        elif _shell_backend in ("bash", "sh"):
            shell = f"/bin/{_shell_backend}"
            full_cmd = f'cd {session.cwd} 2>/dev/null; {command}'
            full_cmd += _cwd_trailer
            cmd_args = [shell, "-c", full_cmd]
        else:
            result["error"] = f"Unknown backend: {_shell_backend}"
            session.history.append(result)
            return result

        # Execute command
        proc = subprocess.Popen(
            cmd_args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env={**os.environ, **session.env}
        )

        # Pre-insert into history for live streaming
        session.history.append(result)
        if len(session.history) > 100:
            session.history = session.history[-100:]

        raw_output = []
        timeout_expired = False

        def read_output():
            try:
                for line in proc.stdout:
                    raw_output.append(line)
                    current_out = "".join(raw_output)
                    if "___JULIUS_CWD___" in current_out:
                        current_out = current_out.split("___JULIUS_CWD___")[0]
                    result["output"] = current_out.rstrip("\n")
            except Exception:
                pass

        t = threading.Thread(target=read_output, daemon=True)
        t.start()

        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timeout_expired = True
            proc.kill()

        t.join(timeout=1)

        raw_output_str = "".join(raw_output)
        output_parts = raw_output_str.rsplit("___JULIUS_CWD___\n", 1)

        if len(output_parts) == 2:
            result["output"] = output_parts[0].rstrip("\n")
            new_cwd = safe_strip(output_parts[1])
            if new_cwd:
                session.cwd = new_cwd
                result["cwd"] = new_cwd
        else:
            result["output"] = raw_output_str.rstrip("\n")

        if timeout_expired:
            result["error"] = f"Command timed out after {timeout}s"
            result["exit_code"] = -3
            result["success"] = False
        else:
            result["error"] = ""
            result["exit_code"] = proc.returncode
            result["success"] = proc.returncode == 0

    except FileNotFoundError:
        result["error"] = f"Shell backend '{_shell_backend}' not found. Reinstall WSL or Git Bash."
        result["exit_code"] = -4
    except Exception as e:
        result["error"] = str(e)
        result["exit_code"] = -5

    result["duration_ms"] = round((time.time() - start_time) * 1000)

    # Log to Sera audit
    _log_command(result)

    return result

def _log_command(result: Dict[str, Any]):
    """Log command execution to Sera audit"""
    try:
        audit_file = LOG_DIR / f"shell_audit_{datetime.now().strftime('%Y%m%d')}.log"
        with open(audit_file, 'a') as f:
            f.write(json.dumps({
                "action": "shell_command",
                "user": result.get("user_id", "system"),
                "session": result.get("session_id", "default"),
                "command": result.get("command", "")[:200],
                "success": result.get("success", False),
                "exit_code": result.get("exit_code", -1),
                "duration_ms": result.get("duration_ms", 0),
                "timestamp": result.get("timestamp", datetime.utcnow().isoformat())
            }) + '\n')
        logger.info(f"Command executed: {result.get('command', '')[:100]}... by {result.get('user_id', 'system')}")
    except Exception as e:
        logger.error(f"Error logging command: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# SCRIPT EXECUTION (Added for terminal.py)
# ═══════════════════════════════════════════════════════════════════════════

def execute_script(script: str, session_id: str = "default",
                   timeout: int = 60, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Execute a multi-line bash script."""
    session = get_session(session_id, user_id)
    
    # Preprocess: strip sudo, auto-fix commands, and block interactive commands
    lines = script.strip().splitlines()
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            cleaned_lines.append(line)
            continue
        # Block interactive commands inside scripts
        if stripped.rstrip(";") in INTERACTIVE_COMMANDS:
            return {
                "command": script,
                "success": False,
                "output": "",
                "error": f"⚠️ '{stripped}' opens an interactive shell and cannot run in scripts.",
                "exit_code": -2,
                "backend": _shell_backend,
                "cwd": session.cwd,
                "duration_ms": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": session.user_id,
                "session_id": session_id
            }
        # Strip sudo prefix
        if _shell_backend == "wsl" and stripped.startswith("sudo "):
            line = line.replace("sudo ", "", 1)
        # Auto-fix interactive prompts
        line = _auto_fix_command(line)
        cleaned_lines.append(line)
    
    script = "\n".join(cleaned_lines)
    
    # For simple single-line commands, just use execute_linux
    if len(cleaned_lines) == 1 and safe_strip(cleaned_lines[0]):
        return execute_linux(safe_strip(cleaned_lines[0]), session_id, timeout, False, user_id)
    
    # Write to temp file and execute
    script_id = uuid.uuid4().hex[:8]
    temp_script = f"/tmp/sera_script_{script_id}.sh"
    
    # Write script to temp file
    write_cmd = f'cat > {temp_script} << \'SERA_EOF\'\n{script}\nSERA_EOF'
    execute_linux(write_cmd, session_id, 10, True, user_id)
    
    # Execute the script
    result = execute_linux(f"bash {temp_script}", session_id, timeout, True, user_id)
    
    # Clean up
    execute_linux(f"rm -f {temp_script}", session_id, 5, True, user_id)
    
    return result

# ═══════════════════════════════════════════════════════════════════════════
# High-Level Linux Operations (from Julius)
# ═══════════════════════════════════════════════════════════════════════════

def install_package(packages: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Install packages using the detected package manager (from Julius)"""
    pm_check = execute_linux("which apt-get yum dnf pacman 2>/dev/null | head -1", 
                            user_id=user_id)
    pm_path = safe_strip(pm_check.get("output", ""))

    if "apt-get" in pm_path or not pm_path:
        cmd = f"apt-get update -qq && apt-get install -y {packages}"
    elif "dnf" in pm_path:
        cmd = f"dnf install -y {packages}"
    elif "yum" in pm_path:
        cmd = f"yum install -y {packages}"
    elif "pacman" in pm_path:
        cmd = f"pacman -S --noconfirm {packages}"
    else:
        cmd = f"apt-get install -y {packages}"

    return execute_linux(cmd, timeout=120, session_id="system", user_id=user_id)

def get_system_info(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get comprehensive Linux system info (from Julius)"""
    commands = {
        "hostname": "hostname",
        "kernel": "uname -r",
        "distro": "cat /etc/os-release 2>/dev/null | head -5 || lsb_release -a 2>/dev/null",
        "uptime": "uptime",
        "cpu": "nproc",
        "memory": "free -h | head -2",
        "disk": "df -h / | tail -1",
        "ip": "hostname -I 2>/dev/null || ip addr show 2>/dev/null | grep 'inet ' | head -3",
        "user": "whoami",
        "shell": "echo $SHELL",
    }
    info = {}
    for key, cmd in commands.items():
        result = execute_linux(cmd, timeout=5, session_id="system", user_id=user_id)
        info[key] = result.get("output", "").strip() if result.get("success") else result.get("error", "N/A")
    return info

def get_shell_status(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get the status of the Linux shell subsystem (from Julius)"""
    status = {
        "available": _shell_backend is not None,
        "backend": _shell_backend,
        "host_os": _system,
        "sessions": get_all_sessions(),
    }

    if _shell_backend:
        test = execute_linux("echo 'SERA Linux Shell Active'", timeout=5, 
                           session_id="system", user_id=user_id)
        status["test_result"] = safe_strip(test.get("output", ""))
        status["operational"] = test.get("success", False)

        if test.get("success"):
            info = execute_linux("uname -a", timeout=5, session_id="system", user_id=user_id)
            status["kernel"] = safe_strip(info.get("output", ""))
    else:
        status["operational"] = False
        status["install_instructions"] = (
            "WSL not detected. Install it:\n"
            "1. Open PowerShell as Admin\n"
            "2. wsl --install\n"
            "3. Restart computer"
        )

    return status

def get_command_history(session_id: str = "default", limit: int = 20) -> List[Dict]:
    """Get recent command history (from Julius)"""
    session = get_session(session_id)
    return session.history[-limit:]

# ═══════════════════════════════════════════════════════════════════════════
# Main entry point
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Sera Linux Shell loaded")
