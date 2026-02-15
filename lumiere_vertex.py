import asyncio
import json
import threading
import customtkinter as ctk
from bleak import BleakClient
import math
import time
import colorsys
import random
import mss
import numpy as np



# --- 1.settings ---
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        DEVICE_ADDRESS = config.get("device_address")
except FileNotFoundError:
    DEVICE_ADDRESS = "PUT_YOUR_MAC_ADDRESS_HERE" 
    print("Warning: config.json not found. Using default address.")

WRITE_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"
APP_VERSION = "v3.0.0 Stable"
DEV_NAME = "Dev by: EL-Haoudar Bilal"

# Gamma table for color correction
GAMMA = [int(((i / 255) ** 2.2) * 255) for i in range(256)]

# --- 2. SCENE LIBRARY ---
class SceneLibrary:
    def __init__(self):
        self.scenes = {
            "Nature 🌿": [
                {"name": "Amazon Rain", "colors": [0.3, 0.4, 0.25], "speed": 0.02},
                {"name": "Deep Ocean", "colors": [0.6, 0.65, 0.55], "speed": 0.03},
                {"name": "Sunset Vibes", "colors": [0.05, 0.08, 0.95], "speed": 0.04},
                {"name": "Northern Lights", "colors": [0.4, 0.7, 0.8], "speed": 0.02},
                {"name": "Sahara Dunes", "colors": [0.1, 0.12, 0.08], "speed": 0.01},
                {"name": "Cherry Blossom", "colors": [0.9, 0.85, 0.95], "speed": 0.03},
                {"name": "Thunderstorm", "colors": [0.6, 0.75, 0.8], "flash": True, "speed": 0.1},
                {"name": "Autumn Leaves", "colors": [0.08, 0.12, 0.05], "speed": 0.025}
            ],
            "Emotion 💖": [
                {"name": "Deep Focus", "colors": [0.55, 0.6, 0.62], "speed": 0.01},
                {"name": "Romance", "colors": [0.95, 0.0, 0.85], "speed": 0.02},
                {"name": "Energy Boost", "colors": [0.1, 0.3, 0.5], "speed": 0.08},
                {"name": "Calm Mind", "colors": [0.45, 0.5, 0.55], "speed": 0.015},
                {"name": "Mystery", "colors": [0.75, 0.8, 0.2], "speed": 0.03},
                {"name": "Happy Day", "colors": [0.15, 0.4, 0.85], "speed": 0.05}
            ],
            "Tech & Party 🚀": [
                {"name": "Cyberpunk 2077", "colors": [0.83, 0.5, 0.9], "speed": 0.05},
                {"name": "Matrix Code", "colors": [0.33, 0.3, 0.36], "speed": 0.06},
                {"name": "Vaporwave", "colors": [0.5, 0.8, 0.9], "speed": 0.04},
                {"name": "Neon City", "colors": [0.0, 0.33, 0.66], "speed": 0.07},
                {"name": "RGB Gamer", "colors": [0.0, 0.33, 0.66, 0.99], "speed": 0.09},
                {"name": "Disco Fever", "colors": [0.0, 0.2, 0.4, 0.6, 0.8], "speed": 0.15},
                {"name": "Hacker Mode", "colors": [0.33, 0.0], "speed": 0.1}
            ],
            "Elements 🔥": [
                {"name": "Fire & Magma", "colors": [0.0, 0.05, 0.02], "speed": 0.06},
                {"name": "Ice Crystals", "colors": [0.5, 0.55, 0.6], "speed": 0.02},
                {"name": "Lightning", "colors": [0.65, 0.7, 0.15], "speed": 0.1},
                {"name": "Space Void", "colors": [0.7, 0.75, 0.8], "speed": 0.01}
            ]
        }
    
    def get_all_categories(self):
        return list(self.scenes.keys())

    def get_scenes_for_category(self, category):
        return self.scenes.get(category, [])

