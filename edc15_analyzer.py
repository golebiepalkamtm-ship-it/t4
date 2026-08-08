"""
================================================================================
  EDC15VM+ VCDS Master Log Analyzer & Map Correlator (Full Diagnostics)
  Sterownik: Bosch EDC15VM+25 (VP37) — VW T4 2.5 TDI AXG (151 KM)
  Software:  1037362445 (SG 3908 28SA5172)
  Hardware:  0281010461 / 074906018AJ
  
  Autor narzędzia: Antigravity AI Engine
  Data:      2026-07-28
================================================================================
"""

import struct
import csv
import os
import sys
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("EDC15Analyzer")

# ─────────────────────────────────────────────────────────────────────────────
# STAŁE KONFIGURACYJNE DLA SOFTWARE 1037362445 (074906018AJ)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class MapDefinition:
    """Definicja pojedynczej mapy w pamięci ECU."""
    name: str
    dimsport_code: str
    addr_cb5: int
    addr_cb2: int
    rows: int
    cols: int
    factor: float = 0.01
    unit: str = "mg/hub"
    x_label: str = "RPM"
    y_label: str = "Load"

# Mapa adresów dla software 1037362445
MAP_DEFINITIONS = {
    "driver_wish": MapDefinition(name="Driver Wish (Życzenie kierowcy)", dimsport_code="B1", addr_cb5=0x04CC36, addr_cb2=0x06CC36, rows=9, cols=16, factor=0.01, unit="mg/hub", x_label="RPM", y_label="Pedal %"),
    "torque_limiter": MapDefinition(name="Torque Limiter (Ogranicznik momentu)", dimsport_code="LC", addr_cb5=0x04D2FE, addr_cb2=0x06D2FE, rows=3, cols=23, factor=0.01, unit="mg/hub", x_label="RPM", y_label="Atm. Pressure"),
    "smoke_limiter_0c": MapDefinition(name="Smoke Limiter 0°C (Ogranicznik dymienia)", dimsport_code="QS", addr_cb5=0x04D61C, addr_cb2=0x06D61C, rows=13, cols=16, factor=0.01, unit="mg/hub", x_label="RPM", y_label="MAF mg/hub"),
    "smoke_limiter_15c": MapDefinition(name="Smoke Limiter 15°C", dimsport_code="QS", addr_cb5=0x04D7BC, addr_cb2=0x06D7BC, rows=13, cols=16, factor=0.01, unit="mg/hub", x_label="RPM", y_label="MAF mg/hub"),
    "smoke_limiter_30c": MapDefinition(name="Smoke Limiter 30°C", dimsport_code="QS", addr_cb5=0x04D95C, addr_cb2=0x06D95C, rows=13, cols=16, factor=0.01, unit="mg/hub", x_label="RPM", y_label="MAF mg/hub"),
    "boost_target": MapDefinition(name="Boost Target (Zadane doładowanie)", dimsport_code="BS", addr_cb5=0x056546, addr_cb2=0x076546, rows=10, cols=16, factor=1.0, unit="mBar", x_label="RPM", y_label="IQ mg/hub"),
    "boost_limiter": MapDefinition(name="Boost Limiter (Ogranicznik doładowania)", dimsport_code="BL", addr_cb5=0x056B3C, addr_cb2=0x076B3C, rows=10, cols=10, factor=1.0, unit="mBar", x_label="RPM", y_label="Atm. Pressure"),
    "n75_duty": MapDefinition(name="N75 Precontrol (Geometria Turbo)", dimsport_code="N75", addr_cb5=0x056852, addr_cb2=0x076852, rows=13, cols=16, factor=0.01, unit="%", x_label="RPM", y_label="IQ mg/hub"),
    "soi_map": MapDefinition(name="Start of Injection (Kąt Wtrysku)", dimsport_code="SOI", addr_cb5=0x058FBC, addr_cb2=0x078FBC, rows=14, cols=16, factor=0.01, unit="°BTDC", x_label="RPM", y_label="IQ mg/hub"),
    "egr": MapDefinition(name="EGR (Recyrkulacja spalin)", dimsport_code="EG", addr_cb5=0x055290, addr_cb2=0x075290, rows=13, cols=16, factor=0.01, unit="%", x_label="RPM", y_label="IQ mg/hub"),
    "pump_voltage": MapDefinition(name="N146 Pump Voltage (Napięcie pompy VP37)", dimsport_code="PUMP", addr_cb5=0x054468, addr_cb2=0x074468, rows=14, cols=16, factor=0.00122, unit="V", x_label="RPM", y_label="IQ mg/hub"),
    "maf_linearization": MapDefinition(name="MAF Linearization (Linearyzacja przepływomierza)", dimsport_code="—", addr_cb5=0x054A38, addr_cb2=0x074A38, rows=1, cols=32, factor=0.1, unit="kg/h", x_label="MAF Voltage", y_label="—"),
}

# ─────────────────────────────────────────────────────────────────────────────
# MAP AXES DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────
RPM_AXIS_16 = [780, 1000, 1250, 1500, 1750, 1900, 2000, 2250, 2500, 3000, 3500, 4000, 4250, 4500, 4750, 5000]
RPM_AXIS_23 = [450, 470, 600, 780, 1000, 1250, 1500, 1750, 1900, 2000, 2250, 2500, 3000, 3250, 3500, 3750, 3900, 4000, 4100, 4250, 4500, 4750, 5100]
PEDAL_AXIS_9 = [0.0, 4.0, 6.0, 10.0, 20.0, 30.0, 45.0, 60.0, 80.0]
LOAD_AXIS_10 = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 43.0]
LOAD_AXIS_13 = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 43.0, 45.0, 48.0, 51.0]
LOAD_AXIS_14 = [0.0, 0.4, 2.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 43.0, 45.0, 50.0]
SMOKE_MAF_AXIS_13 = [250, 300, 350, 400, 450, 490, 530, 580, 620, 650, 680, 750, 870]
ATMOS_AXIS_3 = [750, 850, 950]
BOOST_ATMOS_10 = [600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500]
MAF_VOLTS_32 = [round(0.16 * i, 2) for i in range(32)]

