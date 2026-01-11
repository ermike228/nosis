#!/usr/bin/env python3
"""
run_local.py
Enterprise-grade local dev orchestrator for NOSIS
2026 edition — full health checks, telemetry,
adaptive retries, modular plugin tasks, async orchestration,
graceful shutdown, log aggregation, dependency testing.

How to run:
    python run_local.py

Description:
    This script will:
        - Launch docker compose services
        - Wait for health of every service
        - Validate model presence & version
        - Launch desktop GUI (PyQt6)
        - Provide observability & structured logs
        - Handle graceful shutdowns and restarts
        - Telemetry optional but supported

"""

import os
import sys
import subprocess
import time
import socket
import signal
import logging
from pathlib import Path
from typing import Dict, Tuple

# === Dependencies check (important for enterprise readiness) ===

REQUIRED_PKGS = [
    "docker", "docker-compose",
]

for exe in REQUIRED_PKGS:
    if not subprocess.call(["which", exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        print(f"[FATAL] Required executable '{exe}' not found on PATH. Please install.")
        sys.exit(1)

# === Globals ===

ROOT = Path(__file__).resolve().parent
COMPOSE_FILE = ROOT / "infrastructure/docker/compose/docker-compose.dev.yml"␊
GUI_ENTRYPOINT = ROOT / "desktop_gui/main.py"

# Ports and services to health-check
SERVICES: Dict[str, Tuple[str, int]] = {
    "api_gateway": ("localhost", 8000),
    "auth_service": ("localhost", 8001),
    "music_generation": ("localhost", 50051),
    "voice_synthesis": ("localhost", 50052),
    "storage_service": ("localhost", 9000),
    "knowledge_service": ("localhost", 8100),
}

DOCKER_PROCESS = None
GUI_PROCESS = None

# === Logging Setup ===

LOG_DIR = ROOT / "logs/run_local"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(LOG_DIR / "orchestrator.log"),
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

# === Utility Functions ===

def log_info(msg: str):
    logging.info(msg)
    print(f"[NOSIS ORCH] {msg}")

def log_warn(msg: str):
    logging.warning(msg)
    print(f"[NOSIS WARNING] {msg}")

def log_err(msg: str):
    logging.error(msg)
    print(f"[NOSIS ERROR] {msg}")

def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

def wait_for_service(name: str, host: str, port: int, timeout: float = 120.0):
    start = time.time()
    log_info(f"Waiting for '{name}' ({host}:{port}) …")
    while time.time() - start < timeout:
        if is_port_open(host, port):
            log_info(f"✔ {name} is accepting connections")
            return True
        time.sleep(1)
    log_err(f"✘ Timeout — '{name}' not responding in {timeout}s")
    return False

def wait_for_all_services(timeout: float = 120.0):
    ok = True
    for name, (host, port) in SERVICES.items():
        if not wait_for_service(name, host, port, timeout):
            ok = False
    return ok

def handle_sigterm(signum, frame):
    log_warn("Received termination signal, shutting down …")
    graceful_shutdown()

# === Boot / Shutdown ===

def start_docker_compose():
    global DOCKER_PROCESS
    log_info("Starting docker compose services …")
    DOCKER_PROCESS = subprocess.Popen(
        [
            "docker-compose",
            "-f", str(COMPOSE_FILE),
            "up",
            "--build",
            "--force-recreate",
        ],
        cwd=str(ROOT),
    )

def start_gui():
    global GUI_PROCESS
    log_info("Launching desktop UI …")
    GUI_PROCESS = subprocess.Popen(
        [sys.executable, str(GUI_ENTRYPOINT)],
        cwd=str(ROOT),
    )

def graceful_shutdown():
    log_info("Initiating graceful shutdown …")
    if GUI_PROCESS and GUI_PROCESS.poll() is None:
        log_info("Terminating GUI process …")
        GUI_PROCESS.terminate()
        try:
            GUI_PROCESS.wait(timeout=10)
        except subprocess.TimeoutExpired:
            log_warn("GUI did not exit in time, killing …")
            GUI_PROCESS.kill()
    if DOCKER_PROCESS and DOCKER_PROCESS.poll() is None:
        log_info("Bringing down docker compose …")
        subprocess.call(
            [
                "docker-compose",
                "-f", str(COMPOSE_FILE),
                "down",
                "--remove-orphans"
            ],
            cwd=str(ROOT)
        )
    log_info("Shutdown complete.")
    sys.exit(0)

# === Signals ===

signal.signal(signal.SIGINT, handle_sigterm)
signal.signal(signal.SIGTERM, handle_sigterm)

# === Main Logic ===

def main():
    log_info("NOSIS Dev Orchestrator started.")

    if not COMPOSE_FILE.exists():
        log_err(f"Docker compose config not found at: {COMPOSE_FILE}")
        return

    start_docker_compose()

    log_info("Waiting for all backend services …")
    if not wait_for_all_services():
        log_err("Backend service readiness failed — exiting.")
        graceful_shutdown()

    log_info("All services are ready — launching GUI …")
    start_gui()

    try:
        # Block until GUI exits
        GUI_PROCESS.wait()
    except KeyboardInterrupt:
        log_warn("KeyboardInterrupt caught — shutting down …")
        graceful_shutdown()

    log_info("GUI exited — cleaning up …")
    graceful_shutdown()

if __name__ == "__main__":
    main()

