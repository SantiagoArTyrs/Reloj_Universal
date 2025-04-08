import tkinter as tk
from tkinter import ttk
import math
import pytz
from datetime import datetime
import time
import threading

class Node:
    def __init__(self, country, timezone):
        self.country = country
        self.timezone = timezone
        self.prev = None
        self.next = None

class DoublyCircularLinkedList:
    def __init__(self):
        self.head = None

    def append(self, country, timezone):
        new_node = Node(country, timezone)
        if not self.head:
            self.head = new_node
            new_node.prev = new_node
            new_node.next = new_node
        else:
            tail = self.head.prev
            tail.next = new_node
            new_node.prev = tail
            new_node.next = self.head
            self.head.prev = new_node

    def move_next(self):
        self.head = self.head.next

    def move_prev(self):
        self.head = self.head.prev

    def find(self, country):
        current = self.head
        while True:
            if current.country == country:
                return current
            current = current.next
            if current == self.head:
                break
        return None

    def get_all_countries(self):
        countries = []
        current = self.head
        while True:
            countries.append(current.country)
            current = current.next
            if current == self.head:
                break
        return countries

class ClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reloj Internacional")
        
        # Variables
        self.current_theme = "Oscuro"
        self.sound_enabled = False
        self.animation_active = False
        self._last_second = None
        
        # Temas
        self.THEMES = {
            "Oscuro": {
                "bg": "#101021",
                "fg": "white",
                "clock_face": "white",
                "hour_hand": "white",
                "min_hand": "yellow",
                "sec_hand": "red",
                "text": "white",
                "digital": "white",
                "button_bg": "#16213e",
                "button_fg": "white"
            },
            "Claro": {
                "bg": "#f0f0f0",
                "fg": "black",
                "clock_face": "black",
                "hour_hand": "black",
                "min_hand": "black",
                "sec_hand": "red",
                "text": "black",
                "digital": "blue",
                "button_bg": "#e0e0e0",
                "button_fg": "black"
            }
        }

        # Lista de zonas horarias
        self.timezone_list = DoublyCircularLinkedList()
        self.countries = [
            ("Colombia", "America/Bogota"),
            ("Argentina", "America/Argentina/Buenos_Aires"),
            ("México", "America/Mexico_City"),
            ("España", "Europe/Madrid"),
            ("Japón", "Asia/Tokyo"),
            ("Estados Unidos (NY)", "America/New_York"),
            ("Reino Unido", "Europe/London"),
            ("Francia", "Europe/Paris"),
            ("Alemania", "Europe/Berlin"),
            ("China", "Asia/Shanghai"),
            ("Australia (Syd)", "Australia/Sydney"),
            ("Rusia (Moscú)", "Europe/Moscow"),
            ("Brasil (São Paulo)", "America/Sao_Paulo"),
            ("Chile", "America/Santiago"),
            ("India", "Asia/Kolkata"),
            ("Sudáfrica", "Africa/Johannesburg"),
            ("Corea del Sur", "Asia/Seoul")
        ]

        for country, tz in self.countries:
            self.timezone_list.append(country, tz)

        self.setup_ui()
        self.update_clock()

    def setup_ui(self):
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg=self.THEMES[self.current_theme]["bg"])
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Controles superiores
        control_frame = tk.Frame(self.main_frame, bg=self.THEMES[self.current_theme]["bg"])
        control_frame.pack(fill="x", pady=(0, 20))

        # Tema
        tk.Label(control_frame, text="Tema:", bg=self.THEMES[self.current_theme]["bg"],
                fg=self.THEMES[self.current_theme]["fg"]).pack(side="left", padx=(0, 10))
        
        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(control_frame, textvariable=self.theme_var,
                                 values=list(self.THEMES.keys()), state="readonly")
        theme_combo.pack(side="left", padx=(0, 20))
        theme_combo.bind("<<ComboboxSelected>>", self.change_theme)

        # País
        tk.Label(control_frame, text="País:", bg=self.THEMES[self.current_theme]["bg"],
                fg=self.THEMES[self.current_theme]["fg"]).pack(side="left", padx=(0, 10))
        
        self.country_var = tk.StringVar(value=self.timezone_list.head.country)
        country_combo = ttk.Combobox(control_frame, textvariable=self.country_var,
                                   values=self.timezone_list.get_all_countries(), state="readonly")
        country_combo.pack(side="left")
        country_combo.bind("<<ComboboxSelected>>", self.change_country)

        # Sonido
        self.sound_var = tk.BooleanVar(value=self.sound_enabled)
        sound_check = tk.Checkbutton(control_frame, text="Tic Tac", variable=self.sound_var,
                                   bg=self.THEMES[self.current_theme]["bg"],
                                   fg=self.THEMES[self.current_theme]["fg"],
                                   selectcolor=self.THEMES[self.current_theme]["bg"])
        sound_check.pack(side="right")

        # Canvas para el reloj
        self.canvas = tk.Canvas(self.main_frame, width=400, height=400,
                              bg=self.THEMES[self.current_theme]["bg"], highlightthickness=0)
        self.canvas.pack(pady=20)

        # Etiquetas
        self.location_label = tk.Label(self.main_frame, text="",
                                     font=("Arial", 18, "bold"),
                                     bg=self.THEMES[self.current_theme]["bg"],
                                     fg=self.THEMES[self.current_theme]["text"])
        self.location_label.pack(pady=(20, 5))

        self.time_label = tk.Label(self.main_frame, text="",
                                 font=("Arial", 24),
                                 bg=self.THEMES[self.current_theme]["bg"],
                                 fg=self.THEMES[self.current_theme]["digital"])
        self.time_label.pack()

        # Botones de navegación
        button_frame = tk.Frame(self.main_frame, bg=self.THEMES[self.current_theme]["bg"])
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="◀ Anterior",
                 command=lambda: self.change_timezone(-1),
                 bg=self.THEMES[self.current_theme]["button_bg"],
                 fg=self.THEMES[self.current_theme]["button_fg"],
                 font=("Arial", 12)).pack(side="left", padx=10)

        tk.Button(button_frame, text="Siguiente ▶",
                 command=lambda: self.change_timezone(1),
                 bg=self.THEMES[self.current_theme]["button_bg"],
                 fg=self.THEMES[self.current_theme]["button_fg"],
                 font=("Arial", 12)).pack(side="left")

    def get_current_time(self):
        # Obtener la zona horaria actual
        tz = pytz.timezone(self.timezone_list.head.timezone)
        # Obtener la hora UTC actual
        utc_now = datetime.now(pytz.UTC)
        # Convertir a la zona horaria local
        local_time = utc_now.astimezone(tz)
        return local_time

    def draw_clock(self, current_time):
        self.canvas.delete("all")
        
        # Configuración del reloj
        center_x = 200
        center_y = 200
        radius = 150
        
        # Dibujar círculo exterior
        self.canvas.create_oval(center_x - radius, center_y - radius,
                              center_x + radius, center_y + radius,
                              width=2, outline=self.THEMES[self.current_theme]["clock_face"])
        
        # Dibujar marcadores de hora
        for i in range(60):
            angle = i * 6 - 90
            start = 0.85 * radius if i % 5 == 0 else 0.90 * radius
            end = radius
            rad = math.radians(angle)
            x1 = center_x + math.cos(rad) * start
            y1 = center_y + math.sin(rad) * start
            x2 = center_x + math.cos(rad) * end
            y2 = center_y + math.sin(rad) * end
            
            width = 3 if i % 5 == 0 else 1
            self.canvas.create_line(x1, y1, x2, y2,
                                  fill=self.THEMES[self.current_theme]["clock_face"],
                                  width=width)
            
            if i % 5 == 0:
                text_radius = radius * 0.75
                text_x = center_x + math.cos(rad) * text_radius
                text_y = center_y + math.sin(rad) * text_radius
                hour_number = str(i // 5 if i > 0 else 12)
                self.canvas.create_text(text_x, text_y, text=hour_number,
                                     fill=self.THEMES[self.current_theme]["clock_face"],
                                     font=("Arial", 12, "bold"))
        
        # Calcular ángulos para las manecillas
        hour = current_time.hour % 12
        minute = current_time.minute
        second = current_time.second
        
        # Hora (toma en cuenta minutos para movimiento suave)
        hour_angle = (hour + minute / 60.0) * 30 - 90
        hour_rad = math.radians(hour_angle)
        hour_length = radius * 0.5
        hour_x = center_x + math.cos(hour_rad) * hour_length
        hour_y = center_y + math.sin(hour_rad) * hour_length
        self.canvas.create_line(center_x, center_y, hour_x, hour_y,
                              fill=self.THEMES[self.current_theme]["hour_hand"],
                              width=6)
        
        # Minuto (toma en cuenta segundos para movimiento suave)
        min_angle = (minute + second / 60.0) * 6 - 90
        min_rad = math.radians(min_angle)
        min_length = radius * 0.7
        min_x = center_x + math.cos(min_rad) * min_length
        min_y = center_y + math.sin(min_rad) * min_length
        self.canvas.create_line(center_x, center_y, min_x, min_y,
                              fill=self.THEMES[self.current_theme]["min_hand"],
                              width=4)
        
        # Segundo
        sec_angle = second * 6 - 90
        sec_rad = math.radians(sec_angle)
        sec_length = radius * 0.8
        sec_x = center_x + math.cos(sec_rad) * sec_length
        sec_y = center_y + math.sin(sec_rad) * sec_length
        self.canvas.create_line(center_x, center_y, sec_x, sec_y,
                              fill=self.THEMES[self.current_theme]["sec_hand"],
                              width=2)
        
        # Punto central
        self.canvas.create_oval(center_x-5, center_y-5, center_x+5, center_y+5,
                              fill=self.THEMES[self.current_theme]["sec_hand"])

    def update_clock(self):
        if not self.animation_active:
            current_time = self.get_current_time()
            
            # Actualizar el reloj analógico
            self.draw_clock(current_time)
            
            # Actualizar etiquetas
            self.location_label.config(text=f"Hora actual en {self.timezone_list.head.country}")
            self.time_label.config(text=current_time.strftime("%H:%M:%S"))
            
            # Reproducir sonido si está activado
            if self.sound_var.get():
                if current_time.second != self._last_second:
                    self._last_second = current_time.second
                    threading.Thread(target=self.play_tick).start()
        
        self.root.after(1000, self.update_clock)

    def play_tick(self):
        if self.sound_var.get():
            try:
                import winsound
                winsound.Beep(1000, 50)
            except ImportError:
                # Fallback para sistemas que no son Windows
                print('\a')

    def change_timezone(self, direction):
        if direction > 0:
            self.timezone_list.move_next()
        else:
            self.timezone_list.move_prev()
        
        self.country_var.set(self.timezone_list.head.country)
        self.update_clock()

    def change_country(self, event=None):
        selected_country = self.country_var.get()
        node = self.timezone_list.find(selected_country)
        if node:
            self.timezone_list.head = node
            self.update_clock()

    def change_theme(self, event=None):
        self.current_theme = self.theme_var.get()
        
        # Actualizar colores
        self.main_frame.configure(bg=self.THEMES[self.current_theme]["bg"])
        self.canvas.configure(bg=self.THEMES[self.current_theme]["bg"])
        self.location_label.configure(bg=self.THEMES[self.current_theme]["bg"],
                                    fg=self.THEMES[self.current_theme]["text"])
        self.time_label.configure(bg=self.THEMES[self.current_theme]["bg"],
                                fg=self.THEMES[self.current_theme]["digital"])
        
        # Redibujar el reloj con el nuevo tema
        self.update_clock()

def main():
    root = tk.Tk()
    app = ClockApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()