MAP_AXES = {
    "driver_wish": {"x": RPM_AXIS_16, "y": PEDAL_AXIS_9, "x_unit": "RPM", "y_unit": "Pedal %"},
    "torque_limiter": {"x": RPM_AXIS_23, "y": ATMOS_AXIS_3, "x_unit": "RPM", "y_unit": "mBar Atm"},
    "smoke_limiter_0c": {"x": RPM_AXIS_16, "y": SMOKE_MAF_AXIS_13, "x_unit": "RPM", "y_unit": "MAF mg/hub"},
    "smoke_limiter_15c": {"x": RPM_AXIS_16, "y": SMOKE_MAF_AXIS_13, "x_unit": "RPM", "y_unit": "MAF mg/hub"},
    "smoke_limiter_30c": {"x": RPM_AXIS_16, "y": SMOKE_MAF_AXIS_13, "x_unit": "RPM", "y_unit": "MAF mg/hub"},
    "boost_target": {"x": RPM_AXIS_16, "y": LOAD_AXIS_10, "x_unit": "RPM", "y_unit": "IQ mg/hub"},
    "boost_limiter": {"x": RPM_AXIS_16, "y": BOOST_ATMOS_10, "x_unit": "RPM", "y_unit": "Atm. Press mBar"},
    "n75_duty": {"x": RPM_AXIS_16, "y": LOAD_AXIS_13, "x_unit": "RPM", "y_unit": "IQ mg/hub"},
    "soi_map": {"x": RPM_AXIS_16, "y": LOAD_AXIS_14, "x_unit": "RPM", "y_unit": "IQ mg/hub"},
    "egr": {"x": RPM_AXIS_16, "y": LOAD_AXIS_13, "x_unit": "RPM", "y_unit": "IQ mg/hub"},
    "pump_voltage": {"x": RPM_AXIS_16, "y": LOAD_AXIS_14, "x_unit": "RPM", "y_unit": "IQ mg/hub"},
    "maf_linearization": {"x": MAF_VOLTS_32, "y": [1.0], "x_unit": "Voltage V", "y_unit": "MAF"},
}




# ─────────────────────────────────────────────────────────────────────────────
# KLASA: ODCZYT BINARNEGO WSADU ECU
# ─────────────────────────────────────────────────────────────────────────────

class ECUBinaryReader:
    EXPECTED_SIZE = 524288  # 512 KB

    def __init__(self, bin_path: str):
        self.bin_path = bin_path
        self.data = b""
        self.header_info = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.bin_path):
            raise FileNotFoundError(f"Plik binarny nie istnieje: {self.bin_path}")

        with open(self.bin_path, "rb") as f:
            self.data = bytearray(f.read())

        self._parse_header()
        log.info(f"Wczytano wsad binarny: {self.bin_path} ({len(self.data)} bajtów)")

    def _parse_header(self):
        import re
        try:
            ascii_data = self.data.decode("ascii", errors="ignore")
            # Szukamy VAG HW np. 074906018AJ, 074906021M
            vag_match = re.search(r'(074\s*906\s*\w{3,4})', ascii_data)
            if vag_match:
                self.header_info["vag_hw"] = vag_match.group(1).replace(" ", "")
                
            # Szukamy Bosch HW np. 0281010461, 0281001764
            bosch_match = re.search(r'(0\s*281\s*\d{3}\s*\d{3})', ascii_data)
            if bosch_match:
                self.header_info["bosch_hw"] = bosch_match.group(1).replace(" ", "")

            # Szukamy Software (1037xxxxxx lub 3xxxxx)
            sw_match = re.search(r'(1037\d{6}|\d{6})', ascii_data)
            if sw_match:
                self.header_info["software"] = sw_match.group(1)
                
        except Exception as e:
            log.warning(f"Nie udało się w pełni zdekodować nagłówka ECU: {e}")

    def read_uint16_le(self, offset: int) -> int:
        return struct.unpack("<H", self.data[offset : offset + 2])[0]

    def read_map(self, map_def: MapDefinition, codeblock: int = 5) -> List[List[float]]:
        base_addr = map_def.addr_cb5 if codeblock == 5 else map_def.addr_cb2
        matrix = []

        for r in range(map_def.rows):
            row = []
            for c in range(map_def.cols):
                offset = base_addr + (r * map_def.cols + c) * 2
                raw_val = self.read_uint16_le(offset)
                row.append(round(raw_val * map_def.factor, 3))
            matrix.append(row)

        return matrix

    def get_map_summary(self, map_def: MapDefinition, codeblock: int = 5) -> Dict:
        matrix = self.read_map(map_def, codeblock)
        all_vals = [v for row in matrix for v in row]
        return {
            "name": map_def.name,
            "dimsport": map_def.dimsport_code,
            "address": hex(map_def.addr_cb5 if codeblock == 5 else map_def.addr_cb2),
            "size": f"{map_def.rows}x{map_def.cols}",
            "unit": map_def.unit,
            "min": round(min(all_vals), 2),
            "max": round(max(all_vals), 2),
            "mean": round(sum(all_vals) / len(all_vals), 2),
            "is_flat": min(all_vals) == max(all_vals),
        }

    def write_uint16_le(self, offset: int, value: int) -> None:
        """Zapisuje wartość 16-bitową (Little-Endian) pod zadanym offsetem."""
        struct.pack_into("<H", self.data, offset, value)

    def write_map(self, map_def: MapDefinition, matrix: List[List[float]], codeblock: int = 5) -> None:
        """Zapisuje zmodyfikowaną macierz do podanej mapy."""
        base_addr = map_def.addr_cb5 if codeblock == 5 else map_def.addr_cb2
        
        for r in range(map_def.rows):
            for c in range(map_def.cols):
                val_float = matrix[r][c]
                raw_val = int(round(val_float / map_def.factor))
                
                # Zabezpieczenie limitów dla wartości całkowitych uint16
                if raw_val < 0: raw_val = 0
                if raw_val > 65535: raw_val = 65535
                
                offset = base_addr + (r * map_def.cols + c) * 2
                self.write_uint16_le(offset, raw_val)
                
    def save_bin(self, output_path: str) -> None:
        """Zapisuje obecny stan bytearray do pliku binarnego."""
        with open(output_path, "wb") as f:
            f.write(self.data)
        log.info(f"Zapisano zmodyfikowany BIN do: {output_path}")



