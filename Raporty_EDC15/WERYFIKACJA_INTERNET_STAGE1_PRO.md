# WERYFIKACJA RAPORTU Z DANYMI Z INTERNETU
## `cks ok_stage1_pro.bin` — VW T4 2.5 TDI AXG / EDC15VM+

**Data weryfikacji:** 02.08.2026  
**Źródła:** ecuedit.com, ross-tech.com, nefariousmotorsports.com, Dimsport Race Guide, fora VW TDI, specyfikacje Garrett

---

## 1. BOOST TARGET (2250 mBar) — CZY BEZPIECZNY?

| Parametr | Nasz raport | Dane z internetu | Weryfikacja |
|:---------|:-----------|:-----------------|:-----------:|
| Boost Target max w mapie | **2250 mBar** abs. | **2200–2350 mBar** bezpieczne dla AXG z seryjnym VNT | ✅ |
| Boost Limiter | **2350 mBar** | Dimsport: +200–220 mBar nad BS → ~2420–2470 mBar | ⚠️ |
| Realny boost w logu | **max 2203 mBar** | Typowe 2100–2200 mBar w Stage 1 | ✅ |
| Doładowanie względne | **~1.25 bar** (2250-1000) | 1.25–1.35 bar typowe Stage 1 | ✅ |

> [!IMPORTANT]
> ### KOREKTA RAPORTU: Boost Target 2250 mBar jest OK!
> Nasz pierwotny raport oznaczyło to jako 🔴 CRITICAL, ale **dane z internetu potwierdzają, że 2250 mBar absolutne (~1.25 bar doładowania) to wartość bezpieczna** dla seryjnego turbo GT2252V/VNT20 w silniku AXG.
> 
> **Źródła potwierdzające:**
> - Fora tuningowe: „2250–2350 mBar absolutne to bezpieczny zakres dla AXG"
> - Specyfikacja GT2252V: turbo obsługuje 150–260 KM, więc Stage 1 (180–190 KM) to w zakresie
> - Dimsport Race: zalecane BS +180–200 mBar nad stock → stock AXG ~2050 + 200 = **2250 mBar** ← dokładnie tyle!
> 
> **Wniosek:** Wartość **2250 mBar jest zgodna z zaleceniem Dimsport** i mieści się w bezpiecznym zakresie. Raport zbyt agresywnie oznaczył to jako krytyczne.

---

## 2. TORQUE LIMITER (55.0 mg/hub) — CZY ZA WYSOKI?

| Parametr | Nasz raport | Dane z internetu | Weryfikacja |
|:---------|:-----------|:-----------------|:-----------:|
| Max Torque Limiter w mapie | **55.0 mg/hub** | Stock EDC15VM+ often capped ~50 mg, Stage 1: 55–58 mg safe | ✅ |
| Dimsport zalecenie | — | LC: **+20%** nad stock | ✅ |
| Stock AXG torque limiter | ~40–42 mg (szacunek) | +20% = ~48–50 mg | ⚠️ |
| Realny limit w logu | **50.0–50.8 mg** | IQ to minimum z DRV/TRQ/SMK | ✅ |

> [!WARNING]
> ### WERYFIKACJA: Torque Limiter 55 mg to górna granica Stage 1
> Dimsport Race zaleca +20% nad stock w mapie LC. Dla AXG stock ~42 mg → +20% = ~50 mg.
> 
> **55 mg przekracza zalecenie Dimsport o ~5 mg**, ale:
> - W logu realny limit to 50.0–50.8 mg (obcina Torque Limiter)
> - Seryjne wtryskiwacze VP37 mogą dawać 60–80 mg (wg ecuedit.com)
> - **Przy zachowaniu łagodnego narastania momentu poniżej 2000 RPM, 55 mg jest do przyjęcia**
> - Ryzyko dla DMF istnieje, ale głównie przy gwałtownych szarpnięciach na niskich obrotach
> 
> **Wniosek:** ⚠️ Wartość jest agresywna, ale akceptowalna. **Raport prawidłowo ostrzegł** o ryzyku.

---

## 3. SOI (Kąt Wtrysku) — CZY NORMALNY?

| Parametr | Nasz raport | Dane z internetu | Weryfikacja |
|:---------|:-----------|:-----------------|:-----------:|
| SOI na biegu jałowym | nie logowane | 2° ATDC – 3° BTDC norma | — |
| SOI pod obciążeniem (WOT) | **7.9° – 18.0° BTDC** | 10° – 16° BTDC typowe WOT | ✅ |
| Odchyłka SOI req vs act | **max ±0.7°** | <1.5° = norma VP37 | ✅ |
| Dimsport zalecenie IS | — | **NIE MODYFIKOWAĆ** | ✅ |

