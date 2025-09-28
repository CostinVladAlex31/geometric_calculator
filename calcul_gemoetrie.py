import tkinter as tk
from tkinter import ttk, messagebox
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import sqlite3
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import threading
import time

class DataManager:
    def __init__(self, db_path="geometry_analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shape_type TEXT NOT NULL,
                shape_dimension TEXT NOT NULL,
                parameters TEXT NOT NULL,
                result_area REAL,
                result_perimeter REAL,
                result_volume REAL,
                calculation_time_ms REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                total_calculations INTEGER DEFAULT 0,
                favorite_shape TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_calculation(self, shape_type, shape_dimension, parameters, 
                       result_area=None, result_perimeter=None, result_volume=None,
                       calculation_time_ms=None, session_id="default"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO calculations 
            (shape_type, shape_dimension, parameters, result_area, result_perimeter, 
             result_volume, calculation_time_ms, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (shape_type, shape_dimension, json.dumps(parameters), 
              result_area, result_perimeter, result_volume, calculation_time_ms, session_id))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self, days=7):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM calculations 
            WHERE timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp DESC
        '''.format(days))
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            return self._empty_stats()
        
        stats = {
            'total_calculations': len(data),
            'shapes_frequency': defaultdict(int),
            'dimensions_frequency': defaultdict(int),
            'calculations_by_hour': defaultdict(int),
            'calculations_by_day': defaultdict(int),
            'avg_calculation_time': 0,
            'most_popular_shape': '',
            'recent_calculations': data[:10]
        }
        
        total_time = 0
        time_count = 0
        
        for row in data:
            shape_type = row[1]
            shape_dimension = row[2]
            calc_time = row[7]
            timestamp = row[8]
            
            stats['shapes_frequency'][shape_type] += 1
            stats['dimensions_frequency'][shape_dimension] += 1
            
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour = dt.hour
                day = dt.strftime('%Y-%m-%d')
                stats['calculations_by_hour'][hour] += 1
                stats['calculations_by_day'][day] += 1
            except:
                pass
            
            if calc_time:
                total_time += calc_time
                time_count += 1
        
        if time_count > 0:
            stats['avg_calculation_time'] = total_time / time_count
        
        if stats['shapes_frequency']:
            stats['most_popular_shape'] = max(stats['shapes_frequency'], 
                                            key=stats['shapes_frequency'].get)
        
        return stats
    
    def _empty_stats(self):
        return {
            'total_calculations': 0,
            'shapes_frequency': {},
            'dimensions_frequency': {},
            'calculations_by_hour': {},
            'calculations_by_day': {},
            'avg_calculation_time': 0,
            'most_popular_shape': 'N/A',
            'recent_calculations': []
        }

class CalculatorGeometrie:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator Geometrie - AI Analytics Platform")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        self.data_manager = DataManager()
        self.session_id = f"session_{int(time.time())}"
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tab_2d = ttk.Frame(self.notebook)
        self.tab_3d = ttk.Frame(self.notebook)
        self.tab_dashboard = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_2d, text="Forme 2D")
        self.notebook.add(self.tab_3d, text="Forme 3D")
        self.notebook.add(self.tab_dashboard, text="Analytics Dashboard")
        
        self.setup_2d_interface()
        self.setup_3d_interface()
        self.setup_dashboard_interface()
        
        self.setup_auto_refresh()
        
    def setup_auto_refresh(self):
        def refresh_dashboard():
            if self.notebook.index(self.notebook.select()) == 2:
                self.update_dashboard()
            self.root.after(5000, refresh_dashboard)
        
        self.root.after(1000, refresh_dashboard)
    
    def setup_dashboard_interface(self):
        main_frame = ttk.Frame(self.tab_dashboard)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        header_frame = ttk.LabelFrame(main_frame, text="Statistici Live", padding=10)
        header_frame.pack(fill='x', pady=(0, 10))
        
        kpi_frame = ttk.Frame(header_frame)
        kpi_frame.pack(fill='x')
        
        self.total_calc_label = ttk.Label(kpi_frame, text="Total Calcule: 0", 
                                         font=('Arial', 12, 'bold'))
        self.total_calc_label.grid(row=0, column=0, padx=20, pady=5)
        
        self.popular_shape_label = ttk.Label(kpi_frame, text="Forma Populara: N/A", 
                                           font=('Arial', 12, 'bold'))
        self.popular_shape_label.grid(row=0, column=1, padx=20, pady=5)
        
        self.avg_time_label = ttk.Label(kpi_frame, text="Timp Mediu: 0ms", 
                                       font=('Arial', 12, 'bold'))
        self.avg_time_label.grid(row=0, column=2, padx=20, pady=5)
        
        ttk.Button(kpi_frame, text="Refresh", 
                  command=self.update_dashboard).grid(row=0, column=3, padx=20, pady=5)
        
        charts_frame = ttk.Frame(main_frame)
        charts_frame.pack(fill='both', expand=True)
        
        left_frame = ttk.LabelFrame(charts_frame, text="Analiza Vizuala", padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        right_frame = ttk.LabelFrame(charts_frame, text="Istoric Recent", padding=10)
        right_frame.pack(side='right', fill='y', padx=(5, 0))
        
        self.charts_canvas_frame = ttk.Frame(left_frame)
        self.charts_canvas_frame.pack(fill='both', expand=True)
        
        self.history_tree = ttk.Treeview(right_frame, columns=('Shape', 'Time', 'Result'), 
                                        show='headings', height=15)
        self.history_tree.heading('Shape', text='Forma')
        self.history_tree.heading('Time', text='Timp')
        self.history_tree.heading('Result', text='Rezultat')
        
        self.history_tree.column('Shape', width=100)
        self.history_tree.column('Time', width=80)
        self.history_tree.column('Result', width=120)
        
        scrollbar = ttk.Scrollbar(right_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.update_dashboard()
    
    def update_dashboard(self):
        stats = self.data_manager.get_statistics()
        
        self.total_calc_label.config(text=f"Total Calcule: {stats['total_calculations']}")
        self.popular_shape_label.config(text=f"Forma Populara: {stats['most_popular_shape']}")
        self.avg_time_label.config(text=f"Timp Mediu: {stats['avg_calculation_time']:.1f}ms")
        
        self.update_charts(stats)
        
        self.update_history(stats['recent_calculations'])
    
    def update_charts(self, stats):
        for widget in self.charts_canvas_frame.winfo_children():
            widget.destroy()
        
        fig = Figure(figsize=(12, 8), dpi=100)
        
        if stats['shapes_frequency']:
            ax1 = fig.add_subplot(221)
            shapes = list(stats['shapes_frequency'].keys())
            counts = list(stats['shapes_frequency'].values())
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
            ax1.pie(counts, labels=shapes, autopct='%1.1f%%', colors=colors[:len(shapes)])
            ax1.set_title('Distributia Formelor Geometrice')
        
        if stats['dimensions_frequency']:
            ax2 = fig.add_subplot(222)
            dimensions = list(stats['dimensions_frequency'].keys())
            counts = list(stats['dimensions_frequency'].values())
            bars = ax2.bar(dimensions, counts, color=['#3498db', '#e74c3c'])
            ax2.set_title('Calcule 2D vs 3D')
            ax2.set_ylabel('Numarul de calcule')
            
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom')
        
        if stats['calculations_by_hour']:
            ax3 = fig.add_subplot(223)
            hours = sorted(stats['calculations_by_hour'].keys())
            counts = [stats['calculations_by_hour'][h] for h in hours]
            ax3.plot(hours, counts, marker='o', linewidth=2, markersize=6, color='#2ecc71')
            ax3.set_title('Activitate pe Ore')
            ax3.set_xlabel('Ora zilei')
            ax3.set_ylabel('Numarul de calcule')
            ax3.grid(True, alpha=0.3)
        
        if stats['calculations_by_day']:
            ax4 = fig.add_subplot(224)
            days = sorted(stats['calculations_by_day'].keys())[-7:]
            counts = [stats['calculations_by_day'][d] for d in days]
            day_labels = [d.split('-')[2] + '/' + d.split('-')[1] for d in days]
            bars = ax4.bar(day_labels, counts, color='#9b59b6')
            ax4.set_title('Trend Ultimele 7 Zile')
            ax4.set_xlabel('Data')
            ax4.set_ylabel('Calcule')
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.charts_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def update_history(self, recent_calculations):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        for calc in recent_calculations:
            shape_type = calc[1]
            timestamp = calc[8]
            result_area = calc[4] or 0
            result_volume = calc[6] or 0
            
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M')
            except:
                time_str = 'N/A'
            
            if result_volume > 0:
                result_str = f"V: {result_volume:.2f}"
            else:
                result_str = f"A: {result_area:.2f}"
            
            self.history_tree.insert('', 'end', values=(shape_type, time_str, result_str))

    def setup_2d_interface(self):
        main_frame = ttk.Frame(self.tab_2d)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        selection_frame = ttk.LabelFrame(main_frame, text="Selecteaza Forma", padding=10)
        selection_frame.pack(fill='x', pady=(0, 10))
        
        self.forma_2d = tk.StringVar(value="dreptunghi")
        forms = [("Dreptunghi", "dreptunghi"), ("Patrat", "patrat"), 
                ("Cerc", "cerc"), ("Triunghi", "triunghi")]
        
        for i, (text, value) in enumerate(forms):
            ttk.Radiobutton(selection_frame, text=text, variable=self.forma_2d, 
                           value=value, command=self.update_2d_inputs).grid(row=0, column=i, padx=10)
        
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)
        
        self.inputs_frame_2d = ttk.LabelFrame(content_frame, text="Parametri", padding=10)
        self.inputs_frame_2d.pack(side='left', fill='y', padx=(0, 10))
        
        self.results_frame_2d = ttk.LabelFrame(content_frame, text="Rezultate", padding=10)
        self.results_frame_2d.pack(side='left', fill='y', padx=(0, 10))
        
        self.viz_frame_2d = ttk.LabelFrame(content_frame, text="Vizualizare", padding=10)
        self.viz_frame_2d.pack(side='right', fill='both', expand=True)
        
        self.update_2d_inputs()
        
    def setup_3d_interface(self):
        main_frame = ttk.Frame(self.tab_3d)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        selection_frame = ttk.LabelFrame(main_frame, text="Selecteaza Forma 3D", padding=10)
        selection_frame.pack(fill='x', pady=(0, 10))
        
        self.forma_3d = tk.StringVar(value="cub")
        forms_3d = [("Cub", "cub"), ("Paralelpiped", "paralelpiped"), 
                   ("Sfera", "sfera"), ("Prisma Triunghiulara", "prisma")]
        
        for i, (text, value) in enumerate(forms_3d):
            ttk.Radiobutton(selection_frame, text=text, variable=self.forma_3d, 
                           value=value, command=self.update_3d_inputs).grid(row=0, column=i, padx=10)
        
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)
        
        self.inputs_frame_3d = ttk.LabelFrame(content_frame, text="Parametri", padding=10)
        self.inputs_frame_3d.pack(side='left', fill='y', padx=(0, 10))
        
        self.results_frame_3d = ttk.LabelFrame(content_frame, text="Rezultate", padding=10)
        self.results_frame_3d.pack(side='left', fill='y', padx=(0, 10))
        
        self.viz_frame_3d = ttk.LabelFrame(content_frame, text="Vizualizare 3D", padding=10)
        self.viz_frame_3d.pack(side='right', fill='both', expand=True)
        
        self.update_3d_inputs()
    
    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()
    
    def update_2d_inputs(self):
        self.clear_frame(self.inputs_frame_2d)
        self.clear_frame(self.results_frame_2d)
        self.clear_frame(self.viz_frame_2d)
        
        forma = self.forma_2d.get()
        
        if forma == "dreptunghi":
            ttk.Label(self.inputs_frame_2d, text="Lungime:").pack(pady=2)
            self.lungime_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_2d, textvariable=self.lungime_var).pack(pady=2)
            
            ttk.Label(self.inputs_frame_2d, text="Latime:").pack(pady=2)
            self.latime_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_2d, textvariable=self.latime_var).pack(pady=2)
            
        elif forma == "patrat":
            ttk.Label(self.inputs_frame_2d, text="Latura:").pack(pady=2)
            self.latura_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_2d, textvariable=self.latura_var).pack(pady=2)
            
        elif forma == "cerc":
            ttk.Label(self.inputs_frame_2d, text="Raza:").pack(pady=2)
            self.raza_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_2d, textvariable=self.raza_var).pack(pady=2)
            
        elif forma == "triunghi":
            ttk.Label(self.inputs_frame_2d, text="Latura a:").pack(pady=2)
            self.a_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_2d, textvariable=self.a_var).pack(pady=2)
            
            ttk.Label(self.inputs_frame_2d, text="Latura b:").pack(pady=2)
            self.b_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_2d, textvariable=self.b_var).pack(pady=2)
            
            ttk.Label(self.inputs_frame_2d, text="Latura c:").pack(pady=2)
            self.c_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_2d, textvariable=self.c_var).pack(pady=2)
        
        ttk.Button(self.inputs_frame_2d, text="Calculeaza", 
                  command=self.calculate_2d).pack(pady=10)
    
    def update_3d_inputs(self):
        self.clear_frame(self.inputs_frame_3d)
        self.clear_frame(self.results_frame_3d)
        self.clear_frame(self.viz_frame_3d)
        
        forma = self.forma_3d.get()
        
        if forma == "cub":
            ttk.Label(self.inputs_frame_3d, text="Latura:").pack(pady=2)
            self.latura_3d_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_3d, textvariable=self.latura_3d_var).pack(pady=2)
            
        elif forma == "paralelpiped":
            ttk.Label(self.inputs_frame_3d, text="Lungime:").pack(pady=2)
            self.lungime_3d_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_3d, textvariable=self.lungime_3d_var).pack(pady=2)
            
            ttk.Label(self.inputs_frame_3d, text="Latime:").pack(pady=2)
            self.latime_3d_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_3d, textvariable=self.latime_3d_var).pack(pady=2)
            
            ttk.Label(self.inputs_frame_3d, text="Inaltime:").pack(pady=2)
            self.inaltime_3d_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_3d, textvariable=self.inaltime_3d_var).pack(pady=2)
            
        elif forma == "sfera":
            ttk.Label(self.inputs_frame_3d, text="Raza:").pack(pady=2)
            self.raza_3d_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_3d, textvariable=self.raza_3d_var).pack(pady=2)
            
        elif forma == "prisma":
            ttk.Label(self.inputs_frame_3d, text="Latura a (baza):").pack(pady=2)
            self.a_3d_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_3d, textvariable=self.a_3d_var).pack(pady=2)
            
            ttk.Label(self.inputs_frame_3d, text="Latura b (baza):").pack(pady=2)
            self.b_3d_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_3d, textvariable=self.b_3d_var).pack(pady=2)
            
            ttk.Label(self.inputs_frame_3d, text="Latura c (baza):").pack(pady=2)
            self.c_3d_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_3d, textvariable=self.c_3d_var).pack(pady=2)
            
            ttk.Label(self.inputs_frame_3d, text="Inaltime:").pack(pady=2)
            self.inaltime_prisma_var = tk.StringVar()
            ttk.Entry(self.inputs_frame_3d, textvariable=self.inaltime_prisma_var).pack(pady=2)
        
        ttk.Button(self.inputs_frame_3d, text="Calculeaza", 
                  command=self.calculate_3d).pack(pady=10)
    
    def calculate_2d(self):
        start_time = time.time()
        try:
            forma = self.forma_2d.get()
            self.clear_frame(self.results_frame_2d)
            
            if forma == "dreptunghi":
                lungime = float(self.lungime_var.get())
                latime = float(self.latime_var.get())
                arie = lungime * latime
                perimetru = 2 * (lungime + latime)
                
                calc_time = (time.time() - start_time) * 1000
                self.data_manager.log_calculation(
                    shape_type="dreptunghi",
                    shape_dimension="2D",
                    parameters={"lungime": lungime, "latime": latime},
                    result_area=arie,
                    result_perimeter=perimetru,
                    calculation_time_ms=calc_time,
                    session_id=self.session_id
                )
                
                ttk.Label(self.results_frame_2d, text=f"Arie: {arie:.3f}").pack(pady=2)
                ttk.Label(self.results_frame_2d, text=f"Perimetru: {perimetru:.3f}").pack(pady=2)
                
                self.draw_rectangle_2d(lungime, latime)
                
            elif forma == "patrat":
                latura = float(self.latura_var.get())
                arie = latura * latura
                perimetru = 4 * latura
                
                calc_time = (time.time() - start_time) * 1000
                self.data_manager.log_calculation(
                    shape_type="patrat",
                    shape_dimension="2D",
                    parameters={"latura": latura},
                    result_area=arie,
                    result_perimeter=perimetru,
                    calculation_time_ms=calc_time,
                    session_id=self.session_id
                )
                
                ttk.Label(self.results_frame_2d, text=f"Arie: {arie:.3f}").pack(pady=2)
                ttk.Label(self.results_frame_2d, text=f"Perimetru: {perimetru:.3f}").pack(pady=2)
                
                self.draw_square_2d(latura)
                
            elif forma == "cerc":
                raza = float(self.raza_var.get())
                arie = math.pi * raza * raza
                perimetru = 2 * math.pi * raza
                
                calc_time = (time.time() - start_time) * 1000
                self.data_manager.log_calculation(
                    shape_type="cerc",
                    shape_dimension="2D",
                    parameters={"raza": raza},
                    result_area=arie,
                    result_perimeter=perimetru,
                    calculation_time_ms=calc_time,
                    session_id=self.session_id
                )
                
                ttk.Label(self.results_frame_2d, text=f"Arie: {arie:.3f}").pack(pady=2)
                ttk.Label(self.results_frame_2d, text=f"Perimetru: {perimetru:.3f}").pack(pady=2)
                
                self.draw_circle_2d(raza)
                
            elif forma == "triunghi":
                a = float(self.a_var.get())
                b = float(self.b_var.get())
                c = float(self.c_var.get())
                
                if (a + b > c) and (a + c > b) and (b + c > a):
                    s = (a + b + c) / 2
                    arie = math.sqrt(s * (s - a) * (s - b) * (s - c))
                    perimetru = a + b + c
                    
                    calc_time = (time.time() - start_time) * 1000
                    self.data_manager.log_calculation(
                        shape_type="triunghi",
                        shape_dimension="2D",
                        parameters={"a": a, "b": b, "c": c},
                        result_area=arie,
                        result_perimeter=perimetru,
                        calculation_time_ms=calc_time,
                        session_id=self.session_id
                    )
                    
                    ttk.Label(self.results_frame_2d, text=f"Arie: {arie:.3f}").pack(pady=2)
                    ttk.Label(self.results_frame_2d, text=f"Perimetru: {perimetru:.3f}").pack(pady=2)
                    
                    self.draw_triangle_2d(a, b, c)
                else:
                    messagebox.showerror("Eroare", "Nu se poate forma triunghi cu aceste laturi!")
                    
        except ValueError:
            messagebox.showerror("Eroare", "Introduceti valori numerice valide!")
    
    def calculate_3d(self):
        start_time = time.time()
        try:
            forma = self.forma_3d.get()
            self.clear_frame(self.results_frame_3d)
            
            if forma == "cub":
                latura = float(self.latura_3d_var.get())
                volum = latura ** 3
                arie_totala = 6 * latura ** 2
                
                calc_time = (time.time() - start_time) * 1000
                self.data_manager.log_calculation(
                    shape_type="cub",
                    shape_dimension="3D",
                    parameters={"latura": latura},
                    result_volume=volum,
                    calculation_time_ms=calc_time,
                    session_id=self.session_id
                )
                
                ttk.Label(self.results_frame_3d, text=f"Volum: {volum:.3f}").pack(pady=2)
                ttk.Label(self.results_frame_3d, text=f"Arie totala: {arie_totala:.3f}").pack(pady=2)
                
                self.draw_cube_3d(latura)
                
            elif forma == "paralelpiped":
                lungime = float(self.lungime_3d_var.get())
                latime = float(self.latime_3d_var.get())
                inaltime = float(self.inaltime_3d_var.get())
                
                volum = lungime * latime * inaltime
                arie_totala = 2 * (lungime * latime + lungime * inaltime + latime * inaltime)
                
                calc_time = (time.time() - start_time) * 1000
                self.data_manager.log_calculation(
                    shape_type="paralelpiped",
                    shape_dimension="3D",
                    parameters={"lungime": lungime, "latime": latime, "inaltime": inaltime},
                    result_volume=volum,
                    calculation_time_ms=calc_time,
                    session_id=self.session_id
                )
                
                ttk.Label(self.results_frame_3d, text=f"Volum: {volum:.3f}").pack(pady=2)
                ttk.Label(self.results_frame_3d, text=f"Arie totala: {arie_totala:.3f}").pack(pady=2)
                
                self.draw_parallelepiped_3d(lungime, latime, inaltime)
                
            elif forma == "sfera":
                raza = float(self.raza_3d_var.get())
                volum = (4/3) * math.pi * raza ** 3
                arie = 4 * math.pi * raza ** 2
                
                calc_time = (time.time() - start_time) * 1000
                self.data_manager.log_calculation(
                    shape_type="sfera",
                    shape_dimension="3D",
                    parameters={"raza": raza},
                    result_volume=volum,
                    calculation_time_ms=calc_time,
                    session_id=self.session_id
                )
                
                ttk.Label(self.results_frame_3d, text=f"Volum: {volum:.3f}").pack(pady=2)
                ttk.Label(self.results_frame_3d, text=f"Arie: {arie:.3f}").pack(pady=2)
                
                self.draw_sphere_3d(raza)
                
            elif forma == "prisma":
                a = float(self.a_3d_var.get())
                b = float(self.b_3d_var.get())
                c = float(self.c_3d_var.get())
                inaltime = float(self.inaltime_prisma_var.get())
                
                if (a + b > c) and (a + c > b) and (b + c > a):
                    s = (a + b + c) / 2
                    arie_baza = math.sqrt(s * (s - a) * (s - b) * (s - c))
                    volum = arie_baza * inaltime
                    
                    calc_time = (time.time() - start_time) * 1000
                    self.data_manager.log_calculation(
                        shape_type="prisma",
                        shape_dimension="3D",
                        parameters={"a": a, "b": b, "c": c, "inaltime": inaltime},
                        result_volume=volum,
                        calculation_time_ms=calc_time,
                        session_id=self.session_id
                    )
                    
                    ttk.Label(self.results_frame_3d, text=f"Volum: {volum:.3f}").pack(pady=2)
                    ttk.Label(self.results_frame_3d, text=f"Arie baza: {arie_baza:.3f}").pack(pady=2)
                    
                    self.draw_prism_3d(a, b, c, inaltime)
                else:
                    messagebox.showerror("Eroare", "Nu se poate forma prisma cu aceste laturi pentru baza!")
                    
        except ValueError:
            messagebox.showerror("Eroare", "Introduceti valori numerice valide!")
    
    def draw_rectangle_2d(self, lungime, latime):
        self.clear_frame(self.viz_frame_2d)
        
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        x = -lungime / 2
        y = -latime / 2
        
        rectangle = patches.Rectangle((x, y), lungime, latime, 
                                    fill=False, color='blue', linewidth=2)
        ax.add_patch(rectangle)
        
        spatiu = max(lungime, latime) * 0.3
        ax.set_xlim(x - spatiu, x + lungime + spatiu)
        ax.set_ylim(y - spatiu, y + latime + spatiu)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(f'Dreptunghi {lungime}x{latime}')
        
        canvas = FigureCanvasTkAgg(fig, self.viz_frame_2d)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def draw_square_2d(self, latura):
        self.clear_frame(self.viz_frame_2d)
        
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        x = -latura / 2
        y = -latura / 2
        
        square = patches.Rectangle((x, y), latura, latura, 
                                 fill=False, color='green', linewidth=2)
        ax.add_patch(square)
        
        spatiu = latura * 0.3
        ax.set_xlim(x - spatiu, x + latura + spatiu)
        ax.set_ylim(y - spatiu, y + latura + spatiu)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(f'Patrat cu latura {latura}')
        
        canvas = FigureCanvasTkAgg(fig, self.viz_frame_2d)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def draw_circle_2d(self, raza):
        self.clear_frame(self.viz_frame_2d)
        
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        circle = plt.Circle((0, 0), raza, fill=False, color='red', linewidth=2)
        ax.add_patch(circle)
        
        ax.plot([0, raza], [0, 0], 'r--', linewidth=1)
        ax.plot(0, 0, 'ro', markersize=5)
        
        spatiu = raza * 0.3
        ax.set_xlim(-raza - spatiu, raza + spatiu)
        ax.set_ylim(-raza - spatiu, raza + spatiu)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(f'Cerc cu raza {raza}')
        
        canvas = FigureCanvasTkAgg(fig, self.viz_frame_2d)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def draw_triangle_2d(self, a, b, c):
        self.clear_frame(self.viz_frame_2d)
        
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        latura_medie = (a + b + c) / 3
        inaltime = latura_medie * math.sqrt(3) / 2
        
        punctul_A = [0, 0]
        punctul_B = [latura_medie, 0]
        punctul_C = [latura_medie/2, inaltime]
        
        triangle = patches.Polygon([punctul_A, punctul_B, punctul_C], 
                                 fill=False, color='purple', linewidth=2)
        ax.add_patch(triangle)
        
        ax.plot([punctul_A[0], punctul_B[0], punctul_C[0]], 
               [punctul_A[1], punctul_B[1], punctul_C[1]], 'o', color='purple', markersize=5)
        
        spatiu = latura_medie * 0.2
        ax.set_xlim(-spatiu, latura_medie + spatiu)
        ax.set_ylim(-spatiu, inaltime + spatiu)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(f'Triunghi {a}-{b}-{c}')
        
        canvas = FigureCanvasTkAgg(fig, self.viz_frame_2d)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def draw_cube_3d(self, latura):
        self.clear_frame(self.viz_frame_3d)
        
        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111, projection='3d')
        
        valori = [-latura/2, latura/2]
        X, Y = np.meshgrid(valori, valori)
        
        ax.plot_surface(X, Y, np.ones_like(X) * latura/2, alpha=0.6, color='lightblue')
        ax.plot_surface(X, Y, np.ones_like(X) * -latura/2, alpha=0.6, color='lightblue')
        ax.plot_surface(X, np.ones_like(X) * latura/2, Y, alpha=0.6, color='lightgreen')
        ax.plot_surface(X, np.ones_like(X) * -latura/2, Y, alpha=0.6, color='lightgreen')
        ax.plot_surface(np.ones_like(X) * latura/2, X, Y, alpha=0.6, color='lightcoral')
        ax.plot_surface(np.ones_like(X) * -latura/2, X, Y, alpha=0.6, color='lightcoral')
        
        ax.set_xlim([-latura, latura])
        ax.set_ylim([-latura, latura])
        ax.set_zlim([-latura, latura])
        ax.set_title(f'Cub cu latura {latura}')
        
        canvas = FigureCanvasTkAgg(fig, self.viz_frame_3d)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def draw_parallelepiped_3d(self, lungime, latime, inaltime):
        self.clear_frame(self.viz_frame_3d)
        
        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111, projection='3d')
        
        coordonate_x = [-lungime/2, lungime/2]
        coordonate_y = [-latime/2, latime/2]
        coordonate_z = [-inaltime/2, inaltime/2]
        
        X, Y = np.meshgrid(coordonate_x, coordonate_y)
        ax.plot_surface(X, Y, np.ones_like(X) * coordonate_z[1], alpha=0.6, color='lightblue')
        ax.plot_surface(X, Y, np.ones_like(X) * coordonate_z[0], alpha=0.6, color='lightblue')
        
        X, Z = np.meshgrid(coordonate_x, coordonate_z)
        ax.plot_surface(X, np.ones_like(X) * coordonate_y[1], Z, alpha=0.6, color='lightgreen')
        ax.plot_surface(X, np.ones_like(X) * coordonate_y[0], Z, alpha=0.6, color='lightgreen')
        
        Y, Z = np.meshgrid(coordonate_y, coordonate_z)
        ax.plot_surface(np.ones_like(Y) * coordonate_x[1], Y, Z, alpha=0.6, color='lightcoral')
        ax.plot_surface(np.ones_like(Y) * coordonate_x[0], Y, Z, alpha=0.6, color='lightcoral')
        
        dim_max = max(lungime, latime, inaltime)
        ax.set_xlim([-dim_max, dim_max])
        ax.set_ylim([-dim_max, dim_max])
        ax.set_zlim([-dim_max, dim_max])
        ax.set_title(f'Paralelpiped {lungime}x{latime}x{inaltime}')
        
        canvas = FigureCanvasTkAgg(fig, self.viz_frame_3d)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def draw_sphere_3d(self, raza):
        self.clear_frame(self.viz_frame_3d)
        
        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111, projection='3d')
        
        unghi_u = np.linspace(0, 2 * np.pi, 30)
        unghi_v = np.linspace(0, np.pi, 30)
        
        coordonata_x = raza * np.outer(np.cos(unghi_u), np.sin(unghi_v))
        coordonata_y = raza * np.outer(np.sin(unghi_u), np.sin(unghi_v))
        coordonata_z = raza * np.outer(np.ones(np.size(unghi_u)), np.cos(unghi_v))
        
        ax.plot_surface(coordonata_x, coordonata_y, coordonata_z, alpha=0.6, color='lightcoral')
        ax.scatter([0], [0], [0], color='black', s=30)
        
        ax.set_xlim([-raza*1.2, raza*1.2])
        ax.set_ylim([-raza*1.2, raza*1.2])
        ax.set_zlim([-raza*1.2, raza*1.2])
        ax.set_title(f'Sfera cu raza {raza}')
        
        canvas = FigureCanvasTkAgg(fig, self.viz_frame_3d)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def draw_prism_3d(self, a, b, c, inaltime):
        self.clear_frame(self.viz_frame_3d)
        
        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111, projection='3d')
        
        latura_medie = (a + b + c) / 3
        inaltime_triunghi = latura_medie * math.sqrt(3) / 2
        
        A_jos = [0, 0, -inaltime/2]
        B_jos = [latura_medie, 0, -inaltime/2]
        C_jos = [latura_medie/2, inaltime_triunghi, -inaltime/2]
        
        A_sus = [0, 0, inaltime/2]
        B_sus = [latura_medie, 0, inaltime/2]
        C_sus = [latura_medie/2, inaltime_triunghi, inaltime/2]
        
        fetele = [
            [A_jos, B_jos, C_jos],
            [A_sus, B_sus, C_sus],
            [A_jos, A_sus, B_sus, B_jos],
            [B_jos, B_sus, C_sus, C_jos],
            [C_jos, C_sus, A_sus, A_jos]
        ]
        
        poligon = Poly3DCollection(fetele, alpha=0.6, facecolor='lightpink', edgecolor='black')
        ax.add_collection3d(poligon)
        
        coordonata_maxima = max(latura_medie, inaltime_triunghi, inaltime)
        ax.set_xlim([0-coordonata_maxima*0.2, latura_medie+coordonata_maxima*0.2])
        ax.set_ylim([0-coordonata_maxima*0.2, inaltime_triunghi+coordonata_maxima*0.2])
        ax.set_zlim([-inaltime/2-coordonata_maxima*0.2, inaltime/2+coordonata_maxima*0.2])
        ax.set_title(f'Prisma triunghiulara\nBaza: {a}-{b}-{c}, Inaltime: {inaltime}')
        
        canvas = FigureCanvasTkAgg(fig, self.viz_frame_3d)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

def main():
    root = tk.Tk()
    app = CalculatorGeometrie(root)
    root.mainloop()

if __name__ == "__main__":
    main()