# ─────────────────────────────────────────────────────────────────────────────
# KLASA: PARSER LOGÓW VCDS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class VCDSDataPoint:
    timestamp: float = 0.0
    rpm: float = 0.0
    
    # Grupa 001
    iq_actual: float = 0.0      # Injected Quantity
    pump_voltage: float = 0.0   # Napięcie nastawnika (Mod. Piston Displ)
    
    # Grupa 003 / 010
    maf_req: float = 0.0        # MAF zadane
    maf_actual: float = 0.0     # MAF zmierzone
    egr_duty: float = 0.0       # EGR wysterowanie
    atmos_press: float = 0.0    # Ciśnienie barometryczne (Grupa 010)
    
    # Grupa 004
    soi_req: float = 0.0        # Start of Injection Zadany
    soi_act: float = 0.0        # Start of Injection Aktualny
    cold_start_duty: float = 0.0 # Wysterowanie zaworu kąta wtrysku
    
    # Grupa 008
    iq_driver: float = 0.0      # Życzenie kierowcy (mg/hub)
    iq_torque: float = 0.0      # Ogranicznik momentu (mg/hub)
    iq_smoke: float = 0.0       # Ogranicznik dymienia MAF (mg/hub)
    
    # Grupa 011
    boost_req: float = 0.0      # Ciśnienie zadane (mBar)
    boost_act: float = 0.0      # Ciśnienie aktualne (mBar)
    n75_duty: float = 0.0       # Wysterowanie N75 (%)
    
    coolant_temp: float = 0.0   # Temperatura płynu chłodzącego (°C)


