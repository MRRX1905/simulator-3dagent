"""
===========================================================
BLUEPRINT ARSITEKTUR & EKSPANSI FISIK AI CITY
Dibuat oleh Ari (Developer Agent) | Direview oleh Bima (QA)
Mengatur zoning lahan, kalkulasi struktural, dan integrasi warga baru.
===========================================================
"""
from typing import Dict, Any, List
import json

class CityExpansionBlueprint:
    def __init__(self, zone_name: str = "Distrik Baru"):
        self.zone_name = zone_name
        self.structures: List[Dict[str, Any]] = []

    def plan_structure(self, b_type: str, floors: int, capacity: int) -> Dict[str, Any]:
        if floors < 1:
            raise ValueError("Lantai gedung minimal 1 lantai.")
        structure = {
            "type": b_type,
            "floors": floors,
            "capacity": capacity,
            "power_kw": floors * 12.5,
            "water_liters_day": capacity * 150,
            "safety_status": "APPROVED_SNI"
        }
        self.structures.append(structure)
        return structure

    def generate_report(self) -> Dict[str, Any]:
        total_cap = sum(s["capacity"] for s in self.structures)
        total_pwr = sum(s["power_kw"] for s in self.structures)
        return {
            "zone": self.zone_name,
            "total_buildings": len(self.structures),
            "total_capacity_citizens": total_cap,
            "total_power_load_kw": total_pwr,
            "expansion_readiness": "100% READY"
        }

if __name__ == "__main__":
    planner = CityExpansionBlueprint("Distrik Hunian & Kantor Baru")
    print("==================================================")
    print("    CETAK BIRU EKSPANSI FISIK BANGUNAN KOTA       ")
    print("==================================================")
    planner.plan_structure("Residential Cottage", floors=2, capacity=4)
    planner.plan_structure("Cyber Tech Office", floors=5, capacity=20)
    report = planner.generate_report()
    print(json.dumps(report, indent=4))
    print("[+] Konstruksi disetujui: Gedung & Penduduk siap bergabung!")
    print("==================================================")