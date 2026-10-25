import json
from typing import List, Dict, Any, Optional
from app.llm.base import LLMProvider

class MockLLMProvider(LLMProvider):
    """
    Offline smart deterministic LLM provider for zero-overhead testing,
    rule-based reasoning, and offline autonomous simulation.
    Generates rich, fully functional Python programs for all major task categories.
    """

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        prompt_lower = prompt.lower()

        # Task breakdown / Manager role
        if "breakdown" in prompt_lower or "decompose" in prompt_lower or "subtasks" in prompt_lower:
            return json.dumps({
                "subtasks": [
                    {"role": "researcher", "goal": "Riset kebutuhan spesifikasi", "priority": 0.8},
                    {"role": "developer", "goal": "Implementasi kode awal", "priority": 0.7},
                    {"role": "reviewer", "goal": "QA & Review acceptance criteria", "priority": 0.9}
                ],
                "assumptions": ["Local sandbox execution", "Minimal memory footprint"],
                "risk_level": "low"
            })

        # Peer review role
        if "review" in prompt_lower or "evaluate" in prompt_lower or "critique" in prompt_lower:
            if "validation" not in prompt_lower and "error handling" not in prompt_lower:
                return json.dumps({
                    "status": "needs_revision",
                    "score": 0.65,
                    "findings": [
                        {
                            "severity": "medium",
                            "missing": "input validation",
                            "recommendation": "Tambahkan skema validasi tipe dan batas nilai"
                        }
                    ],
                    "evidence": "Artifact does not contain boundary check assertions"
                })
            else:
                return json.dumps({
                    "status": "approved",
                    "score": 0.98,
                    "findings": [],
                    "evidence": "Semua acceptance criteria, struktur data, dan penanganan error terpenuhi dengan sempurna"
                })

        # Code authoring / Developer role
        if "code" in prompt_lower or "implement" in prompt_lower or "python" in prompt_lower or "write" in prompt_lower or "buat" in prompt_lower:
            # 1. Web Application / Website / Dashboard / Portfolio / HTML
            if any(k in prompt_lower for k in ["web", "website", "html", "dashboard", "portofolio", "portfolio", "server", "api"]):
                return (
                    '"""\n'
                    '===========================================================\n'
                    'AI CITY WEB APP & DASHBOARD ENGINE\n'
                    'Dibuat oleh Ari (Developer Agent) | Direview oleh Bima (QA)\n'
                    'Menjalankan Web Server lokal interaktif dengan UI responsif modern.\n'
                    '===========================================================\n'
                    '"""\n'
                    'import http.server\n'
                    'import json\n'
                    'from datetime import datetime\n\n'
                    'PORT = 8085\n\n'
                    'HTML_PAGE = """<!DOCTYPE html>\n'
                    '<html lang="id">\n'
                    '<head>\n'
                    '    <meta charset="UTF-8">\n'
                    '    <title>AI City Citizen Dashboard</title>\n'
                    '    <style>\n'
                    '        * { box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }\n'
                    '        body { background: #0b0f19; color: #f8fafc; padding: 40px 20px; text-align: center; }\n'
                    '        .container { max-width: 800px; margin: 0 auto; background: #131b2e; border: 1px solid #1e293b; border-radius: 16px; padding: 32px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }\n'
                    '        h1 { color: #00f0ff; font-size: 28px; margin-bottom: 8px; }\n'
                    '        p { color: #94a3b8; font-size: 14px; margin-bottom: 24px; }\n'
                    '        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-top: 20px; }\n'
                    '        .card { background: #1e293b; border-radius: 12px; padding: 20px; text-align: left; border-left: 4px solid #00f0ff; }\n'
                    '        .card h3 { font-size: 13px; color: #94a3b8; text-transform: uppercase; }\n'
                    '        .card .val { font-size: 24px; font-weight: bold; color: #fff; margin-top: 8px; }\n'
                    '        .badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; background: #065f46; color: #34d399; margin-top: 16px; }\n'
                    '    </style>\n'
                    '</head>\n'
                    '<body>\n'
                    '    <div class="container">\n'
                    '        <h1>AI CITY PORTFOLIO & DASHBOARD</h1>\n'
                    '        <p>Aplikasi Web mandiri yang di-generate dan divalidasi oleh Agen AI City</p>\n'
                    '        <div class="badge">SISTEM ONLINE & RUNNING</div>\n'
                    '        <div class="grid">\n'
                    '            <div class="card"><h3>Total Populasi</h3><div class="val">8 Agents</div></div>\n'
                    '            <div class="card" style="border-left-color: #10b981;"><h3>Kondisi Kota</h3><div class="val">Optimal (98%)</div></div>\n'
                    '            <div class="card" style="border-left-color: #f59e0b;"><h3>Produktivitas</h3><div class="val">142 Tasks/day</div></div>\n'
                    '        </div>\n'
                    '    </div>\n'
                    '</body>\n'
                    '</html>"""\n\n'
                    'class AICityWebHandler(http.server.SimpleHTTPRequestHandler):\n'
                    '    def do_GET(self):\n'
                    '        if self.path in ("/", "/index.html"):\n'
                    '            self.send_response(200)\n'
                    '            self.send_header("Content-type", "text/html; charset=utf-8")\n'
                    '            self.end_headers()\n'
                    '            self.wfile.write(HTML_PAGE.encode("utf-8"))\n'
                    '        elif self.path == "/api/status":\n'
                    '            self.send_response(200)\n'
                    '            self.send_header("Content-type", "application/json")\n'
                    '            self.end_headers()\n'
                    '            payload = {"city": "AI City", "status": "active", "timestamp": datetime.now().isoformat()}\n'
                    '            self.wfile.write(json.dumps(payload).encode("utf-8"))\n'
                    '        else:\n'
                    '            self.send_error(404, "Page Not Found")\n\n'
                    '    def log_message(self, format, *args):\n'
                    '        pass\n\n'
                    'def test_server_readiness():\n'
                    '    print("==================================================")\n'
                    '    print("   AI CITY WEB SERVER & DASHBOARD INTI TERVERIFIKASI")\n'
                    '    print("==================================================")\n'
                    '    print(f"[*] Port target: {PORT}")\n'
                    '    print("[*] Handler: AICityWebHandler (REST API & HTML)")\n'
                    '    print(f"[*] Ukuran frontend: {len(HTML_PAGE)} bytes")\n'
                    '    print("[*] Endpoint terdaftar: GET / , GET /api/status")\n'
                    '    print("[+] Status Sandbox: Server web siap dijalankan dengan sukses!")\n'
                    '    print("==================================================")\n'
                    '    return True\n\n'
                    'if __name__ == "__main__":\n'
                    '    test_server_readiness()\n'
                )

            # 2. Game / Permainan (Snake, Tic-Tac-Toe, RPG, Console Game)
            elif any(k in prompt_lower for k in ["game", "permainan", "snake", "tictactoe", "rpg", "arcade"]):
                return (
                    '"""\n'
                    '===========================================================\n'
                    'AI CITY CONSOLE GAME ENGINE (TIC-TAC-TOE & AI OPPONENT)\n'
                    'Dibuat oleh Ari (Developer Agent) | Direview oleh Bima (QA)\n'
                    '===========================================================\n'
                    '"""\n'
                    'from typing import List, Optional\n\n'
                    'class TicTacToeEngine:\n'
                    '    def __init__(self):\n'
                    '        self.board: List[str] = [" " for _ in range(9)]\n'
                    '        self.current_winner: Optional[str] = None\n\n'
                    '    def render_board(self) -> str:\n'
                    '        b = self.board\n'
                    '        output = []\n'
                    '        output.append("   +---+---+---+")\n'
                    '        for i in range(3):\n'
                    '            row = f"   | {b[i*3]} | {b[i*3+1]} | {b[i*3+2]} |"\n'
                    '            output.append(row)\n'
                    '            output.append("   +---+---+---+")\n'
                    '        return "\\n".join(output)\n\n'
                    '    def make_move(self, square: int, letter: str) -> bool:\n'
                    '        if not (0 <= square <= 8):\n'
                    '            raise ValueError("Square index harus antara 0 dan 8.")\n'
                    '        if self.board[square] == " ":\n'
                    '            self.board[square] = letter\n'
                    '            if self._check_winner(square, letter):\n'
                    '                self.current_winner = letter\n'
                    '            return True\n'
                    '        return False\n\n'
                    '    def _check_winner(self, square: int, letter: str) -> bool:\n'
                    '        row_ind = square // 3\n'
                    '        row = self.board[row_ind*3 : (row_ind+1)*3]\n'
                    '        if all([s == letter for s in row]): return True\n'
                    '        col_ind = square % 3\n'
                    '        column = [self.board[col_ind+i*3] for i in range(3)]\n'
                    '        if all([s == letter for s in column]): return True\n'
                    '        if square % 2 == 0:\n'
                    '            d1 = [self.board[i] for i in [0, 4, 8]]\n'
                    '            if all([s == letter for s in d1]): return True\n'
                    '            d2 = [self.board[i] for i in [2, 4, 6]]\n'
                    '            if all([s == letter for s in d2]): return True\n'
                    '        return False\n\n'
                    '    def empty_squares(self) -> List[int]:\n'
                    '        return [i for i, x in enumerate(self.board) if x == " "]\n\n'
                    'if __name__ == "__main__":\n'
                    '    print("==================================================")\n'
                    '    print("        AI CITY GAME ENGINE: TIC-TAC-TOE AI       ")\n'
                    '    print("==================================================")\n'
                    '    game = TicTacToeEngine()\n'
                    '    game.make_move(4, "X") # Player center\n'
                    '    game.make_move(0, "O") # AI corner\n'
                    '    game.make_move(2, "X") # Player corner\n'
                    '    game.make_move(6, "O") # AI defense\n'
                    '    game.make_move(1, "X") # Player top\n'
                    '    print(game.render_board())\n'
                    '    print(f"[*] Kotak kosong tersisa: {game.empty_squares()}")\n'
                    '    print("[+] Engine Game berhasil dijalankan & lolos verifikasi!")\n'
                    '    print("==================================================")\n'
                )

            # 3. Calendar / Kalender / Penjadwalan
            elif any(k in prompt_lower for k in ["kalender", "calendar", "jadwal", "agenda"]):
                return (
                    '"""\n'
                    '===========================================================\n'
                    'APLIKASI KALENDER & JADWAL PRODUKTIVITAS AI CITY\n'
                    'Dibuat oleh Ari (Developer Agent) | Direview oleh Bima (QA)\n'
                    '===========================================================\n'
                    '"""\n'
                    'import calendar\n'
                    'from datetime import datetime\n'
                    'from typing import Dict, List\n\n'
                    'class CityCalendar:\n'
                    '    def __init__(self, year: int = None, month: int = None):\n'
                    '        now = datetime.now()\n'
                    '        self.year = year or now.year\n'
                    '        self.month = month or now.month\n'
                    '        self.events: Dict[str, List[str]] = {}\n\n'
                    '    def display_month(self) -> str:\n'
                    '        cal = calendar.TextCalendar(calendar.SUNDAY)\n'
                    '        return cal.formatmonth(self.year, self.month)\n\n'
                    '    def add_event(self, day: int, event_name: str):\n'
                    '        if not (1 <= day <= 31):\n'
                    '            raise ValueError("Tanggal harus berada dalam rentang 1 hingga 31.")\n'
                    '        key = f"{self.year}-{self.month:02d}-{day:02d}"\n'
                    '        if key not in self.events:\n'
                    '            self.events[key] = []\n'
                    '        self.events[key].append(event_name)\n'
                    '        return f"Event \'{event_name}\' berhasil dicatat untuk tanggal {key}."\n\n'
                    '    def list_events(self) -> Dict[str, List[str]]:\n'
                    '        return self.events\n\n'
                    'if __name__ == "__main__":\n'
                    '    app = CityCalendar()\n'
                    '    print("==================================================")\n'
                    '    print("              KALENDER KOTA AI CITY               ")\n'
                    '    print("==================================================")\n'
                    '    print(app.display_month())\n'
                    '    app.add_event(15, "Rapat Koordinasi Tata Kota")\n'
                    '    app.add_event(20, "Demo QA & Penerimaan Warga Baru")\n'
                    '    print("[*] Agenda Terjadwal:")\n'
                    '    for date, items in app.list_events().items():\n'
                    '        print(f"  * {date}: { \', \'.join(items) }")\n'
                    '    print("[+] Modul Kalender lolos acceptance criteria!")\n'
                    '    print("==================================================")\n'
                )

            # 4. Calculator / Kalkulator / Perhitungan
            elif any(k in prompt_lower for k in ["kalkulator", "calculator", "hitung", "math"]):
                return (
                    '"""\n'
                    '===========================================================\n'
                    'MODUL KALKULATOR CERDAS & ANALISIS MATEMATIKA AI CITY\n'
                    'Dibuat oleh Ari (Developer Agent) | Direview oleh Bima (QA)\n'
                    '===========================================================\n'
                    '"""\n'
                    'import math\n'
                    'from typing import List, Dict\n\n'
                    'class SmartCalculator:\n'
                    '    def __init__(self):\n'
                    '        self.history: List[Dict[str, str]] = []\n\n'
                    '    def calculate(self, expression: str) -> float:\n'
                    '        allowed = {\n'
                    '            "sin": math.sin, "cos": math.cos, "sqrt": math.sqrt,\n'
                    '            "pi": math.pi, "e": math.e, "pow": pow, "abs": abs\n'
                    '        }\n'
                    '        for char in expression:\n'
                    '            if char not in "0123456789+-*/(). sincospiepowab,":\n'
                    '                raise ValueError(f"Karakter berbahaya terdeteksi: {char}")\n'
                    '        res = eval(expression, {"__builtins__": {}}, allowed)\n'
                    '        self.history.append({"expr": expression, "result": str(res)})\n'
                    '        return float(res)\n\n'
                    '    def get_history(self) -> List[Dict[str, str]]:\n'
                    '        return self.history\n\n'
                    'if __name__ == "__main__":\n'
                    '    calc = SmartCalculator()\n'
                    '    print("==================================================")\n'
                    '    print("        KALKULATOR CERDAS AI CITY RUNTIME         ")\n'
                    '    print("==================================================")\n'
                    '    tests = ["125 * 8", "(450 + 50) / 2", "sqrt(144) + 18", "sin(pi / 2)"]\n'
                    '    for t in tests:\n'
                    '        val = calc.calculate(t)\n'
                    '        print(f"  * {t:20s} = {val}")\n'
                    '    print(f"[*] Total riwayat operasi: {len(calc.get_history())} transaksi")\n'
                    '    print("[+] Kalkulator tervalidasi 100% aman dan akurat!")\n'
                    '    print("==================================================")\n'
                )

            # 5. Pembangunan / Konstruksi / Ekspansi Kota / Arsitektur
            elif any(k in prompt_lower for k in ["bangun", "rumah", "kantor", "gedung", "ekspansi", "arsitek", "rekrut", "penduduk", "warga", "ruko"]):
                return (
                    '"""\n'
                    '===========================================================\n'
                    'BLUEPRINT ARSITEKTUR & EKSPANSI FISIK AI CITY\n'
                    'Dibuat oleh Ari (Developer Agent) | Direview oleh Bima (QA)\n'
                    'Mengatur zoning lahan, kalkulasi struktural, dan integrasi warga baru.\n'
                    '===========================================================\n'
                    '"""\n'
                    'from typing import Dict, Any, List\n'
                    'import json\n\n'
                    'class CityExpansionBlueprint:\n'
                    '    def __init__(self, zone_name: str = "Distrik Baru"):\n'
                    '        self.zone_name = zone_name\n'
                    '        self.structures: List[Dict[str, Any]] = []\n\n'
                    '    def plan_structure(self, b_type: str, floors: int, capacity: int) -> Dict[str, Any]:\n'
                    '        if floors < 1:\n'
                    '            raise ValueError("Lantai gedung minimal 1 lantai.")\n'
                    '        structure = {\n'
                    '            "type": b_type,\n'
                    '            "floors": floors,\n'
                    '            "capacity": capacity,\n'
                    '            "power_kw": floors * 12.5,\n'
                    '            "water_liters_day": capacity * 150,\n'
                    '            "safety_status": "APPROVED_SNI"\n'
                    '        }\n'
                    '        self.structures.append(structure)\n'
                    '        return structure\n\n'
                    '    def generate_report(self) -> Dict[str, Any]:\n'
                    '        total_cap = sum(s["capacity"] for s in self.structures)\n'
                    '        total_pwr = sum(s["power_kw"] for s in self.structures)\n'
                    '        return {\n'
                    '            "zone": self.zone_name,\n'
                    '            "total_buildings": len(self.structures),\n'
                    '            "total_capacity_citizens": total_cap,\n'
                    '            "total_power_load_kw": total_pwr,\n'
                    '            "expansion_readiness": "100% READY"\n'
                    '        }\n\n'
                    'if __name__ == "__main__":\n'
                    '    planner = CityExpansionBlueprint("Distrik Hunian & Kantor Baru")\n'
                    '    print("==================================================")\n'
                    '    print("    CETAK BIRU EKSPANSI FISIK BANGUNAN KOTA       ")\n'
                    '    print("==================================================")\n'
                    '    planner.plan_structure("Residential Cottage", floors=2, capacity=4)\n'
                    '    planner.plan_structure("Cyber Tech Office", floors=5, capacity=20)\n'
                    '    report = planner.generate_report()\n'
                    '    print(json.dumps(report, indent=4))\n'
                    '    print("[+] Konstruksi disetujui: Gedung & Penduduk siap bergabung!")\n'
                    '    print("==================================================")\n'
                )

            # 6. Default Smart Clean Program (General Tasks)
            else:
                return (
                    '"""\n'
                    '===========================================================\n'
                    'MODUL SISTEM OPERASIONAL MANDIRI AI CITY\n'
                    'Dibuat oleh Ari (Developer Agent) | Direview oleh Bima (QA)\n'
                    '===========================================================\n'
                    '"""\n'
                    'from typing import Any, Dict, List\n'
                    'import time\n\n'
                    'class CityWorkforceEngine:\n'
                    '    def __init__(self, task_name: str = "Tugas Kota"):\n'
                    '        self.task_name = task_name\n'
                    '        self.logs: List[str] = []\n\n'
                    '    def process_work(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:\n'
                    '        if payload is not None and not isinstance(payload, dict):\n'
                    '            raise ValueError("Payload masukan harus bertipe dictionary.")\n'
                    '        self.logs.append(f"Inisiasi pemrosesan tugas: {self.task_name}")\n'
                    '        self.logs.append("Validasi tipe data & kriteria acceptance: Lolos")\n'
                    '        self.logs.append("Eksekusi logika solusi otonom selesai")\n'
                    '        return {\n'
                    '            "status": "success",\n'
                    '            "task": self.task_name,\n'
                    '            "completion_time": time.strftime("%Y-%m-%d %H:%M:%S"),\n'
                    '            "execution_logs": self.logs,\n'
                    '            "output_data": payload or {"metrics": "optimal"}\n'
                    '        }\n\n'
                    'if __name__ == "__main__":\n'
                    '    engine = CityWorkforceEngine("Pekerjaan Otonom AI City")\n'
                    '    print("==================================================")\n'
                    '    print("       EKSEKUSI TUGAS NYATA SANDBOX AI CITY       ")\n'
                    '    print("==================================================")\n'
                    '    res = engine.process_work({"priority": "high", "agent": "Ari"})\n'
                    '    for l in res["execution_logs"]:\n'
                    '        print(f"  [*] {l}")\n'
                    '    print(f"[+] Status Akhir: {res[\'status\'].upper()} (Waktu: {res[\'completion_time\']})")\n'
                    '    print("==================================================")\n'
                )

        # Skill learning / Mentor role
        if "skill" in prompt_lower or "learn" in prompt_lower or "curriculum" in prompt_lower:
            return json.dumps({
                "procedures": [
                    "Baca dokumentasi dasar",
                    "Buat script contoh sederhana",
                    "Jalankan test validasi fungsi"
                ],
                "tests": [
                    "Uji input valid",
                    "Uji input invalid / edge case"
                ]
            })

        return f"Processed prompt successfully: {prompt[:100]}..."

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        last_message = messages[-1]["content"] if messages else ""
        return await self.generate(last_message, temperature=temperature, max_tokens=max_tokens)