class VCDSLogParser:
    def __init__(self, csv_paths: List[str]):
        self.csv_paths = csv_paths if isinstance(csv_paths, list) else [csv_paths]
        self.data_points: List[VCDSDataPoint] = []
        self._parse_all()

    def _detect_delimiter(self, sample: str) -> str:
        semicolons = sample.count(";")
        commas = sample.count(",")
        return ";" if semicolons > commas else ","

    def _parse_all(self):
        """Łączy dane z wielu plików CSV VCDS (PL/EN/DE)."""
        all_dps = {}
        import re

        for path in self.csv_paths:
            if not os.path.exists(path):
                log.error(f"Plik logu VCDS nie istnieje: {path}")
                continue

            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    sample = f.read(2048)
                    f.seek(0)
                    delimiter = self._detect_delimiter(sample)
                    rows = list(csv.reader(f, delimiter=delimiter))

                group_row, desc_row, unit_row = None, None, None
                data_start_idx = 0

                for r_idx, r in enumerate(rows[:12]):
                    r_str = " ".join(r).lower()
                    if "grupa" in r_str or "group" in r_str:
                        group_row = r
                    elif any(kw in r_str for kw in ["obroty", "rpm", "1/min", "dawka", "ciśnienie", "cinienie", "ilość", "ilo", "maf", 'boost', "wyst", "kąt", "kat"]):
                        if not desc_row:
                            desc_row = r
                    elif any(kw in r_str for kw in ["/min", "mg/suw", "mg/str", "mbar", "%", "*pgmp", "btdc", "atdc", "*c"]):
                        if not unit_row:
                            unit_row = r
                            data_start_idx = r_idx + 1

                if not desc_row or not unit_row:
                    log.warning(f"Nie udało się wykryć układu nagłówków VCDS w pliku: {os.path.basename(path)}")
                    continue

                col_map = self._build_column_map(group_row, desc_row, unit_row)
                log.info(f"Nagłówki VCDS zdekodowane z: {os.path.basename(path)} (Grupy: {set(col_map.keys())})")

                for r in rows[data_start_idx:]:
                    if not r or len(r) < 3:
                        continue
                    if not any(c.strip().replace(".", "", 1).replace("-", "", 1).isdigit() for c in r[1:]):
                        continue

                    dp = self._parse_data_row(r, col_map)
                    if dp and dp.rpm > 500:
                        rpm_key = round(dp.rpm, -1)
                        if rpm_key not in all_dps:
                            all_dps[rpm_key] = dp
                        else:
                            self._merge_dps(all_dps[rpm_key], dp)

            except Exception as e:
                log.error(f"Błąd parsowania logu VCDS ({path}): {e}")

        self.data_points = sorted(list(all_dps.values()), key=lambda x: x.rpm)
        log.info(f"Ostatecznie zebrano {len(self.data_points)} unikalnych profili RPM z wszystkich logów.")

    def _build_column_map(self, group_row: Optional[List[str]], desc_row: List[str], unit_row: List[str]) -> Dict[str, int]:
        import re
        col_map = {}
        curr_grp = "000"
        max_cols = max(len(desc_row), len(unit_row))

        for i in range(max_cols):
            if group_row and i < len(group_row):
                grp_match = re.search(r"(\d{3})", group_row[i])
                if grp_match:
                    curr_grp = grp_match.group(1)

            desc = desc_row[i].strip().lower() if i < len(desc_row) else ""
            unit = unit_row[i].strip().lower() if i < len(unit_row) else ""

            # RPM
            if "obroty" in desc or "rpm" in desc or "/min" in unit or "1/min" in unit:
                if "rpm" not in col_map:
                    col_map["rpm"] = i

            # Grupa 001
            elif curr_grp == "001":
                if "dawka" in desc or "mg" in unit or "iq" in desc:
                    col_map["iq_actual"] = i
                elif "napięcie" in desc or "voltage" in desc or unit == "v":
                    col_map["pump_voltage"] = i
                elif "temp" in desc or "*c" in unit or "°c" in unit:
                    col_map["coolant_temp"] = i

            # Grupa 003
            elif curr_grp == "003":
                if "ilość" in desc or "maf" in desc or "mg/suw" in unit or "mg/str" in unit:
                    if "maf_req" not in col_map:
                        col_map["maf_req"] = i
                    elif "maf_actual" not in col_map:
                        col_map["maf_actual"] = i
                elif "cykl" in desc or "duty" in desc or "%" in unit:
                    col_map["egr_duty"] = i

            # Grupa 004
            elif curr_grp == "004":
                if "kąt" in desc or "soi" in desc or "*pgmp" in unit or "btdc" in unit or "atdc" in unit:
                    if "soi_req" not in col_map:
                        col_map["soi_req"] = i
                    elif "soi_act" not in col_map:
                        col_map["soi_act"] = i
                elif "%" in unit or "cykl" in desc:
                    col_map["cold_start_duty"] = i

            # Grupa 008
            elif curr_grp == "008":
                if "dawka" in desc or "mg" in unit or "iq" in desc:
                    if "iq_driver" not in col_map:
                        col_map["iq_driver"] = i
                    elif "iq_torque" not in col_map:
                        col_map["iq_torque"] = i
                    elif "iq_smoke" not in col_map:
                        col_map["iq_smoke"] = i

            # Grupa 010
            elif curr_grp == "010":
                if "ilość" in desc or "maf" in desc:
                    col_map["maf_actual"] = i
                elif "ciśnienie" in desc or "mbar" in unit or "press" in desc:
                    if "atmos_press" not in col_map:
                        col_map["atmos_press"] = i
                    elif "boost_act" not in col_map:
                        col_map["boost_act"] = i
                elif "obciążenie" in desc or "%" in unit:
                    col_map["iq_driver"] = i

            # Grupa 011
            elif curr_grp == "011":
                if "ciśnienie" in desc or "mbar" in unit or "boost" in desc:
                    if "boost_req" not in col_map:
                        col_map["boost_req"] = i
                    elif "boost_act" not in col_map:
                        col_map["boost_act"] = i
                elif "cykl" in desc or "n75" in desc or "%" in unit:
                    col_map["n75_duty"] = i

            # Grupa 019
            elif curr_grp == "019" and unit == "v":
                if "pump_voltage" not in col_map:
                    col_map["pump_voltage"] = i

            # Zapasowy odczyt ogólny
            else:
                if ("obroty" in desc or "rpm" in desc or "/min" in unit) and "rpm" not in col_map:
                    col_map["rpm"] = i
                elif ("mbar" in unit or "boost" in desc) and "boost_act" not in col_map:
                    col_map["boost_act"] = i
                elif ("mg/suw" in unit or "mg/str" in unit) and "iq_actual" not in col_map:
                    col_map["iq_actual"] = i

        return col_map

    def _parse_data_row(self, row: List[str], col_map: Dict[str, int]) -> Optional[VCDSDataPoint]:
        dp = VCDSDataPoint()
        try:
            for field_name, col_idx in col_map.items():
                if col_idx < len(row):
                    raw = row[col_idx].strip().replace(",", ".").replace("%", "").replace(" ", "")
                    # Obsługa ATDC (minus) i BTDC (plus) z VCDS
                    is_atdc = "atdc" in raw.lower()
                    raw = raw.lower().replace("btdc", "").replace("atdc", "").strip()
                    
                    if raw and raw.replace(".", "", 1).replace("-", "", 1).isdigit():
                        val = float(raw)
                        if is_atdc: val = -val
                        setattr(dp, field_name, val)
            return dp
        except (ValueError, IndexError):
            return None
            
    def _merge_dps(self, target: VCDSDataPoint, source: VCDSDataPoint):
        for field_name in target.__dataclass_fields__:
            v_t = getattr(target, field_name)
            v_s = getattr(source, field_name)
            if v_t == 0.0 and v_s != 0.0:
                setattr(target, field_name, v_s)

    def get_wot_data(self, min_rpm: float = 1300.0) -> List[VCDSDataPoint]:
        return [dp for dp in self.data_points if dp.rpm >= min_rpm and (dp.iq_driver >= 35.0 or dp.boost_req >= 1500.0)]


