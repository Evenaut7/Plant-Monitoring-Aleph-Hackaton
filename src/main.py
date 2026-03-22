import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database.models import db
from database.plantManager import PlantManager
from groqConfig.groq_assistant import analyze_plant
from utilities.cameraManager import CameraDevice
from utilities.chartManager import ChartManager
from playhouse.shortcuts import model_to_dict

from UI.app import App 

def build_callback(manager, plant, specimen_data, camera_id):
    def on_photo(image_path):
        if db.is_closed():
            db.connect()
        try:
            plant_data = analyze_plant(
                image_path=image_path,
                specimen_data=specimen_data
            )
            manager.register_current_observation(
                plant=plant,
                health=plant_data.get("health_state", "Unknown"),
                phase=plant_data.get("maturation_phase", "Unknown"),
                color=plant_data.get("foliage_color", "Unknown"),
                soil=plant_data.get("soil_condition", "Unknown"),
                pests=plant_data.get("pests", "None"),
                tendency=plant_data.get("health_tendency", "Unknown")
            )
            return plant_data 
        except Exception as e:
            print(f"[Camera {camera_id}] Analysis error: {e}")
            return None
        finally:
            if not db.is_closed():
                db.close()
    return on_photo

class MonitorCarouselWindow:
    def __init__(self, root, devices, db_manager):
        self.root = root
        self.devices = devices
        self.db_manager = db_manager
        self.current_index = 0
        
        self.root.title("Plant Monitoring Panel - Real Time")
        self.root.geometry("1050x650") 
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.root.columnconfigure(0, weight=3) 
        self.root.columnconfigure(1, weight=2) 
        self.root.rowconfigure(0, weight=1)    
        self.root.rowconfigure(1, weight=0)    
        
        self.video_label = ttk.Label(self.root, text="Starting camera...", anchor="center")
        self.video_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.details_frame = ttk.Frame(self.root, padding=10)
        self.details_frame.grid(row=0, column=1, sticky="nsew", pady=10)
        
        ttk.Label(self.details_frame, text="Live Status", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0,5))
        
        self.plant_title_label = ttk.Label(self.details_frame, text="Plant", font=("Segoe UI", 12, "italic"))
        self.plant_title_label.pack(anchor="w", pady=(0,10))
        
        self.status_list_label = ttk.Label(self.details_frame, text="", font=("Consolas", 11), justify="left")
        self.status_list_label.pack(fill="x", pady=(0, 15))
        
        self.chart_frame = ttk.Frame(self.details_frame)
        self.chart_frame.pack(fill="both", expand=True)
        self.current_canvas = None
        
        self.controls_frame = ttk.Frame(self.root, padding=10)
        self.controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        ttk.Button(self.controls_frame, text="◀ Previous Camera", command=self.prev_camera).pack(side="left", padx=20)
        ttk.Button(self.controls_frame, text="Next Camera ▶", command=self.next_camera).pack(side="right", padx=20)
        
        self.cam_counter_label = ttk.Label(self.controls_frame, text="", font=("Segoe UI", 10, "bold"))
        self.cam_counter_label.pack(side="top")

        self.update_video_feed()

    def update_chart(self):
        current_cam = self.devices[self.current_index]
        history = self.db_manager.get_observation_history(current_cam.plant)
        fig = ChartManager.get_health_evolution_figure(history, current_cam.plant_name)
        
        if self.current_canvas:
            self.current_canvas.get_tk_widget().destroy()
            
        self.current_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.current_canvas.draw()
        self.current_canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_video_feed(self):
        current_cam = self.devices[self.current_index]
        
        if getattr(self, "_last_seen_text", None) != current_cam.latest_analysis_text:
            self._last_seen_text = current_cam.latest_analysis_text
            self.update_chart()
        
        self.plant_title_label.config(text=current_cam.plant_name)
        self.status_list_label.config(text=current_cam.latest_analysis_text)
        self.cam_counter_label.config(text=f"Viewing Camera {self.current_index + 1} of {len(self.devices)} (Hardware ID: {current_cam.ID})")
        
        rgb_frame = current_cam.get_tkinter_frame()
        if rgb_frame is not None:
            img = Image.fromarray(rgb_frame)
            img.thumbnail((650, 480))
            self.tk_image = ImageTk.PhotoImage(image=img)
            self.video_label.config(image=self.tk_image)
            self.video_label.image = self.tk_image 
        
        self.root.after(30, self.update_video_feed)

    def next_camera(self):
        self.current_index = (self.current_index + 1) % len(self.devices)
        self.video_label.config(image="")
        self._last_seen_text = None 

    def prev_camera(self):
        self.current_index = (self.current_index - 1) % len(self.devices)
        self.video_label.config(image="")
        self._last_seen_text = None 

    def on_close(self):
        print("\nTurning off cameras and shutting down system...")
        for cam in self.devices:
            cam.deactivate_job()
            cam.release()
        self.db_manager.close_database()
        self.root.destroy()

def main():
    print("Verifying database...")
    temp_manager = PlantManager()
    temp_manager.initialize_database()
    
    if len(list(temp_manager.get_plants())) == 0:
        print("Empty database. Creating default plants...")
        try:
            temp_manager.create_complete_plant(
                specimen_name="Monstera Deliciosa",
                care_instructions="Indirect light, moderate watering.",
                color_desc="Dark green",
                maduration_desc="Vegetative",
                plant_desc="Office Monstera"
            )
            temp_manager.create_complete_plant(
                specimen_name="Epipremnum Aureum",
                care_instructions="Tolerates low light, weekly watering.",
                color_desc="Light green with spots",
                maduration_desc="Vegetative",
                plant_desc="Desk Pothos"
            )
            print("Default plants generated.")
        except Exception as e:
            print(f"Error creating default plants: {e}")
            
    temp_manager.close_database()

    # 1. EXECUTE CONFIGURATION PHASE
    root = tk.Tk()
    app = App(root)
    app.run() 
    
    # 2. PREPARE MONITORING PHASE
    print("\nConfiguration phase closed. Starting monitoring...")
    
    # Clear window for the monitor
    for widget in root.winfo_children():
        widget.destroy()

    manager = PlantManager()
    if db.is_closed():
        manager.initialize_database()

    active_plant_cameras = manager.get_active_plantCameras()

    if not active_plant_cameras:
        print("No active cameras registered. System will terminate.")
        manager.close_database()
        root.destroy()
        exit()

    devices = []
    for plant_camera in active_plant_cameras:
        plant = plant_camera.plant
        camera_id = plant_camera.camera.index
        specimen_data = model_to_dict(manager.get_specimen(plant.specimen.id))
        
        callback = build_callback(manager, plant, specimen_data, camera_id)
        
        cam = CameraDevice(ID=camera_id, state="active", plant=plant)
        interval_seconds = int(plant_camera.observation_interval * 3600)
        if interval_seconds < 5: interval_seconds = 5 
        
        cam.activate_job(interval=interval_seconds, path="temp/", on_photo=callback) 
        devices.append(cam)

    print(f"Loading Carousel for {len(devices)} cameras...")

    # 3. EXECUTE MONITORING CAROUSEL IN THE SAME WINDOW
    carousel = MonitorCarouselWindow(root, devices, manager)
    root.mainloop()

if __name__ == '__main__':
    main()