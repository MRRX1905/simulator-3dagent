"""
Aplikasi Kalender Interaktif AI City
Dibuat oleh Ari (Developer Agent) | Direview oleh Bima (QA)
"""
import calendar
from datetime import datetime

class CityCalendar:
    def __init__(self, year: int = None, month: int = None):
        now = datetime.now()
        self.year = year or now.year
        self.month = month or now.month
        self.events = {}

    def display_month(self) -> str:
        """Menampilkan kalender bulanan dalam format visual teks."""
        cal = calendar.TextCalendar(calendar.SUNDAY)
        return cal.formatmonth(self.year, self.month)

    def add_event(self, day: int, event_name: str):
        """Menambahkan jadwal/kegiatan pada tanggal tertentu."""
        if not (1 <= day <= 31):
            raise ValueError("Tanggal harus antara 1 dan 31.")
        key = f"{self.year}-{self.month:02d}-{day:02d}"
        if key not in self.events:
            self.events[key] = []
        self.events[key].append(event_name)
        return f"Event '{event_name}' berhasil dicatat untuk {key}."

    def list_events(self) -> dict:
        return self.events

if __name__ == "__main__":
    app = CityCalendar()
    print("===============================")
    print("     KALENDER KOTA AI CITY     ")
    print("===============================")
    print(app.display_month())
    app.add_event(15, "Rapat Koordinasi AI City")
    app.add_event(20, "Demo Review QA")
    print("Jadwal Acara:", app.list_events())