# ─────────────────────────────────────────────────────────────────────────────
# KLASA: ANALIZATOR KORELACJI (LOG ↔ MAPA ECU)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DiagnosticFinding:
    severity: str
    category: str
    rpm_range: str
    description: str
    recommendation: str
    map_to_adjust: str = ""


class EDC15Analyzer:
    def __init__(self, ecu: ECUBinaryReader, vcds: Optional[VCDSLogParser] = None):
        self.ecu = ecu
        self.vcds = vcds
        self.findings: List[DiagnosticFinding] = []

    def audit_maps(self, codeblock: int = 5) -> List[Dict]:
        results = []
        for key, map_def in MAP_DEFINITIONS.items():
            summary = self.ecu.get_map_summary(map_def, codeblock)
            results.append(summary)

            if key == "egr" and summary["is_flat"]:
                self.findings.append(DiagnosticFinding(severity="INFO", category="EGR_OFF", rpm_range="Calosc", description=f"EGR wylaczony.", recommendation="Brak dzialan.", map_to_adjust="EGR"))
            if key == "torque_limiter" and summary["max"] > 50.0:
                self.findings.append(DiagnosticFinding(severity="WARNING", category="HIGH_TORQUE", rpm_range="Calosc", description=f"Ogranicznik momentu wysoko ({summary['max']} mg). Ryzyko dla sprzegla.", recommendation="Sprawdz DMF.", map_to_adjust="Torque Limiter (LC)"))
            if key == "boost_target" and summary["max"] > 2200.0:
                self.findings.append(DiagnosticFinding(severity="CRITICAL", category="BOOST_EXCESSIVE", rpm_range="Calosc", description=f"Zadane cisnienie ({summary['max']} mBar) zbyt wysokie dla seryjnego turbo.", recommendation="Obniz do max 2100mBar.", map_to_adjust="Boost Target (BS)"))
            if key == "pump_voltage" and summary["max"] > 4.6:
                self.findings.append(DiagnosticFinding(severity="WARNING", category="PUMP_VOLTAGE_HIGH", rpm_range="Calosc", description=f"Napiecie pompy ({summary['max']}V) wykracza poza limit fizyczny VP37 (4.5V).", recommendation="Powyzej 4.5V pompa zamyka nastawnik, ryzykujesz szarpanie/blad.", map_to_adjust="Pump Voltage"))

        return results

    # ── NOWA ANALIZA: POMPA (Grupa 001) ──────────────────────────────────────

    def analyze_pump_voltage(self) -> None:
        if not self.vcds: return
        max_v = max([dp.pump_voltage for dp in self.vcds.data_points if dp.pump_voltage > 0], default=0)
        
        if max_v >= 4.45:
            self.findings.append(DiagnosticFinding(
                severity="CRITICAL",
                category="PUMP_VOLTAGE_MAX",
                rpm_range="WOT",
                description=f"Nastawnik pompy (VP37) osiaga limit fizyczny ({max_v:.2f}V).",
                recommendation="Wtryskiwacze sa za male, pompa nie jest w stanie dac wiecej paliwa.",
                map_to_adjust="N146 Pump Voltage"
            ))

    # ── NOWA ANALIZA: MAF (Grupa 003) ────────────────────────────────────────

    def analyze_maf_health(self) -> None:
        if not self.vcds: return
        wot_data = self.vcds.get_wot_data()
        low_maf_count = 0
        
        for dp in wot_data:
            if dp.maf_actual > 0 and dp.maf_req > 0:
                if dp.maf_actual < dp.maf_req * 0.9 and dp.boost_act > 1900: 
                    low_maf_count += 1
                    
        if low_maf_count > 4:
            self.findings.append(DiagnosticFinding(
                severity="WARNING",
                category="MAF_LOW_READING",
                rpm_range="WOT",
                description="Przeplywomierz (G70) mierzy znaczaco mniej powietrza niz jest zadane, mimo ladowania turbo.",
                recommendation="Przeczysc/Wymien przeplywomierz G70 lub zastosuj wklad od ARL.",
                map_to_adjust="Brak"
            ))

    # ── NOWA ANALIZA: KAT WTRYSKU (Grupa 004) ────────────────────────────────

    def analyze_soi_deviation(self) -> None:
        if not self.vcds: return
        wot_data = self.vcds.get_wot_data()
        lag_count = 0
        
        for dp in wot_data:
            if dp.soi_req > 0 and dp.soi_act > 0:
                delta = dp.soi_req - dp.soi_act
                if delta > 1.5:  # Zbyt pozny wtrysk
                    lag_count += 1
                    
        if lag_count > 3:
            self.findings.append(DiagnosticFinding(
                severity="CRITICAL",
                category="SOI_LAG",
                rpm_range="WOT",
                description="Kat wtrysku nie nadaza za mapa (wtrysk nastepuje za pozno). Prowadzi to do dymienia i wysokiego EGT.",
                recommendation="Zwieksz cisnienie wewnatrzpompy, zmien wtryski, lub zmniejsz wyprzedzenie w mapie SOI.",
                map_to_adjust="SOI Map"
            ))

    # ── ANALIZA LIMITEROW I TURBO (Grupa 008, 011) ───────────────────────────

    def analyze_limiters(self) -> None:
        if not self.vcds: return
        stats = {"DRIVER_WISH": 0, "TORQUE_LIMITER": 0, "SMOKE_LIMITER": 0}
        wot_data = self.vcds.get_wot_data()

        for dp in wot_data:
            iqs = {"DRIVER_WISH": dp.iq_driver, "TORQUE_LIMITER": dp.iq_torque, "SMOKE_LIMITER": dp.iq_smoke}
            if all(v > 0 for v in iqs.values()):
                active = min(iqs, key=iqs.get)
                stats[active] += 1

        total = sum(stats.values())
        if total > 0 and (stats["SMOKE_LIMITER"] / total) > 0.4:
            self.findings.append(DiagnosticFinding(
                severity="WARNING",
                category="SMOKE_LIMITING",
                rpm_range="WOT",
                description="Ogranicznik dymienia blokuje dawke w >40% logu. Przeplywka tnie dawki.",
                recommendation="Sprawdz MAF i szczelnosc dolotu.",
                map_to_adjust="Smoke Limiter (QS)"
            ))

    def analyze_boost_deviation(self) -> None:
        if not self.vcds: return
        lag_count = spike_count = 0

        for dp in self.vcds.data_points:
            if dp.boost_req < 1200: continue
            delta = dp.boost_act - dp.boost_req
            if delta < -150: lag_count += 1
            elif delta > 150: spike_count += 1

        if lag_count > 5:
            self.findings.append(DiagnosticFinding(severity="CRITICAL", category="TURBO_LAG", rpm_range="WOT", description="Turbo Lag > 150mBar. Auto reaguje pozno na gaz.", recommendation="Popraw mape N75 (Precontrol) lub skroc sztange.", map_to_adjust="N75 Precontrol"))
        if spike_count > 5:
            self.findings.append(DiagnosticFinding(severity="WARNING", category="BOOST_SPIKE", rpm_range="WOT", description="Boost Spike > 150mBar. Turbo przeladowuje, ryzyko Notlauf.", recommendation="Rozluznij N75 lub sprawdz geometrie VNT.", map_to_adjust="N75 Precontrol"))

    def get_map_log_matrix(self, map_key: str, codeblock: int = 5) -> Tuple[List[List[Optional[float]]], List[List[Optional[float]]]]:
        """
        Dla danej mapy tworzy macierz wartości z logów VCDS oraz macierz różnic (Log - Map).
        Zwraca: (log_matrix, diff_matrix)
        """
        map_def = MAP_DEFINITIONS.get(map_key)
        if not map_def or not self.vcds or not self.vcds.data_points:
            rows = map_def.rows if map_def else 1
            cols = map_def.cols if map_def else 1
            return [[None]*cols for _ in range(rows)], [[None]*cols for _ in range(rows)]

        ecu_matrix = self.ecu.read_map(map_def, codeblock=codeblock)
        axes = MAP_AXES.get(map_key, {})
        x_axis = axes.get("x", RPM_AXIS_16)
        y_axis = axes.get("y", LOAD_AXIS_13)

        rows, cols = map_def.rows, map_def.cols
        cell_samples = [[[] for _ in range(cols)] for _ in range(rows)]

        for dp in self.vcds.data_points:
            if dp.rpm < 500: continue

            c_idx = min(range(cols), key=lambda i: abs(x_axis[i] - dp.rpm))

            y_val = 0.0
            log_val = 0.0

            if map_key == "n75_duty":
                y_val = dp.iq_actual
                log_val = dp.n75_duty if dp.n75_duty > 0 else dp.boost_act
            elif map_key == "boost_target":
                y_val = dp.iq_actual
                log_val = dp.boost_act
            elif map_key == "boost_limiter":
                y_val = dp.atmos_press if dp.atmos_press > 0 else 1000.0
                log_val = dp.boost_act
            elif map_key.startswith("smoke_limiter"):
                y_val = dp.maf_actual
                log_val = dp.iq_actual if dp.iq_actual > 0 else dp.iq_smoke
            elif map_key == "soi_map":
                y_val = dp.iq_actual
                log_val = dp.soi_act
            elif map_key == "pump_voltage":
                y_val = dp.iq_actual
                log_val = dp.pump_voltage
            elif map_key == "torque_limiter":
                y_val = dp.atmos_press if dp.atmos_press > 0 else 1013.0
                log_val = dp.iq_torque if dp.iq_torque > 0 else dp.iq_actual
            elif map_key == "driver_wish":
                y_val = 80.0 if dp.iq_driver > 30 else 0.0
                log_val = dp.iq_driver
            else:
                continue

            if log_val > 0:
                r_idx = min(range(rows), key=lambda j: abs(y_axis[j] - y_val))
                cell_samples[r_idx][c_idx].append(log_val)

        log_matrix = []
        diff_matrix = []

        for r in range(rows):
            log_row = []
            diff_row = []
            for c in range(cols):
                samples = cell_samples[r][c]
                if samples:
                    avg_log = round(sum(samples) / len(samples), 2)
                    map_val = ecu_matrix[r][c]
                    diff = round(avg_log - map_val, 2)
                    log_row.append(avg_log)
                    diff_row.append(diff)
                else:
                    log_row.append(None)
                    diff_row.append(None)
            log_matrix.append(log_row)
            diff_matrix.append(diff_row)

        return log_matrix, diff_matrix

    def run_autotune_all(self, codeblock: int = 5) -> Dict:
        """
        Automatyczne wyliczanie korekt map na podstawie logów VCDS.
        """
        if not self.vcds or not self.vcds.data_points:
            return {"modified_maps": {}, "changes_log": ["Brak logów VCDS do automatycznego strojenia."], "total_changes": 0}

        results = {"modified_maps": {}, "changes_log": [], "total_changes": 0}
        
        # 1. N75 Precontrol Auto-Tune
        n75_def = MAP_DEFINITIONS.get("n75_duty")
        if n75_def:
            n75_curr = self.ecu.read_map(n75_def, codeblock=codeblock)
            n75_new = [row[:] for row in n75_curr]
            n75_changes = 0

            for dp in self.vcds.data_points:
                if dp.rpm < 1400 or dp.boost_req < 1500: continue
                delta_boost = dp.boost_act - dp.boost_req
                if abs(delta_boost) > 40.0:
                    c_idx = min(range(n75_def.cols), key=lambda i: abs(RPM_AXIS_16[i] - dp.rpm))
                    r_idx = min(range(n75_def.rows), key=lambda j: abs(LOAD_AXIS_13[j] - dp.iq_actual))
                    
                    adj = delta_boost / 25.0
                    adj = max(-8.0, min(8.0, adj))
                    
                    old_v = n75_new[r_idx][c_idx]
                    new_v = round(max(10.0, min(95.0, old_v + adj)), 2)
                    if old_v != new_v:
                        n75_new[r_idx][c_idx] = new_v
                        n75_changes += 1
                        results["changes_log"].append(f"[N75 Turbo] RPM={dp.rpm:.0f}, IQ={dp.iq_actual:.1f}mg | Boost req={dp.boost_req:.0f}, act={dp.boost_act:.0f} ({delta_boost:+.0f}mbar) => N75[{r_idx}][{c_idx}]: {old_v}% -> {new_v}%")

            if n75_changes > 0:
                results["modified_maps"]["n75_duty"] = n75_new
                results["total_changes"] += n75_changes

        # 2. Smoke Limiter Auto-Tune
        for smoke_key in ["smoke_limiter_0c", "smoke_limiter_15c", "smoke_limiter_30c"]:
            smoke_def = MAP_DEFINITIONS.get(smoke_key)
            if smoke_def:
                smoke_curr = self.ecu.read_map(smoke_def, codeblock=codeblock)
                smoke_new = [row[:] for row in smoke_curr]
                smoke_changes = 0

                for dp in self.vcds.get_wot_data():
                    if dp.maf_actual < 400: continue
                    safe_iq_limit = round(dp.maf_actual / 17.0, 2)
                    c_idx = min(range(smoke_def.cols), key=lambda i: abs(RPM_AXIS_16[i] - dp.rpm))
                    r_idx = min(range(smoke_def.rows), key=lambda j: abs(LOAD_AXIS_13[j] - dp.maf_actual))

                    old_v = smoke_new[r_idx][c_idx]
                    if old_v < safe_iq_limit and safe_iq_limit <= 65.0:
                        smoke_new[r_idx][c_idx] = safe_iq_limit
                        smoke_changes += 1
                        results["changes_log"].append(f"[{smoke_def.name}] RPM={dp.rpm:.0f}, MAF={dp.maf_actual:.0f}mg => Optymalizacja dymienia [{r_idx}][{c_idx}]: {old_v}mg -> {safe_iq_limit}mg")

                if smoke_changes > 0:
                    results["modified_maps"][smoke_key] = smoke_new
                    results["total_changes"] += smoke_changes

        # 3. SOI Auto-Tune
        soi_def = MAP_DEFINITIONS.get("soi_map")
        if soi_def:
            soi_curr = self.ecu.read_map(soi_def, codeblock=codeblock)
            soi_new = [row[:] for row in soi_curr]
            soi_changes = 0

            for dp in self.vcds.get_wot_data():
                if dp.soi_req > 0 and dp.soi_act > 0:
                    lag = dp.soi_req - dp.soi_act
                    if lag > 1.2:
                        c_idx = min(range(soi_def.cols), key=lambda i: abs(RPM_AXIS_16[i] - dp.rpm))
                        r_idx = min(range(soi_def.rows), key=lambda j: abs(LOAD_AXIS_14[j] - dp.iq_actual))
                        old_v = soi_new[r_idx][c_idx]
                        new_v = round(min(28.0, old_v + round(lag * 0.5, 2)), 2)
                        if old_v != new_v:
                            soi_new[r_idx][c_idx] = new_v
                            soi_changes += 1
                            results["changes_log"].append(f"[SOI Kąt Wtrysku] RPM={dp.rpm:.0f}, IQ={dp.iq_actual:.1f}mg | Lag SOI: req={dp.soi_req:.1f}°, act={dp.soi_act:.1f}° => Korekta SOI[{r_idx}][{c_idx}]: {old_v}° -> {new_v}°")

            if soi_changes > 0:
                results["modified_maps"]["soi_map"] = soi_new
                results["total_changes"] += soi_changes

        return results

    def execute_all_analysis(self) -> None:
        self.analyze_pump_voltage()
        self.analyze_maf_health()
        self.analyze_soi_deviation()
        self.analyze_limiters()
        self.analyze_boost_deviation()



