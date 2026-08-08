# RAPORT DIAGNOSTYCZNY EDC15VM+ — ANALIZA KORELACYJNA
## Sterownik: 074906018AJ / 0281010461 / SW: 1037362445
## Codeblock analizowany: 5

---
### 1. AUDYT WARTOŚCI MAP WE WSADZIE BINARNYM

| Mapa | Dimsport | Adres | Rozmiar | Jednostka | Min | Max | Średnia | Flat? |
| :--- | :---: | :---: | :---: | :---: | ---: | ---: | ---: | :---: |
| Driver Wish (Życzenie kierowcy) | B1 | 0x4cc36 | 9×16 | mg/hub | 0.0 | 55.0 | 20.29 | — |
| Torque Limiter (Ogranicznik momentu) | LC | 0x4d2fe | 3×23 | mg/hub | 0.0 | 50.85 | 34.3 | — |
| Smoke Limiter 0°C (Ogranicznik dymienia) | QS | 0x4d61c | 13×16 | mg/hub | 2.2 | 54.9 | 26.38 | — |
| Smoke Limiter 15°C | QS | 0x4d7bc | 13×16 | mg/hub | 2.2 | 54.9 | 26.67 | — |
| Smoke Limiter 30°C | QS | 0x4d95c | 13×16 | mg/hub | 3.2 | 55.9 | 27.89 | — |
| Boost Target (Zadane doładowanie) | BS | 0x56546 | 10×16 | mBar | 1050.0 | 2190.0 | 1483.58 | — |
| Boost Limiter (Ogranicznik doładowania) | BL | 0x56b3c | 10×10 | mBar | 1540.0 | 2190.0 | 2072.8 | — |
| EGR (Recyrkulacja spalin) | EG | 0x55290 | 13×16 | % | 85.0 | 85.0 | 85.0 | ✅ (Off) |
| N146 Pump Voltage (Napięcie pompy VP37) | — | 0x54468 | 14×16 | V | 0.0 | 35.88 | 17.97 | — |
| MAF Linearization (Linearyzacja przepływomierza) | — | 0x54a38 | 1×32 | mg/hub | 0.04 | 655.33 | 145.46 | — |
| Start IQ 1 (Dawka rozruchowa) | — | 0x4ce70 | 9×9 | mg/hub | 0.0 | 50.0 | 23.81 | — |
| Idle RPM 1 (Obroty jałowe) | — | 0x4d010 | 1×2 | RPM | 780.0 | 1140.0 | 960.0 | — |

---
### 3. ODKRYCIA DIAGNOSTYCZNE I REKOMENDACJE

#### 🟡 1. [WARNING] HIGH_TORQUE
* **Zakres RPM:** Max IQ > 50 mg/hub
* **Opis:** Ogranicznik momentu ustawiony wysoko (max: 50.85 mg/hub). Ryzyko uszkodzenia sprzęgła lub koła dwumasowego.
* **Mapa do korekty:** Torque Limiter (LC) (`0x4d2fe`)
* **Rekomendacja:** Sprawdź wytrzymałość sprzęgła i DMF. Rozważ wzmocnione sprzęgło.

#### 🟢 2. [INFO] EGR_OFF
* **Zakres RPM:** Cała mapa
* **Opis:** EGR wyłączony (stała wartość: 85.0)
* **Mapa do korekty:** EGR 01 (`0x55290`)
* **Rekomendacja:** Brak działania. EGR OFF jest standardem w Stage 1.

#### 🟡 3. [WARNING] HIGH_TORQUE
* **Zakres RPM:** Max IQ > 50 mg/hub
* **Opis:** Ogranicznik momentu ustawiony wysoko (max: 50.85 mg/hub). Ryzyko uszkodzenia sprzęgła lub koła dwumasowego.
* **Mapa do korekty:** Torque Limiter (LC) (`0x4d2fe`)
* **Rekomendacja:** Sprawdź wytrzymałość sprzęgła i DMF. Rozważ wzmocnione sprzęgło.

#### 🟢 4. [INFO] EGR_OFF
* **Zakres RPM:** Cała mapa
* **Opis:** EGR wyłączony (stała wartość: 85.0)
* **Mapa do korekty:** EGR 01 (`0x55290`)
* **Rekomendacja:** Brak działania. EGR OFF jest standardem w Stage 1.
