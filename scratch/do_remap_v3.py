import sys
import struct
sys.path.insert(0, r"d:\t4")
from edc15_analyzer import ECUBinaryReader, MAP_DEFINITIONS

def remap_v3(input_path, output_path):
    ecu = ECUBinaryReader(input_path)
    
    def apply_transform(map_def, codeblock, transform_fn):
        matrix = ecu.read_map(map_def, codeblock)
        for r in range(len(matrix)):
            for c in range(len(matrix[r])):
                val = matrix[r][c]
                matrix[r][c] = transform_fn(r, c, val)
        ecu.write_map(map_def, matrix, codeblock)

    # 1. Torque Limiter (3 wiersze x 23 kolumny)
    # Kolumny obrotów: 6(1500), 7(1750), 8(1900), 9(2000)
    # Wszystkie 3 wiersze ulegną zmianie dla ciśnień
    def trans_torque(r, c, val):
        # Dół i środek
        if c == 6: return max(val, 45.0)  # 1500 rpm 
        if c == 7: return max(val, 52.0)  # 1750 rpm
        if c == 8: return max(val, 58.0)  # 1900 rpm
        if 9 <= c <= 15: return max(val, 60.0) # 2000 - 3750 rpm max ogień
        
        # Płynne łagodzenie u góry
        if c > 15 and val > 40.0:
            diff = val - 40.0
            return round(40.0 + diff * 1.5, 2)
        return val

    # 2. Driver Wish (9 wierszy gazu x 16 kolumn obrotów)
    # Zrzut pokazuje: Y(RPM) od dołu do góry w VAG EDC (więc 9 to pozycje, 16 to RPM, czy odwrotnie?)
    # Nasz map definitions mówi: Y_len=9, X_len=16. 
    # Dla pedału > 80% (najwyższe 2 wiersze) pompujemy po prostu wielką wartość 61 mg wszędzie tam, 
    # gdzie było więcej niż 30, uwalniając 100% reakcji z dołu na wdepnięcie,
    # w końcu to Torque decyduje co wejdzie realnie!
    def trans_dw(r, c, val):
        # W rzędach dla najwyższego gazu (zakładam indeksy 7, 8 jeśli wiersze rosną z przepustnicą)
        if r >= 7 and val > 30.0:
            return 61.0
        return val

    # 3. Smoke Limitery (13 wierszy MAF x 16 kolumn RPM albo odwrotnie)
    # Wszędzie, gdzie MAF jest wysoki i w seryjnym oprogramowaniu puszczał pow. 35mg, zdejmujemy obroże
    # dając od 55 (dla 1500) do 60mg.
    def trans_smoke(r, c, val):
        if val > 35.0:
            # Nie patrzę na kolumnę, po prostu jeśli limiter dymu miał tu w serii luźniej, ja puszczam jeszcze luźniej
            # aby na starcie turbo "nie zatkał" mi dymienia jak turbo w T4 próbuje dmuchnąć.
            diff = val - 35.0
            return round(35.0 + diff * 1.6, 2) # max ok 60
        return val

    # 4. Boost Target (10x16)
    # Gdzie chciał > 1800, ciągniemy do 2380.
    # Żeby pomóc z dołu, podbijamy też niższe wartości. 
    def trans_boost(r, c, val):
        if val > 1400.0:
            diff = val - 1400.0
            return min(2400.0, round(1400.0 + diff * 1.5, 2))
        return val

    # 5. Boost Limiter (10x10) - Mapa
    def trans_blimit(r, c, val):
        if val > 1500.0:
            diff = val - 1500.0
            return round(1500.0 + diff * 1.5, 2)
        return val

    # 6. Pump voltage
    def trans_pump(r, c, val):
        if val > 4.0:
            diff = val - 4.0
            return round(4.0 + diff * 1.44, 3)
        return val

    for cb in [2, 5]:
        apply_transform(MAP_DEFINITIONS['torque_limiter'], cb, trans_torque)
        apply_transform(MAP_DEFINITIONS['driver_wish'], cb, trans_dw)
        apply_transform(MAP_DEFINITIONS['smoke_limiter_0c'], cb, trans_smoke)
        apply_transform(MAP_DEFINITIONS['smoke_limiter_15c'], cb, trans_smoke)
        apply_transform(MAP_DEFINITIONS['smoke_limiter_30c'], cb, trans_smoke)
        apply_transform(MAP_DEFINITIONS['boost_target'], cb, trans_boost)
        apply_transform(MAP_DEFINITIONS['boost_limiter'], cb, trans_blimit)
        apply_transform(MAP_DEFINITIONS['pump_voltage'], cb, trans_pump)
        
    # --- HARDCODED SVBL ---
    # Musimy zmodyfikować bufor binarny PRZED save_bin.
    svbl_value = 2550
    svbl_bytes = struct.pack('<H', svbl_value)
    
    # CB2 - manual (na podst. skryptu = 0x51c28 = 334888)
    ecu.data[0x51c28] = svbl_bytes[0]
    ecu.data[0x51c28+1] = svbl_bytes[1]
    
    # CB5 - automat (na podst. skryptu = 0x71c28 = 465960)
    ecu.data[0x71c28] = svbl_bytes[0]
    ecu.data[0x71c28+1] = svbl_bytes[1]
    # ----------------------
        
    ecu.save_bin(output_path)
    print("REMAP V3 (Moc z dołu + SVBL) ZAKOŃCZONY!")

if __name__ == "__main__":
    input_f = r"d:\t4\cks ok"
    output_f = r"d:\t4\cks ok_v3_z_dolu.bin"
    remap_v3(input_f, output_f)