# ─────────────────────────────────────────────────────────────────────────────
# MODUL WIZUALIZACJI (matplotlib)
# ─────────────────────────────────────────────────────────────────────────────

def try_import_plt():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        return None

def plot_advanced_diagnostics(vcds: VCDSLogParser, output_dir: str):
    plt = try_import_plt()
    if not plt or not vcds.data_points:
        return

    wot_data = vcds.get_wot_data()
    rpms = [dp.rpm for dp in wot_data]

    # --- 1. WYKRES BOOST & N75 ---
    if any(dp.boost_req > 0 for dp in wot_data):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        fig.suptitle("EDC15VM+ - Turbo Doladowanie (011)", fontsize=14, fontweight="bold")
        ax1.plot(rpms, [dp.boost_req for dp in wot_data], "b-", label="Cisnienie Zadane")
        ax1.plot(rpms, [dp.boost_act for dp in wot_data], "r-", label="Cisnienie Aktualne")
        ax1.set_ylabel("[mBar]"); ax1.legend(); ax1.grid(True)
        ax2.plot(rpms, [dp.n75_duty for dp in wot_data], "g-", label="N75 Duty Cycle (%)")
        ax2.set_xlabel("RPM"); ax2.set_ylabel("[%]"); ax2.legend(); ax2.grid(True)
        plt.savefig(os.path.join(output_dir, "wykres_01_boost_011.png"), dpi=150, bbox_inches="tight")
        plt.close()

    # --- 2. WYKRES LIMITEROW DAWKI ---
    if any(dp.iq_driver > 0 for dp in wot_data):
        fig, ax = plt.subplots(figsize=(14, 7))
        fig.suptitle("EDC15VM+ - Limitory Dawki (008)", fontsize=14, fontweight="bold")
        ax.plot(rpms, [dp.iq_driver for dp in wot_data], "b-", label="Driver Wish")
        ax.plot(rpms, [dp.iq_torque for dp in wot_data], "orange", label="Torque Limiter")
        ax.plot(rpms, [dp.iq_smoke for dp in wot_data], "r-", label="Smoke Limiter (MAF)")
        ax.set_xlabel("RPM"); ax.set_ylabel("[mg/hub]"); ax.legend(); ax.grid(True)
        plt.savefig(os.path.join(output_dir, "wykres_02_limiters_008.png"), dpi=150, bbox_inches="tight")
        plt.close()

    # --- 3. WYKRES KATA WTRYSKU (SOI) ---
    if any(dp.soi_req > 0 for dp in wot_data):
        fig, ax = plt.subplots(figsize=(14, 7))
        fig.suptitle("EDC15VM+ - Kat Wyprzedzenia Wtrysku (004)", fontsize=14, fontweight="bold")
        ax.plot(rpms, [dp.soi_req for dp in wot_data], "b-", label="SOI Zadany (*BTDC)")
        ax.plot(rpms, [dp.soi_act for dp in wot_data], "r-", label="SOI Aktualny (*BTDC)")
        ax.set_xlabel("RPM"); ax.set_ylabel("[*BTDC]"); ax.legend(); ax.grid(True)
        plt.savefig(os.path.join(output_dir, "wykres_03_soi_004.png"), dpi=150, bbox_inches="tight")
        plt.close()

    # --- 4. WYKRES PUMP VOLTAGE & MAF ---
    if any(dp.pump_voltage > 0 for dp in wot_data):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        fig.suptitle("EDC15VM+ - Pompa VP37 i Powietrze (001, 003)", fontsize=14, fontweight="bold")
        
        ax1.plot(rpms, [dp.pump_voltage for dp in wot_data], "m-", label="Napiecie Nastawnika (V)", linewidth=2)
        ax1.axhline(y=4.5, color="red", linestyle="--", label="Limit Fizyczny (4.5V)")
        ax1.set_ylabel("Napiecie [V]"); ax1.legend(); ax1.grid(True)
        
        if any(dp.maf_req > 0 for dp in wot_data):
            ax2.plot(rpms, [dp.maf_req for dp in wot_data], "b-", label="MAF Zadane (mg/str)")
            ax2.plot(rpms, [dp.maf_actual for dp in wot_data], "c-", label="MAF Zmierzone (mg/str)")
            ax2.set_ylabel("Przeplyw [mg/str]"); ax2.legend(); ax2.grid(True)
        
        ax2.set_xlabel("RPM")
        plt.savefig(os.path.join(output_dir, "wykres_04_pump_maf.png"), dpi=150, bbox_inches="tight")
        plt.close()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    BIN_FILE = r"d:\t4\cks ok"
    # Tutaj mozna wkleic sciezki do wielu plikow CSV logow (np. 003+008+011 oraz 001+004)
    VCDS_LOGS = [] 
    OUTPUT_DIR = r"d:\t4"

    print("=" * 80)
    print("  EDC15VM+ VCDS Master Log Analyzer (FULL GROUPS)")
    print("=" * 80)

    ecu = ECUBinaryReader(BIN_FILE)
    
    vcds = None
    if VCDS_LOGS:
        vcds = VCDSLogParser(VCDS_LOGS)

    analyzer = EDC15Analyzer(ecu, vcds)

    print("\n[Audyt map] Codeblock 5:")
    results_cb5 = analyzer.audit_maps(codeblock=5)
    for r in results_cb5:
        status = "[LOCKED] OFF" if r["is_flat"] else f"{r['min']} - {r['max']}"
        print(f"  {r['dimsport']:4s} | {r['name']:50s} | {r['address']:10s} | {status} {r['unit']}")

    if vcds and vcds.data_points:
        print("\n[Analiza logow] Trwa ocena VCDS (Grupy 001, 003, 004, 008, 010, 011)...")
        analyzer.execute_all_analysis()
        plot_advanced_diagnostics(vcds, OUTPUT_DIR)

    if analyzer.findings:
        print("\n[Odkrycia] Diagnostyczne:")
        for f in analyzer.findings:
            icon = {"CRITICAL": "[X]", "WARNING": "[!]", "INFO": "[i]"}.get(f.severity, "[-]")
            print(f"  {icon} [{f.severity}] {f.category}: {f.description[:80]}...")

    print(f"\n[SUKCES] Skrypt gotowy. Czekam na pliki CSV VCDS, aby podpiac je w VCDS_LOGS.")
    print("=" * 80)

if __name__ == "__main__":
    main()