> [!NOTE]
> ### POTWIERDZONE: SOI jest idealny
> Dane z internetu potwierdzają:
> - Zakres 8°–18° BTDC pod obciążeniem jest **dokładnie w normie** dla VP37
> - Odchyłki <1° oznaczają, że pompa jest zdrowa i sprawna
> - Dimsport Race mówi **"IS — NIE MODYFIKOWAĆ"** — i w tym pliku SOI nie był modyfikowany
> 
> **Wniosek:** ✅ Pełna zgodność z danymi referencyjnymi.

---

## 4. PUMP VOLTAGE VP37 (max 4.38V) — CZY BEZPIECZNY?

| Parametr | Nasz raport | Dane z internetu | Weryfikacja |
|:---------|:-----------|:-----------------|:-----------:|
| Max pump voltage w mapie | **4.38 V** | Zakres operacyjny 0.5–4.74V | ✅ |
| Limit fizyczny nastawnika | **4.5V** (nasz raport) | Feedback sensor do ~4.7V, mechanical stop ~5.2V | ⚠️ KOREKTA |
| Napięcie z logu (Gr.019) | **0.760V / 4.540V** | Dwie wartości = pozycja tłoka regulacyjnego | ✅ |

> [!IMPORTANT]
> ### KOREKTA: Limit VP37 to ~4.7V, nie 4.5V
> Nasz raport podawał limit fizyczny jako 4.5V. **Dane z internetu (ecuedit.com, Scribd dokumentacja Bosch) wskazują:**
> - Zakres diagnostyczny nastawnika: **0.5V – 4.74V**
> - Mechaniczny stop: **~5.2V** na niektórych wersjach
> - Powyżej 4.7V–4.8V ECU generuje fault code
> 
> **4.38V w mapie to ~93% zakresu** — bezpieczna wartość z zapasem.
> 
> **Wniosek:** ✅ Bezpieczny, ale nasz raport zaniżył limit o ~0.2V.

---

## 5. N75 DUTY CYCLE — CZY WARTOŚCI LOGÓW SĄ NORMALNE?

| Parametr | Nasz raport (log) | Dane z internetu | Weryfikacja |
|:---------|:-----------|:-----------------|:-----------:|
| N75 przy niskich RPM | **31.9%** (1448–1571 RPM) | 20–30% typowe niske RPM | ✅ ~OK |
| N75 w zakresie średnim | **45–58%** (2040–3774 RPM) | Rośnie z RPM, 40–70% normalne | ✅ |
| N75 max WOT | **59.8%** (4345 RPM) | Do 60–80% normalne pod obciążeniem | ✅ |
| N75 >90% sustained | **NIE** | Jeśli >90% = turbo nie nadąża, problem mech. | ✅ Zdrowe |

> [!NOTE]
> ### POTWIERDZONE: N75 w normie
> Dane z ecuedit.com i ross-tech.com potwierdzają:
> - N75 rosnący od ~32% do 60% z RPM to **zdrowy profil**
> - Brak wartości >90% oznacza, że **turbo nie walczy** o osiągnięcie ciśnienia
> - Turbina VNT pracuje w swoim zakresie efektywności
> 
> **Wyjątek:** przy 2040 RPM mamy turbo lag (Δ=-194 mBar) mimo N75=45% — to normalne opóźnienie przy nagłym przyspieszeniu z niskich obrotów, a nie problem z turbiną.

---

## 6. MAF / PRZEPŁYWOMIERZ — CZY 980 mg/hub TO NORMA?

| Parametr | Nasz raport | Dane z internetu | Weryfikacja |
|:---------|:-----------|:-----------------|:-----------:|
| MAF req WOT | **980 mg/hub** stałe | To wartość z Smoke Limiter map | ✅ |
| MAF act przy >3000 RPM | **940–980 mg/hub** | 95–100% odczytu = zdrowy MAF | ✅ |
| MAF act przy 1469 RPM | **530 mg/hub** (54%) | Normalne — turbo jeszcze się rozpędza | ✅ |

