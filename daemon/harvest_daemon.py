#!/usr/bin/env python3
"""
harvest_daemon.py - The active cycle-harvesting controller.
Monitors node idle time, resumes node in Slurm when idle,
and force-evicts cluster jobs when a human returns.
"""
import subprocess
import time
import socket
import os

NODE = socket.gethostname().split(".")[0]
IDLE_THRESHOLD = int(os.environ.get("IDLE_THRESHOLD", "900")) # 15 minutes (900 seconds)

def run_cmd(cmd):
    """Utility to run system commands safely."""
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return res.stdout.strip()
    except Exception as e:
        return str(e)

def resume_node_in_slurm():
    """Tells Slurm Master that this machine is free to take HPC jobs."""
    print(f"[{time.ctime()}] Node {NODE} is IDLE. Enlisting in Slurm cluster...")
    run_cmd(f"scontrol update NodeName={NODE} State=RESUME")

def evict_node_immediately():
    """Frees the PC immediately for a human student."""
    print(f"[{time.ctime()}] HUMAN INTERRUPT! Evicting cluster workloads...")
    
    # 1. Immediately kill running compute containers (0 lag for student)
    run_cmd("docker kill $(docker ps -q --filter ancestor=desktop-grid-mpi:v1)")
    
    # 2. Tell Slurm to drain this node so no new jobs are sent
    run_cmd(f"scontrol update NodeName={NODE} State=DRAIN Reason='Student returned'")
    
    # 3. Tell Slurm to requeue whatever job was running so it restarts on another PC
    run_cmd(f"scontrol requeue nodename={NODE}")

def get_simulated_idle_seconds():
    # In production, this reads evdev timestamp. 
    # For testing, we read from an environment variable or dummy file
    return int(os.environ.get("MOCK_IDLE", "0"))

def main():
    state = "DRAINED"
    print(f"Starting Harvest Daemon on {NODE}. Initial state: {state}")
    
    while True:
        idle_seconds = get_simulated_idle_seconds()
        
        # Condition A: Machine has been idle for > 15 mins and is not yet in the cluster
        if idle_seconds >= IDLE_THRESHOLD and state == "DRAINED":
            resume_node_in_slurm()
            state = "ENLISTED"
            
        # Condition B: Machine was in the cluster, but someone just touched it!
        elif idle_seconds < IDLE_THRESHOLD and state == "ENLISTED":
            evict_node_immediately()
            state = "DRAINED"
            
        time.sleep(2)

if __name__ == "__main__":
    main()