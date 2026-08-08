import customtkinter as ctk
import tkinter.filedialog as filedialog
import os
import threading
import tkinter.messagebox as messagebox
from edc15_analyzer import ECUBinaryReader, VCDSLogParser, EDC15Analyzer, plot_advanced_diagnostics, MAP_DEFINITIONS, MAP_AXES

# Konfiguracja wyglądu CustomTkinter
ctk.set_appearance_mode("Dark")  # Tryb ciemny
ctk.set_default_color_theme("blue")  # Akcent kolorystyczny

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("EDC15VM+ Desktop Tuning & Diagnostics")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # Zmienne ścieżek i narzędzi
        self.bin_path = ""
        self.csv_paths = []
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(base_dir, "Raporty_EDC15")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.ecu = None
        self.vcds = None
        self.analyzer = None

        # Główny layout (zamiast panelu z boku, dajmy widok z zakładkami na całość)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.tab_dashboard = self.tabview.add("1. Projekt i Pliki")
        self.tab_analysis = self.tabview.add("2. Diagnostyka (Audyt & Logi)")
        self.tab_tuner = self.tabview.add("3. Edytor Map (Tuning)")
        
        self.setup_dashboard_tab()
        self.setup_analysis_tab()
        self.setup_tuner_tab()

    # ---------------------------------------------------------
    # TAB 1: DASHBOARD
    # ---------------------------------------------------------
    def setup_dashboard_tab(self):
        self.tab_dashboard.grid_columnconfigure((0, 1), weight=1)
        
        title = ctk.CTkLabel(self.tab_dashboard, text="EDC15VM+ Master Tuner", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Ramka BIN
        frame_bin = ctk.CTkFrame(self.tab_dashboard)
        frame_bin.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(frame_bin, text="Wsad sterownika (BIN)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.lbl_bin = ctk.CTkLabel(frame_bin, text="Brak wybranego pliku", text_color="gray")
        self.lbl_bin.pack(pady=10)
        ctk.CTkButton(frame_bin, text="Wczytaj wsad (BIN)", command=self.load_bin_file).pack(pady=10)
        
        # Ramka CSV
        frame_csv = ctk.CTkFrame(self.tab_dashboard)
        frame_csv.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(frame_csv, text="Logi z jazdy (CSV z VCDS)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.lbl_csv = ctk.CTkLabel(frame_csv, text="Brak wybranych logów", text_color="gray")
        self.lbl_csv.pack(pady=10)
        ctk.CTkButton(frame_csv, text="Wczytaj logi (CSV)", command=self.load_csv_files).pack(pady=10)
        
        # Przycisk analizy na środku
        self.btn_analyze = ctk.CTkButton(self.tab_dashboard, text="Rozpocznij analizę ECU i Logów", 
                                         font=ctk.CTkFont(size=16, weight="bold"), height=50,
                                         command=self.run_analysis, fg_color="#C0392B", hover_color="#922B21")
        self.btn_analyze.grid(row=2, column=0, columnspan=2, pady=40, padx=50, sticky="ew")

        # Ramka ze stanem sprzętu
        self.hardware_info = ctk.CTkLabel(self.tab_dashboard, text="Status: Czekam na pliki...", text_color="gray")
        self.hardware_info.grid(row=3, column=0, columnspan=2)

    def load_bin_file(self):
        file = filedialog.askopenfilename(title="Wybierz wsad EDC15", filetypes=[("Wszystkie pliki", "*.*"), ("Pliki BIN", "*.bin")])
        if file:
            self.bin_path = file
            self.lbl_bin.configure(text=os.path.basename(file), text_color="#2ECC71")
            
            # Wczytywanie w tle zeby pokazac co to
            try:
                self.ecu = ECUBinaryReader(self.bin_path)
                sw = self.ecu.header_info.get("software", "Nieznany")
                hw_vag = self.ecu.header_info.get("vag_hw", "Nieznany VAG")
                hw_bosch = self.ecu.header_info.get("bosch_hw", "Nieznany Bosch")
                self.hardware_info.configure(text=f"VAG: {hw_vag} | Bosch: {hw_bosch} | SW: {sw}", text_color="white")
                # Od razu ładujemy edytor map
                self.populate_map_selector()
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się wczytać wsadu: {e}")

    def load_csv_files(self):
        files = filedialog.askopenfilenames(title="Wybierz logi VCDS (CSV)", filetypes=[("Pliki CSV", "*.csv"), ("Pliki TXT", "*.txt")])
        if files:
            self.csv_paths = list(files)
            self.lbl_csv.configure(text=f"Wczytano {len(self.csv_paths)} plik(ów) z logami", text_color="#2ECC71")

        # Dodatkowa ramka uruchamiania Web GUI
        frame_web = ctk.CTkFrame(self.tab_dashboard)
        frame_web.grid(row=4, column=0, columnspan=2, pady=15, padx=20, sticky="ew")
        ctk.CTkLabel(frame_web, text="Supermodern Web Application Interface (HTML5 / CSS3)", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=15, pady=10)
        ctk.CTkButton(frame_web, text="🌐 Otwórz Interfejs Webowy w Przeglądarce", fg_color="#8E44AD", hover_color="#71368A", command=self.launch_web_gui).pack(side="right", padx=15, pady=10)

    def launch_web_gui(self):
        import subprocess
        try:
            subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "edc15_web_gui.py")])
            messagebox.showinfo("Serwer Web", "Uruchomiono nowoczesny interfejs webowy! Sprawdź przeglądarkę pod adresem http://localhost:8080")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się uruchomić serwera web: {e}")

    # ---------------------------------------------------------
    # TAB 2: DIAGNOSTYKA
    # ---------------------------------------------------------
    def setup_analysis_tab(self):
        self.tab_analysis.grid_rowconfigure(1, weight=1)
        self.tab_analysis.grid_columnconfigure(0, weight=1)
        
        top_ctrl = ctk.CTkFrame(self.tab_analysis)
        top_ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.lbl_analysis_status = ctk.CTkLabel(top_ctrl, text="Brak danych do analizy. Uruchom analizę z panelu głównego.", font=ctk.CTkFont(size=14))
        self.lbl_analysis_status.pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(top_ctrl, text="Pokaż wykresy (otwórz folder)", command=self.open_output_dir).pack(side="right", padx=10, pady=10)

        # Kontener na przewijane kafelki "odkryć"
        self.findings_frame = ctk.CTkScrollableFrame(self.tab_analysis)
        self.findings_frame.grid(row=1, column=0, sticky="nsew")

    def open_output_dir(self):
        if os.path.exists(self.output_dir):
            os.startfile(self.output_dir)
        else:
            messagebox.showinfo("Folder", "Folder jeszcze nie istnieje lub brak wykresów.")

    def run_analysis(self):
        if not self.ecu:
            messagebox.showerror("Błąd", "Najpierw musisz wczytać plik BIN!")
            return

        self.btn_analyze.configure(state="disabled", text="Trwa analiza...")
        self.lbl_analysis_status.configure(text="Trwa analiza danych...")
        self.tabview.set("2. Diagnostyka (Audyt & Logi)")
        
        threading.Thread(target=self._analysis_thread).start()

    def _analysis_thread(self):
        try:
            for widget in self.findings_frame.winfo_children():
                widget.destroy()

            if self.csv_paths:
                self.vcds = VCDSLogParser(self.csv_paths)
            else:
                self.vcds = None
                
            self.analyzer = EDC15Analyzer(self.ecu, self.vcds)
            self.analyzer.audit_maps(codeblock=5)
            
            if self.vcds and self.vcds.data_points:
                self.analyzer.execute_all_analysis()
                plot_advanced_diagnostics(self.vcds, self.output_dir)

            self.after(0, self._render_analysis_results)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Błąd Analizy", str(e)))
        finally:
            self.after(0, lambda: self.btn_analyze.configure(state="normal", text="Rozpocznij analizę ECU i Logów"))

    def _render_analysis_results(self):
        self.lbl_analysis_status.configure(text=f"Analiza zakończona. Znaleziono odkryć: {len(self.analyzer.findings) if self.analyzer else 0}")
        if not self.analyzer or not self.analyzer.findings:
            l = ctk.CTkLabel(self.findings_frame, text="Wszystkie parametry w normie. Brak ostrzeżeń dla tego wsadu i logów.", font=ctk.CTkFont(size=14))
            l.pack(pady=20)
            return

        for f in self.analyzer.findings:
            color_map = {"CRITICAL": "#E74C3C", "WARNING": "#F39C12", "INFO": "#3498DB"}
            border_color = color_map.get(f.severity, "#555555")
            
            card = ctk.CTkFrame(self.findings_frame, border_width=2, border_color=border_color, corner_radius=10)
            card.pack(fill="x", padx=10, pady=10)
            
            header = ctk.CTkFrame(card, fg_color=border_color, corner_radius=0)
            header.pack(fill="x")
            
            ctk.CTkLabel(header, text=f"[{f.severity}] {f.category} (Zakres: {f.rpm_range})", font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left", padx=10, pady=5)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(content, text=f"Opis: {f.description}", justify="left", wraplength=900).pack(anchor="w")
            ctk.CTkLabel(content, text=f"Zalecenie: {f.recommendation}", justify="left", wraplength=900, text_color="#AAB7B8").pack(anchor="w", pady=(5, 0))
            if f.map_to_adjust and f.map_to_adjust != "Brak":
                ctk.CTkLabel(content, text=f"Sugerowana mapa: {f.map_to_adjust}", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 0))

    # ---------------------------------------------------------
    # TAB 3: TUNER (Edytor Map z Wartościami Logów & Auto-Tune)
    # ---------------------------------------------------------
    def setup_tuner_tab(self):
        self.tab_tuner.grid_rowconfigure(1, weight=1)
        self.tab_tuner.grid_columnconfigure(0, weight=1)
        
        self.current_map_def = None
        self.current_map_key = None
        self.entries = []

        top_ctrl = ctk.CTkFrame(self.tab_tuner)
        top_ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.map_var = ctk.StringVar(value="Wybierz mapę po wczytaniu BIN...")
        self.map_menu = ctk.CTkOptionMenu(top_ctrl, values=["Brak pliku BIN"], command=self.load_map_into_editor, variable=self.map_var)
        self.map_menu.pack(side="left", padx=10, pady=10)

        self.btn_autotune = ctk.CTkButton(top_ctrl, text="🚀 Uruchom Auto-Tune z Logów", fg_color="#8E44AD", hover_color="#71368A", command=self.run_autotune)
        self.btn_autotune.pack(side="left", padx=10, pady=10)

        self.btn_save_map = ctk.CTkButton(top_ctrl, text="Zastosuj zmiany do pamięci", command=self.apply_map_changes)
        self.btn_save_map.pack(side="left", padx=10, pady=10)

        self.btn_save_bin = ctk.CTkButton(top_ctrl, text="Zapisz do pliku BIN (Eksport)", command=self.save_bin_file, fg_color="#C0392B", hover_color="#922B21")
        self.btn_save_bin.pack(side="right", padx=10, pady=10)

        self.editor_grid = ctk.CTkScrollableFrame(self.tab_tuner)
        self.editor_grid.grid(row=1, column=0, sticky="nsew")

    def populate_map_selector(self):
        map_names = [md.name for md in MAP_DEFINITIONS.values()]
        self.map_menu.configure(values=map_names)
        self.map_var.set("Wybierz mapę...")

    def load_map_into_editor(self, map_name):
        if not self.ecu: return
        
        for k, md in MAP_DEFINITIONS.items():
            if md.name == map_name:
                self.current_map_def = md
                self.current_map_key = k
                break
        
        if not self.current_map_def: return
        
        for widget in self.editor_grid.winfo_children():
            widget.destroy()
            
        self.entries = []
        matrix = self.ecu.read_map(self.current_map_def, codeblock=5)
        
        # Pobieramy logi VCDS nakładane na macierz
        log_matrix, diff_matrix = ([], [])
        if self.analyzer and self.vcds:
            log_matrix, diff_matrix = self.analyzer.get_map_log_matrix(self.current_map_key, codeblock=5)

        axes = MAP_AXES.get(self.current_map_key, {})
        x_axis = axes.get("x", [])
        y_axis = axes.get("y", [])

        # Nagłówek osi X (RPM)
        if x_axis:
            lbl_corner = ctk.CTkLabel(self.editor_grid, text=f"{axes.get('y_unit','Y')} \\ {axes.get('x_unit','X')}", font=ctk.CTkFont(size=11, weight="bold"))
            lbl_corner.grid(row=0, column=0, padx=4, pady=4)
            for c in range(min(self.current_map_def.cols, len(x_axis))):
                lbl_x = ctk.CTkLabel(self.editor_grid, text=str(x_axis[c]), font=ctk.CTkFont(size=11, weight="bold"), text_color="#3498DB")
                lbl_x.grid(row=0, column=c+1, padx=2, pady=2)

        for r in range(self.current_map_def.rows):
            row_entries = []
            # Nagłówek osi Y (Load/IQ/MAF)
            if y_axis and r < len(y_axis):
                lbl_y = ctk.CTkLabel(self.editor_grid, text=str(y_axis[r]), font=ctk.CTkFont(size=11, weight="bold"), text_color="#E67E22")
                lbl_y.grid(row=r+1, column=0, padx=4, pady=4)

            for c in range(self.current_map_def.cols):
                val = matrix[r][c]
                cell_frame = ctk.CTkFrame(self.editor_grid, border_width=1, border_color="#444444")
                cell_frame.grid(row=r+1, column=c+1, padx=2, pady=2)

                entry = ctk.CTkEntry(cell_frame, width=70, justify="center", font=ctk.CTkFont(size=12, weight="bold"))
                entry.insert(0, str(val))
                entry.pack(padx=2, pady=(2, 0))

                # Wyświetlanie nakładki logów VCDS obok/poniżej wartości w mapie
                if log_matrix and r < len(log_matrix) and c < len(log_matrix[r]) and log_matrix[r][c] is not None:
                    log_val = log_matrix[r][c]
                    diff = diff_matrix[r][c]
                    diff_str = f"+{diff}" if diff > 0 else f"{diff}"
                    color = "#F1C40F" if abs(diff) > 20 else "#2ECC71"
                    
                    lbl_log = ctk.CTkLabel(cell_frame, text=f"Log: {log_val}\n({diff_str})", font=ctk.CTkFont(size=9), text_color=color)
                    lbl_log.pack(padx=2, pady=(0, 2))

                row_entries.append(entry)
            self.entries.append(row_entries)

    def run_autotune(self):
        if not self.ecu or not self.vcds or not self.analyzer:
            messagebox.showerror("Błąd Auto-Tune", "Wymagane jest wczytanie pliku BIN oraz przynajmniej jednego pliku z logami VCDS!")
            return

        res = self.analyzer.run_autotune_all(codeblock=5)
        if res["total_changes"] == 0:
            messagebox.showinfo("Auto-Tune", "Brak wymaganych korekt w mapach na podstawie wczytanych logów.")
            return

        # Aplikujemy automatycznie zmodyfikowane mapy
        for m_key, new_mat in res["modified_maps"].items():
            m_def = MAP_DEFINITIONS.get(m_key)
            if m_def:
                self.ecu.write_map(m_def, new_mat, codeblock=5)
                self.ecu.write_map(m_def, new_mat, codeblock=2)

        summary_text = f"Dokonano {res['total_changes']} automatycznych korekt w mapach: {', '.join(res['modified_maps'].keys())}\n\nSzczegóły:\n"
        summary_text += "\n".join(res["changes_log"][:15])
        if len(res["changes_log"]) > 15:
            summary_text += f"\n...oraz {len(res['changes_log']) - 15} innych korekt."

        messagebox.showinfo("Auto-Tune Sukces!", summary_text)

        # Odświeżamy widok obecnej mapy
        if self.current_map_def:
            self.load_map_into_editor(self.current_map_def.name)

    def apply_map_changes(self):
        if not self.ecu or not self.current_map_def or not self.entries: 
            messagebox.showwarning("Uwaga", "Wybierz mapę i dokonaj edycji.")
            return
            
        try:
            new_matrix = []
            for r in range(self.current_map_def.rows):
                row_vals = []
                for c in range(self.current_map_def.cols):
                    val = float(self.entries[r][c].get())
                    row_vals.append(val)
                new_matrix.append(row_vals)
            
            self.ecu.write_map(self.current_map_def, new_matrix, codeblock=5)
            self.ecu.write_map(self.current_map_def, new_matrix, codeblock=2)
            
            messagebox.showinfo("Sukces", "Zastosowano zmiany w mapie w jednostkach fizycznych (CB2 i CB5).")
        except ValueError:
            messagebox.showerror("Błąd", "Wprowadzono niepoprawne wartości (dozwolone tylko liczby).")

    def save_bin_file(self):
        if not self.ecu:
            messagebox.showerror("Błąd", "Brak wczytanego wsadu.")
            return
            
        file = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("BIN files", "*.bin")], title="Zapisz zmodyfikowany BIN")
        if file:
            self.ecu.save_bin(file)
            messagebox.showwarning("Zapisano BIN", f"Zapisano pomyślnie do:\n{file}\n\nUWAGA: Musisz przeliczyć sumę kontrolną (np. w WinOLS) przed wgraniem!")

if __name__ == "__main__":
    import sys
    app = App()
    app.mainloop()