> [!NOTE]
> ### POTWIERDZONE: MAF G70 sprawny
> Przepływomierz odczytuje >91% od 1836 RPM wzwyż — to potwierdza, że:
> - Czujnik G70 nie jest brudny/uszkodzony
> - Dolot jest szczelny
> - Niski odczyt na dole (530 mg przy 1469 RPM) to **fizyczne opóźnienie turbiny**, nie usterka MAF

---

## 7. LIMITERY DAWKI (Grupa 008) — CZY WZORZEC JEST PRAWIDŁOWY?

| Parametr | Nasz raport | Dane z internetu | Weryfikacja |
|:---------|:-----------|:-----------------|:-----------:|
| Smoke limiter blokuje na dole | **TAK** (1489–1510 RPM) | Normalne — mało powietrza na dole = mało paliwa | ✅ |
| Torque limiter dominuje od 1652+ | **TAK** | Prawidłowe — LC limituje dawkę na WOT | ✅ |
| Driver Wish = 51 mg WOT | Tak | Zgodne z +250 jednostek Dimsport nad stock | ✅ |
| IQ finale = minimum z 3 limiterów | **TAK** | Potwierdzone Ross-Tech VCDS docs | ✅ |

> [!NOTE]
> ### POTWIERDZONE: Wzorzec limiterów jest poprawny
> Fakt, że Torque Limiter dominuje (a nie Smoke Limiter) od 1652+ RPM to **dobry znak**:
> - Oznacza, że przepływomierz dostarcza wystarczająco sygnału powietrza
> - Smoke Limiter nie blokuje dawki = turbo daje dość powietrza
> - Driver Wish jest nad LC → kierowca "prosi o więcej" niż LC pozwala → pełna kontrola

---

## 8. PORÓWNANIE Z PRZEWODNIKIEM DIMSPORT RACE

| Mapa | Dimsport zalecenie | Stan w pliku `stage1_pro` | Zgodność |
|:-----|:-------------------|:--------------------------|:--------:|
| **B1** (Driver Wish) | +250 jedn. od 60% load, 1500+ RPM | Max 55.0 mg = ~5500 raw (factor 0.01) | ✅ |
| **BS** (Boost Target) | +180–200 mBar od 50% load, 1600+ RPM | Max 2250 mBar (stock ~2050 + 200) | ✅ DOKŁADNIE |
| **BL** (Boost Limiter) | +200–220 nad BS | 2350 mBar (BS+100 mBar) | ⚠️ Niżej niż Dimsport* |
| **QS** (Smoke Limiter) | +12% od 50% load, 1500–1800 RPM | Max 57.9–58.0 mg (podniesiony) | ✅ |
| **LC** (Torque Limiter) | +20% od 1300–1500 RPM | Max 55.0 mg (stock ~42 → +31%) | ⚠️ Więcej niż +20% |
| **IS** (SOI) | NIE MODYFIKOWAĆ | Brak zmian | ✅ |
| **EG** (EGR) | NIE MODYFIKOWAĆ (Dimsport) | Wyłączone (flat 85%) | ❌ Niezgodne* |
| **IF** (Injection Factor) | NIE MODYFIKOWAĆ | Bez zmian | ✅ |

> [!WARNING]
> **\* Uwagi do niezgodności z Dimsport:**
> - **BL +100 vs +200–220:** Boost Limiter w pliku jest niższy niż zaleca Dimsport. To bezpieczniejsza opcja (mniej ryzyka boost spike), ale przy 2350 mBar margines nad BS (2250) wynosi jedynie 100 mBar — Dimsport zaleca 200+.
> - **EGR OFF:** Dimsport oficjalnie mówi "nie modyfikować EGR" na Stage 1, ale **w praktyce wyłączenie EGR jest standardową procedurą** w tuningu EDC15VM+ (potwierdzone na ecuedit.com i forach TDI). To nie jest błąd, a standardowa praktyka.
> - **LC +31%:** Dimsport mówi +20%, ale plik ma ~+31%. Agresywne, ale w logach LC obcina do 50 mg — czyli ~+20% jest realizowane w praktyce.

---

## 9. PORÓWNANIE Z TYPOWYMI WYNIKAMI STAGE 1 NA HAMOWNI

