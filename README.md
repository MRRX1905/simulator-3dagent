# AI CITY — Autonomous Artificial Society & Digital Workforce

> Virtual artificial society inhabited by autonomous AI agents that live, work, learn, collaborate, peer-review one another, acquire certified skills, use sandboxed computer tools, and evolve their city.

---

## 🏛️ Arsitektur Sistem

AI City memisahkan visual kota (*visualization layer*) dari otak AI (*backend AI layer*):

- **Backend Core**: FastAPI (Python 3.14) asynchronous runtime dengan SQLite (WAL mode).
- **LLM Gateway**: Provider-agnostic abstraction (`MockProvider`, `OllamaProvider`, `LMStudioProvider`, OpenAI-compatible).
- **Agent Mental Model**: State Machine (`IDLE`, `PLANNING`, `EXECUTING`, `WAITING_TOOL`, `REVIEWING`, `LEARNING`, `DONE`), Big Five Personality, Dynamic Needs (`food`, `energy`, `social`, `money`).
- **Autonomous Life Loop**: World Tick Scheduler yang menghidupkan kota bahkan ketika user sedang offline.
- **Peer-to-Peer Review Engine**: Protokol review ketat berbasis bukti (*evidence-based*), temuan terstruktur (*severity*, *missing*, *recommendation*), serta siklus auto-revisi.
- **Skill Registry & Capability Gap Detector**: Marketplace skill internal (Level 0 - 5), pencocokan mentor-learner, pengujian di sandbox sebelum sertifikasi.
- **Tool Gateway & Sandbox**: Pembagian Zona Keamanan A (Safe), B (Moderate), C (High Risk / Approval), D (Critical), serta perlindungan anti-jailbreak direktori workspace.
- **Real-Time Streaming Bridge**: REST API dan WebSocket stream (`/ws/world`, `/ws/agents`) untuk Unity 6 atau Web Dashboard.

---

## 👥 5 Agent Utama (MVP)

1. **Citra (Manager)**: Memecah tugas pengguna menjadi *task graph*, delegasi peran, dan agregasi hasil.
2. **Ari (Developer)**: Mengimplementasikan solusi kode, mengeksekusi script di workspace sandbox, dan merevisi kode berdasarkan temuan QA.
3. **Bima (QA / Reviewer)**: Menjalankan acceptance criteria testing dan menghasilkan peer review objektif.
4. **Deni (Researcher)**: Menggali dokumentasi teknis, pola repositori, dan menyimpan pengetahuan ke memori semantik.
5. **Eka (Skill Mentor)**: Mendeteksi capability gap, membimbing agen lain melalui kurikulum latihan, dan memvalidasi sertifikasi skill.

---

## 🎮 Cara Menjalankan

### 1. 3D Game World Simulator (Rekomendasi Utama — Tampilan Dunia Game 3D)
Jalankan file game native desktop (tanpa membuka web browser):
```cmd
C:\AI_CITY\play_city.bat
```
*(Atau via PowerShell: `powershell -ExecutionPolicy Bypass -File "C:\AI_CITY\play_city.ps1"`)*

**Fitur Visual 3D Game World:**
- **Lingkungan 3D**: Lanskap kota lengkap dengan jalan aspal, zebra cross, trotoar, pepohonan, lampu jalan, dan air mancur plaza.
- **Bangunan Berkarakter**:
  - *City Hall* (Pemerintahan / Kantor Citra) dengan pilar dan menara jam.
  - *Tech Hub Tower* (Gedung kaca software tempat Ari bekerja) dengan antena pemancar neon.
  - *QA & Testing Lab* (Fasilitas uji coba tempat Bima bekerja) dengan radar dish.
  - *Research Academy & Library* (Gedung rotunda kubah tempat Deni & Eka).
  - *Residential Houses* & *Construction Site* (Area pembangunan kota).
- **Karakter 3D Beranimasi (NPCs)**: Ari, Bima, Citra, Deni, dan Eka berjalan secara otonom antara rumah dan tempat kerja mereka.
- **Thought Bubbles**: Balon pikiran terapung di atas kepala karakter menunjukkan apa yang sedang mereka kerjakan secara live.
- **Siklus Siang & Malam (Day/Night)**: Pencahayaan matahari bergerak dinamis, lampu jalan menyala di malam hari.
- **RPG HUD & Kontrol Interaktif**:
  - Panel inspeksi agent dengan avatar, bar energi, bar makanan, dan skill.
  - Tombol **"🎯 Berikan Goal / Tugas"** untuk menugaskan pekerjaan langsung dari dalam game 3D.
  - Kontrol kamera 3D bebas (Orbit 360°, Pan, Zoom).

---

### 2. Konsol Terminal Interaktif (CLI Simulator)
Jika ingin kontrol teks murni di Command Prompt / PowerShell:
```cmd
C:\AI_CITY\city.bat
```

---

### 3. Backend Service (Daemon untuk Unity 6 / External Consumer)
```powershell
powershell -ExecutionPolicy Bypass -File "C:\AI_CITY\scripts\start_city.ps1"
```

---

## 🛡️ Zona Keamanan (Safety Zones)

| Zona | Tingkat Risiko | Tindakan | Kebijakan |
|---|---|---|---|
| **Zone A** | Safe | Baca/tulis file workspace, eksekusi test lokal | Eksekusi Otomatis |
| **Zone B** | Moderate | Network request domain allowlist | Otomatis dengan Audit |
| **Zone C** | High Risk | Git push, cloud upload | **Wajib Approval Manusia** |
| **Zone D** | Critical | Penghapusan file, command berbahaya | **Ditolak / Verifikasi 2 Tahap** |

---

## 📁 Struktur Direktori

```text
C:\AI_CITY\
├── backend\
│   ├── app\
│   │   ├── api\               # REST endpoints & WebSocket bridge
│   │   ├── agents\            # Agent classes, roles, & registry
│   │   ├── core\              # Scheduler & state machine
│   │   ├── llm\               # Provider-agnostic LLM Gateway
│   │   ├── memory\            # Episodic, semantic, & procedural memory
│   │   ├── peer_review\       # P-to-P advice & review engine
│   │   ├── safety\            # Approval queue
│   │   ├── skills\            # Skill registry & gap detector
│   │   ├── tools\             # Sandboxed filesystem & command runner
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── main.py
│   ├── data\                  # ai_city.db (SQLite WAL)
│   ├── workspace\             # Isolated sandbox directory
│   └── tests\                 # Comprehensive pytest suite
├── skills\                    # JSON skill catalog
├── scripts\                   # PowerShell utility scripts
└── README.md
```
