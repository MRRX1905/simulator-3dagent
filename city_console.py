#!/usr/bin/env python
"""
AI CITY — Interactive Terminal Console & Launcher
Pengendali kota AI otonom langsung dari Terminal Windows (tanpa web browser).
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure backend is in Python path
BACKEND_DIR = Path("C:/AI_CITY/backend").resolve()
sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings
from app.database import init_db
from app.agents.registry import agent_registry
from app.core.scheduler import world_scheduler
from app.skills.registry import skill_registry
from app.tools.gateway import tool_gateway
from app.safety.approval_manager import approval_manager
from app.models import TaskModel

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    print(f"{CYAN}{BOLD}")
    print("  ================================================================")
    print("    [AI CITY] - AUTONOMOUS ARTIFICIAL SOCIETY & WORKFORCE         ")
    print("       (Terminal Console / Local Windows Simulator)              ")
    print("  ================================================================")
    print(f"{RESET}")

def print_status():
    world_time = world_scheduler.get_world_time()
    agents = agent_registry.get_all_agents()
    
    print(f"\n{BOLD}[WAKTU KOTA]:{RESET} {YELLOW}{world_time}{RESET} | {BOLD}[TOTAL AGENT]:{RESET} {GREEN}{len(agents)}{RESET} | {BOLD}[LLM]:{RESET} {MAGENTA}{settings.LLM_PROVIDER}{RESET}")
    print(f"{BOLD}[WORKSPACE]:{RESET} {CYAN}{settings.WORKSPACE_PATH}{RESET}\n")

    print(f"{BOLD}{'ID':<18} {'NAMA':<10} {'ROLE':<14} {'STATUS':<12} {'LOKASI':<12} {'ENERGI':<8} {'MAKAN':<8} {'REPUTASI'}{RESET}")
    print("-" * 92)

    for a in agents:
        status_color = GREEN if a.status == "IDLE" else YELLOW if a.status in ("PLANNING", "EXECUTING") else MAGENTA
        print(f"{a.id:<18} {a.name:<10} {a.role:<14} {status_color}{a.status:<12}{RESET} {a.location:<12} {a.needs.energy:<8.2f} {a.needs.food:<8.2f} {a.reputation}")
    print()

def safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print()
        return "q"

async def submit_goal():
    print(f"\n{CYAN}{BOLD}--- BERIKAN TUJUAN / GOAL KE KOTA ---{RESET}")
    goal = safe_input(f"{YELLOW}Masukkan tujuan/pekerjaan untuk agent: {RESET}").strip()
    if not goal or goal == "q":
        print(f"{RED}Tujuan dibatalkan.{RESET}")
        return

    print(f"\n{GREEN}[*] Mengirim tujuan ke Citra (Manager Agent)...{RESET}")
    manager = agent_registry.get_agent_instance("agent_manager_01")
    task_id = f"task_{int(time.time())}"
    
    task = TaskModel(
        id=task_id,
        title=f"Goal: {goal[:40]}",
        goal=goal,
        created_by="user_console",
        assigned_to="agent_manager_01",
        status="RUNNING"
    )

    plan_result = await manager.execute_task(task)
    print(f"{GREEN}[OK] Citra telah memecah tugas menjadi subtasks:{RESET}")
    for st in plan_result.get("plan", []):
        print(f"   * Role: {BOLD}{st.get('role')}{RESET} -> Goal: {st.get('goal')}")

    # Now let Ari execute the dev subtask
    print(f"\n{CYAN}[DEV] Ari (Developer Agent) mulai mengimplementasikan solusi di workspace...{RESET}")
    dev = agent_registry.get_agent_instance("agent_dev_01")
    dev_task = TaskModel(
        id=f"dev_{task_id}",
        title=f"Dev: {goal[:30]}",
        goal=goal,
        created_by="agent_manager_01",
        assigned_to="agent_dev_01"
    )
    
    dev_result = await dev.execute_task(dev_task)
    print(f"{GREEN}[OK] Ari selesai bekerja!{RESET}")
    print(f"   * Artefak dihasilkan: {BOLD}{dev_result.get('artifact_path')}{RESET}")
    print(f"   * Hasil Peer Review Bima (QA): {BOLD}{dev_result.get('review_status')}{RESET} (Skor: {dev_result.get('review_score')})")
    print(f"   * Total iterasi revisi: {dev_result.get('iterations')}")

    # Display snippet of created file
    try:
        content = tool_gateway.fs.read_file(dev_result.get('artifact_path'))
        print(f"\n{YELLOW}--- Isi Kode Hasil Kerja di Sandbox ---{RESET}")
        print(content)
        print(f"{YELLOW}---------------------------------------{RESET}")
    except Exception as e:
        print(f"Tidak dapat membaca file: {e}")

async def advance_tick():
    print(f"\n{CYAN}[*] Menjalankan 1 Tick Simulasi Kota...{RESET}")
    res = await world_scheduler.tick()
    print(f"{GREEN}[OK] Tick berhasil! Waktu sekarang: {YELLOW}{res['world_time']}{RESET} (Tick #{res['tick']})")
    if res['dispatched_tasks']:
        print(f"   Tugas didispatch ke agent: {res['dispatched_tasks']}")
    else:
        print("   Tidak ada tugas tertunda yang perlu didispatch.")

def view_skills():
    print(f"\n{CYAN}{BOLD}--- KATALOG SKILL & MENTOR AI CITY ---{RESET}")
    skills = skill_registry.list_skills()
    for s in skills:
        val_str = f"{GREEN}[Tervalidasi]{RESET}" if s.validated else f"{YELLOW}[Kandidat]{RESET}"
        print(f"* {BOLD}{s.name}{RESET} (Level {s.level}) {val_str}")
        print(f"  Deskripsi : {s.description}")
        print(f"  Kategori  : {s.category}")
    print()

def view_workspace():
    print(f"\n{CYAN}{BOLD}--- ISI WORKSPACE SANDBOX ({settings.WORKSPACE_PATH}) ---{RESET}")
    files = tool_gateway.fs.list_files(".")
    if not files:
        print("Workspace masih kosong.")
    else:
        for f in files:
            t = "DIR " if f["is_dir"] else f"{f['size']} B"
            print(f"  [{t}] {f['relative_path']}")
    print()

def view_approvals():
    print(f"\n{CYAN}{BOLD}--- ANTREAN PERSETUJUAN (ZONA C & D) ---{RESET}")
    apps = approval_manager.list_pending_approvals()
    if not apps:
        print(f"{GREEN}Tidak ada aksi berisiko tinggi yang menunggu persetujuan.{RESET}")
        return

    for a in apps:
        print(f"ID: {a.id} | Agent: {a.agent_id} | Zona: {RED}Zone {a.zone}{RESET} | Aksi: {a.action}")
        print(f"Detail: {a.details}")
        ans = safe_input("Setujui aksi ini? (y/n/skip): ").strip().lower()
        if ans == "y":
            approval_manager.resolve_approval(a.id, approved=True)
            print(f"{GREEN}Disetujui.{RESET}")
        elif ans == "n":
            approval_manager.resolve_approval(a.id, approved=False)
            print(f"{RED}Ditolak.{RESET}")

async def live_mode():
    print(f"\n{YELLOW}{BOLD}Memulai Mode Simulasi Live Otonom (Tekan Ctrl+C untuk kembali ke menu)...{RESET}")
    try:
        while True:
            res = await world_scheduler.tick()
            print(f"[{YELLOW}{res['world_time']}{RESET}] Tick #{res['tick']} | Kota aktif...")
            await asyncio.sleep(2.5)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    print(f"\n{GREEN}[Mode live selesai. Kembali ke menu utama.]{RESET}")

async def main_menu():
    init_db()
    agent_registry.seed_default_agents()

    try:
        while True:
            print_banner()
            print("  PILIHAN MENU:")
            print("  [1] Status Kota & Penduduk (Agents)")
            print("  [2] Berikan Tugas / Goal ke Kota")
            print("  [3] Majukan Waktu Simulasi (1 Tick)")
            print("  [4] Katalog Skill & Mentor")
            print("  [5] Buka / Lihat File Workspace Sandbox")
            print("  [6] Antrean Persetujuan Keamanan (Zone C/D)")
            print("  [7] Mode Simulasi Live Otonom")
            print("  [q] Keluar")
            print("-" * 64)

            pilihan = safe_input(f"{BOLD}Pilih opsi [1-7 / q]: {RESET}").strip()

            if pilihan == "1":
                print_status()
                safe_input(f"\n{CYAN}Tekan Enter untuk kembali...{RESET}")
            elif pilihan == "2":
                await submit_goal()
                safe_input(f"\n{CYAN}Tekan Enter untuk kembali...{RESET}")
            elif pilihan == "3":
                await advance_tick()
                safe_input(f"\n{CYAN}Tekan Enter untuk kembali...{RESET}")
            elif pilihan == "4":
                view_skills()
                safe_input(f"\n{CYAN}Tekan Enter untuk kembali...{RESET}")
            elif pilihan == "5":
                view_workspace()
                safe_input(f"\n{CYAN}Tekan Enter untuk kembali...{RESET}")
            elif pilihan == "6":
                view_approvals()
                safe_input(f"\n{CYAN}Tekan Enter untuk kembali...{RESET}")
            elif pilihan == "7":
                await live_mode()
                safe_input(f"\n{CYAN}Tekan Enter untuk kembali...{RESET}")
            elif pilihan.lower() in ("q", "exit", "quit"):
                print(f"\n{GREEN}Sampai jumpa di AI City!{RESET}")
                break
            else:
                print(f"{RED}Pilihan tidak valid.{RESET}")
                await asyncio.sleep(1)
    except (KeyboardInterrupt, EOFError):
        print(f"\n{GREEN}AI City ditutup. Sampai jumpa!{RESET}")

if __name__ == "__main__":
    try:
        asyncio.run(main_menu())
    except (KeyboardInterrupt, SystemExit):
        print(f"\n{GREEN}AI City ditutup dengan aman.{RESET}")
        try:
            sys.exit(0)
        except SystemExit:
            pass