# --- 3. MAIN ENGINE ---
class LightEngine:
    def __init__(self, status_callback):
        self.client = None
        self.running = True
        self.status_callback = status_callback
        
        self.current_rgb = [0.0, 0.0, 0.0]
        self.target_rgb = [0.0, 0.0, 0.0]
        self.brightness = 1.0
        self.mode = "STATIC" 
        
        self.active_scene = None
        self.t = 0.0
        self.scene_speed = 0.02

    async def connect(self):
        try:
            self.client = BleakClient(DEVICE_ADDRESS)
            await self.client.connect()
            self.status_callback("conn", "Connected ✅")
            return True
        except Exception as e:
            self.status_callback("conn", "Disconnected ❌")
            print(f"Connection Error: {e}")
            return False

    def set_static_color(self, r, g, b):
        self.mode = "STATIC"
        self.target_rgb = [r, g, b]
        self.status_callback("mode", "Manual Color")

    def set_scene(self, scene_data):
        self.mode = "SCENE"
        self.active_scene = scene_data
        self.scene_speed = scene_data["speed"]
        self.status_callback("mode", f"Scene: {scene_data['name']}")

    def set_sync_mode(self):
        self.mode = "SYNC"
        self.status_callback("mode", "🖥️ Screen Sync")

    async def loop(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            
            while self.running:
                if not self.client or not self.client.is_connected:
                    await asyncio.sleep(2)
                    continue

                if self.mode == "STATIC":
                    pass 

                elif self.mode == "SCENE":
                    colors = self.active_scene["colors"]
                    idx_float = (self.t) % len(colors)
                    idx1 = int(idx_float)
                    idx2 = (idx1 + 1) % len(colors)
                    mix = idx_float - idx1
                    
                    h1, h2 = colors[idx1], colors[idx2]
                    if abs(h1 - h2) > 0.5:
                        if h1 < h2: h1 += 1.0
                        else: h2 += 1.0
                    curr_h = (h1 * (1-mix)) + (h2 * mix)
                    curr_h %= 1.0
                    
                    r, g, b = colorsys.hsv_to_rgb(curr_h, 1.0, 1.0)
                    self.target_rgb = [r*255, g*255, b*255]
                    self.t += self.scene_speed

                elif self.mode == "SYNC":
                    try:
                        sct_img = sct.grab(monitor)
                        img = np.array(sct_img)
                        small = img[::50, ::50]
                        avg = np.mean(small, axis=(0, 1))
                        self.target_rgb = [avg[2], avg[1], avg[0]]
                    except: pass

                # --- Smoothing & Gamma ---
                smooth = 0.1
                if self.mode == "SYNC": smooth = 0.25

                self.current_rgb[0] += (self.target_rgb[0] - self.current_rgb[0]) * smooth
                self.current_rgb[1] += (self.target_rgb[1] - self.current_rgb[1]) * smooth
                self.current_rgb[2] += (self.target_rgb[2] - self.current_rgb[2]) * smooth

                final_r = int(self.current_rgb[0] * self.brightness)
                final_g = int(self.current_rgb[1] * self.brightness)
                final_b = int(self.current_rgb[2] * self.brightness)

                # Clamp
                final_r = GAMMA[max(0, min(255, final_r))]
                final_g = GAMMA[max(0, min(255, final_g))]
                final_b = GAMMA[max(0, min(255, final_b))]

                packet = bytearray([0x7e, 0x00, 0x05, 0x03, final_r, final_g, final_b, 0x00, 0xef])
                try:
                    await self.client.write_gatt_char(WRITE_UUID, packet, response=False)
                    self.status_callback("rgb", f"RGB: {final_r},{final_g},{final_b}")
                except: pass

                await asyncio.sleep(0.03)

# RESPONSIVE GUI
class LumiereApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.library = SceneLibrary()
        
        # إعدادات النافذة
        self.title(f"LUMIÈRE ULTIMATE {APP_VERSION}")
        self.geometry("1100x700")
        self.minsize(800, 600)
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_expanded = True

        # 1. Sidebar - Increased width to 280
        self.create_sidebar()
        
        # 2. Main Area
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # 3. Bottom Status Bar
        self.create_status_bar()

        # Engine Init
        self.engine = LightEngine(self.update_status_ui)
        self.start_engine()

        self.show_scenes_ui()

    def create_sidebar(self):
        # CHANGED: Width increased from 220 to 280
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Toggle Button
        self.btn_menu = ctk.CTkButton(self.sidebar, text="☰", width=40, height=40,
                                      fg_color="transparent", hover_color="#444",
                                      command=self.toggle_sidebar)
        self.btn_menu.place(x=10, y=10)

        # Logo
        self.lbl_logo = ctk.CTkLabel(self.sidebar, text="LUMIÈRE", font=("Impact", 24))
        self.lbl_logo.place(x=60, y=15)
        
        # Navigation
        self.nav_buttons = []
        
        btn_data = [
            ("🌍", "SCENES", self.show_scenes_ui),
            ("🎨", "MANUAL", self.show_manual_ui),
            ("🖥️", "SYNC", self.show_sync_ui)
        ]
        
        start_y = 100
        for icon, text, cmd in btn_data:
            # Added more spacing in text for cleaner look
            btn = ctk.CTkButton(self.sidebar, text=f"  {icon}    {text}", anchor="w",
                                height=50, font=("Arial", 14, "bold"),
                                fg_color="transparent", hover_color="#333",
                                command=cmd)
            btn.place(x=10, y=start_y, relwidth=0.9)
            self.nav_buttons.append({"btn": btn, "icon": icon, "text": text})
            start_y += 60

        # Brightness
        self.lbl_bright = ctk.CTkLabel(self.sidebar, text="BRIGHTNESS", font=("Arial", 10))
        self.lbl_bright.place(x=20, y=start_y + 20)
        
        self.bright_slider = ctk.CTkSlider(self.sidebar, from_=0, to=1, command=self.change_brightness)
        self.bright_slider.set(1.0)
        self.bright_slider.place(x=20, y=start_y + 50, relwidth=0.8)

        # Developer Credit
        self.lbl_dev = ctk.CTkLabel(self.sidebar, text=DEV_NAME, 
                                    font=("Consolas", 10, "bold"), text_color="#666")
        self.lbl_dev.pack(side="bottom", pady=20)

    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.sidebar.configure(width=50)
            self.lbl_logo.place_forget()
            self.lbl_bright.place_forget()
            self.bright_slider.place(x=10, y=300, relwidth=0.7)
            self.lbl_dev.pack_forget()
            
            for item in self.nav_buttons:
                item["btn"].configure(text=f"{item['icon']}")
                item["btn"].place(x=10, relwidth=0.7)
                
            self.sidebar_expanded = False
        else:
            # CHANGED: Width increased from 220 to 280
            self.sidebar.configure(width=280)
            self.lbl_logo.place(x=60, y=15)
            self.lbl_bright.place(x=20, y=280)
            self.bright_slider.place(x=20, y=310, relwidth=0.8)
            self.lbl_dev.pack(side="bottom", pady=20)
            
            for item in self.nav_buttons:
                item["btn"].configure(text=f"  {item['icon']}    {item['text']}")
                item["btn"].place(x=10, relwidth=0.9)
                
            self.sidebar_expanded = True

    def create_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color="#1a1a1a")
        self.status_bar.grid(row=1, column=1, sticky="ew")
        
        self.lbl_conn = ctk.CTkLabel(self.status_bar, text="Connecting...", font=("Consolas", 12), text_color="orange")
        self.lbl_conn.pack(side="left", padx=20)
        
        ctk.CTkLabel(self.status_bar, text="|", text_color="gray").pack(side="left")
        
        self.lbl_mode = ctk.CTkLabel(self.status_bar, text="Mode: Idle", font=("Consolas", 12))
        self.lbl_mode.pack(side="left", padx=20)

        ctk.CTkLabel(self.status_bar, text="|", text_color="gray").pack(side="left")

        self.lbl_rgb = ctk.CTkLabel(self.status_bar, text="RGB: 0,0,0", font=("Consolas", 12), text_color="#00ffff")
        self.lbl_rgb.pack(side="right", padx=20)
        
        ctk.CTkLabel(self.status_bar, text=APP_VERSION, text_color="gray", font=("Arial", 10)).pack(side="right", padx=20)

    # --- UI Logic ---
    def update_status_ui(self, key, value):
        if key == "conn":
            self.lbl_conn.configure(text=value, text_color="#00ff00" if "Connected" in value else "red")
        elif key == "mode":
            self.lbl_mode.configure(text=value)
        elif key == "rgb":
            self.lbl_rgb.configure(text=value)

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_scenes_ui(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="SCENE LIBRARY", font=("Impact", 30)).pack(pady=(10, 20), anchor="w")
        
        scroll = ctk.CTkScrollableFrame(self.main_frame)
        scroll.pack(fill="both", expand=True)
        
        categories = self.library.get_all_categories()
        
        for cat in categories:
            ctk.CTkLabel(scroll, text=cat, font=("Arial", 20, "bold"), anchor="w").pack(fill="x", pady=(20, 10))
            
            grid_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            grid_frame.pack(fill="x")
            
            scenes = self.library.get_scenes_for_category(cat)
            
            for i, scene in enumerate(scenes):
                if i % 3 == 0: row_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
                if i % 3 == 0: row_frame.pack(fill="x", pady=5)
                
                btn = ctk.CTkButton(row_frame, text=scene["name"], height=50,
                                    fg_color="#333", hover_color="#0055aa",
                                    font=("Arial", 14),
                                    command=lambda s=scene: self.engine.set_scene(s))
                btn.pack(side="left", fill="x", expand=True, padx=5)

    def show_manual_ui(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="MANUAL MIXER", font=("Impact", 30)).pack(pady=20, anchor="w")
        
        container = ctk.CTkFrame(self.main_frame)
        container.pack(fill="both", expand=True, padx=50, pady=20)
        
        for color, name in [("red", "RED CHANNEL"), ("green", "GREEN CHANNEL"), ("blue", "BLUE CHANNEL")]:
            ctk.CTkLabel(container, text=name, text_color=color, font=("Arial", 14, "bold")).pack(pady=(30, 5))
            slider = ctk.CTkSlider(container, from_=0, to=255, progress_color=color, height=20, command=self.update_manual)
            slider.set(0)
            slider.pack(fill="x", padx=50)
            setattr(self, f"slider_{name.split()[0].lower()}", slider)

    def show_sync_ui(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="SCREEN SYNC", font=("Impact", 30)).pack(pady=20, anchor="w")
        
        frame = ctk.CTkFrame(self.main_frame, fg_color="#222")
        frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        btn = ctk.CTkButton(frame, text="ACTIVATE AMBILIGHT", height=120, font=("Impact", 24),
                            fg_color="#5000aa", hover_color="#7000dd",
                            command=self.engine.set_sync_mode)
        btn.pack(fill="x", padx=50, pady=80)
        
        ctk.CTkLabel(frame, text="Real-time Low Latency Mode active.", text_color="gray").pack()

    def update_manual(self, _):
        r = int(self.slider_red.get())
        g = int(self.slider_green.get())
        b = int(self.slider_blue.get())
        self.engine.set_static_color(r, g, b)

    def change_brightness(self, val):
        self.engine.brightness = val

    def start_engine(self):
        loop = asyncio.new_event_loop()
        t = threading.Thread(target=lambda: self._run_loop(loop), daemon=True)
        t.start()

    def _run_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.engine.connect())
        loop.run_until_complete(self.engine.loop())

if __name__ == "__main__":
    app = LumiereApp()
    app.mainloop()