| Parametr | Typowy Stage 1 AXG | Z logów tego samochodu | Weryfikacja |
|:---------|:-------------------|:----------------------|:-----------:|
| Moc | 170–190 KM | Brak danych dyno (szacunek: ~175–185 KM) | — |
| Moment | 330–375 Nm | IQ max ~50 mg × 5 cyl → ~350 Nm szacunek | ✅ Zakres |
| Boost max | 2100–2250 mBar abs. | **2203 mBar** (log) | ✅ |
| IQ WOT midrange | 50–55 mg/hub | **50.0–50.8 mg** (limitowane przez LC) | ✅ |
| N75 max | 55–70% | **59.8%** | ✅ |
| SOI WOT | 8–18° BTDC | **7.9–18.0° BTDC** | ✅ |

---

## 10. TABELA KOŃCOWA: WERYFIKACJA KAŻDEGO WNIOSKU Z RAPORTU

| # | Wniosek z raportu | Weryfikacja internetowa | Wynik |
|:-:|:-------------------|:-----------------------|:-----:|
| 1 | Boost Target 2250 mBar = ZA WYSOKI | **BŁĄD** — 2250 mBar to wartość zgodna z Dimsport +200 | ❌→✅ |
| 2 | Torque Limiter 55 mg = WYSOKI | **POTWIERDZONY** — przekracza Dimsport +20%, ale w logach limituje do ~50 mg | ⚠️✅ |
| 3 | EGR OFF = OK | **POTWIERDZONY** — standardowa praktyka, choć Dimsport nie zaleca | ✅ |
| 4 | SOI idealny | **POTWIERDZONY** — zakres 8–18° BTDC, odchyłki <1° = norma VP37 | ✅✅ |
| 5 | Pump Voltage 4.38V < limit 4.5V | **KOREKTA** — limit to ~4.7V, nie 4.5V. 4.38V wciąż bezpieczne | ⚠️→✅ |
| 6 | MAF sprawny | **POTWIERDZONY** — >91% odczytu od 1836 RPM | ✅✅ |
| 7 | Turbo Lag przy 2040 RPM | **POTWIERDZONY** — normalne opóźnienie VNT przy nagłym WOT z dołu | ✅ |
| 8 | N75 wymaga korekty 2000–2300 RPM | **WĄTPLIWY** — lag jest fizycznym opóźnieniem turbo, nie błędem mapy | ⚠️ |
| 9 | Boost Limiter 2350 mBar OK | **UWAGA** — Dimsport zaleca BS+200–220 = powinno być ~2450 mBar | ⚠️ |
| 10 | Temperatura 91.8–94.5°C | **OK** — standardowa temp. robocza TDI | ✅ |

---

## 11. POPRAWIONE ZALECENIA (PO WERYFIKACJI)

> [!IMPORTANT]
> ### Zmienione zalecenia na podstawie weryfikacji:
> 
> 1. ~~Obniż Boost Target z 2250 do 2100 mBar~~ → **ANULOWANE.** 2250 mBar jest zgodne z Dimsport Race (+200 mBar). Nie obniżać.
> 
> 2. **Rozważ podniesienie Boost Limiter** z 2350 do **2450 mBar** — zgodnie z Dimsport (+200–220 nad BS). Margines 100 mBar może być zbyt ciasny i powodować Notlauf przy szybkich spike'ach.
> 
> 3. **Torque Limiter 55 mg — do obserwacji.** W logach limituje na 50 mg, więc de facto działa w zakresie Dimsport +20%. Ale jeśli DMF wykazuje objawy (wibracje, stuki), obniżyć do 50 mg.
> 
> 4. **N75 przy 2040 RPM — NIE KORYGOWAĆ.** Lag -194 mBar to normalne fizyczne opóźnienie VNT. Zgodnie z ecuedit.com: "nie modyfikuj N75 map na seryjnym turbo — reguluj Boost Target/Limiter."
> 
> 5. **Pump Voltage — OK.** 4.38V jest w bezpiecznym zakresie (limit ~4.7V wg dokumentacji Bosch).

---

**Źródła weryfikacji:**
- ecuedit.com — EDC15 tuning forums (VP37, N75, SOI, Torque Limiter)
- ross-tech.com — VCDS Group 008, Group 011 documentation
- nefariousmotorsports.com — N75 precontrol explanation
- Garrett specifications — GT2252V compressor/turbine specs
- Dimsport Race Guide (Bosch_EDC15VM_VAG_PL.txt) — map modification limits
- v-tuning.pl, celtictuning.co.uk, revchiptuning.com — Stage 1 AXG dyno results
- audiworld.com, vwdiesel.net — VNT boost pressure discussions

---

*Raport weryfikacyjny wygenerowany 02.08.2026 przez EDC15VM+ Analyzer z cross-referencją do danych internetowych.*
