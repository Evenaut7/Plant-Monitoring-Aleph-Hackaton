import tkinter as tk
from tkinter import ttk, messagebox
from database.plantManager import PlantManager
import cv2

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Plant Monitoring System")
        self.root.geometry("600x500")
        self.manager = PlantManager()
        self.manager.initialize_database()
        self._build_ui()
        self._refresh_all()

    def _build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_cameras = tk.Frame(self.notebook, padx=15, pady=15)
        self.tab_create  = tk.Frame(self.notebook, padx=15, pady=15)
        self.tab_plants  = tk.Frame(self.notebook, padx=15, pady=15)

        self.notebook.add(self.tab_cameras, text="  Cameras  ")
        self.notebook.add(self.tab_create,  text="  Create Plant  ")
        self.notebook.add(self.tab_plants,  text="  Registered Plants  ")

        self._build_cameras_section()
        self._build_create_plant_section()
        self._build_plants_section()

    # ─── TAB 1: Cámaras ───────────────────────────────────────────────────────
    def _build_cameras_section(self):
        tk.Label(self.tab_cameras, text="Detected Cameras", font=("Arial", 12, "bold")).pack(anchor="w")

        self.camera_listbox = tk.Listbox(self.tab_cameras, height=6)
        self.camera_listbox.pack(fill=tk.X, pady=5)

        tk.Label(self.tab_cameras, text="Assign to plant:").pack(anchor="w")
        self.plant_var = tk.StringVar()
        self.plant_dropdown = ttk.Combobox(self.tab_cameras, textvariable=self.plant_var, state="readonly")
        self.plant_dropdown.pack(fill=tk.X, pady=5)

        tk.Label(self.tab_cameras, text="Interval (hours):").pack(anchor="w")
        self.interval_entry = tk.Entry(self.tab_cameras)
        self.interval_entry.insert(0, "0.00278")
        self.interval_entry.pack(fill=tk.X, pady=5)

        tk.Button(self.tab_cameras, text="Assign Camera", command=self._assign_camera).pack(fill=tk.X, pady=5)
        tk.Button(self.tab_cameras, text="Refresh Cameras", command=self._detect_cameras).pack(fill=tk.X)

    # ─── TAB 2: Crear planta ──────────────────────────────────────────────────
    def _build_create_plant_section(self):
        tk.Label(self.tab_create, text="Create Plant", font=("Arial", 12, "bold")).pack(anchor="w")

        fields = [
            ("Specimen name",     "entry_specimen"),
            ("Care instructions", "entry_care"),
            ("Common color",      "entry_color"),
            ("Maturation desc",   "entry_maduration"),
            ("Plant description", "entry_plant_desc"),
        ]

        for label, attr in fields:
            tk.Label(self.tab_create, text=label).pack(anchor="w")
            entry = tk.Entry(self.tab_create)
            entry.pack(fill=tk.X, pady=2)
            setattr(self, attr, entry)

        tk.Button(self.tab_create, text="Create Plant", command=self._create_plant).pack(fill=tk.X, pady=10)

    # ─── TAB 3: Plantas registradas ───────────────────────────────────────────
    def _build_plants_section(self):
        tk.Label(self.tab_plants, text="Registered Plants", font=("Arial", 12, "bold")).pack(anchor="w")

        self.plants_listbox = tk.Listbox(self.tab_plants, height=15)
        self.plants_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        tk.Button(self.tab_plants, text="Refresh Plants", command=self._refresh_plants).pack(fill=tk.X)

    # ─── LÓGICA ───────────────────────────────────────────────────────────────
    def _detect_cameras(self):
        self.camera_listbox.delete(0, tk.END)
        self.detected_cameras = []
        for i in range(5):
            cam = cv2.VideoCapture(i)
            if cam.isOpened():
                self.camera_listbox.insert(tk.END, f"Camera index {i}")
                self.detected_cameras.append(i)
                cam.release()
        if not self.detected_cameras:
            self.camera_listbox.insert(tk.END, "No cameras found")

    def _assign_camera(self):
        selected = self.camera_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Select a camera first.")
            return
        if not self.plant_var.get():
            messagebox.showwarning("Warning", "Select a plant first.")
            return
        try:
            interval = float(self.interval_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Interval must be a number.")
            return

        camera_index = self.detected_cameras[selected[0]]
        plant_desc = self.plant_var.get()
        plant = next((p for p in self.manager.get_plants() if p.plant_description == plant_desc), None)

        if plant:
            camera = self.manager.register_camera(index=camera_index, state="active")
            self.manager.assign_camera_to_plant(plant=plant, camera=camera, interval_hours=interval)
            messagebox.showinfo("Success", f"Camera {camera_index} assigned to '{plant_desc}'")
            self._refresh_all()

    def _create_plant(self):
        fields = {
            "specimen":   self.entry_specimen.get(),
            "care":       self.entry_care.get(),
            "color":      self.entry_color.get(),
            "maduration": self.entry_maduration.get(),
            "desc":       self.entry_plant_desc.get(),
        }
        if not all(fields.values()):
            messagebox.showwarning("Warning", "All fields are required.")
            return
        self.manager.create_complete_plant(
            specimen_name=fields["specimen"],
            care_instructions=fields["care"],
            color_desc=fields["color"],
            maduration_desc=fields["maduration"],
            plant_desc=fields["desc"]
        )
        messagebox.showinfo("Success", f"Plant '{fields['desc']}' created.")
        self._refresh_all()

    def _refresh_plants(self):
        self.plants_listbox.delete(0, tk.END)
        plants = self.manager.get_plants()
        plant_names = []
        for plant in plants:
            active = any(pc.is_active for pc in plant.camera_assignments)
            status = "[ON]" if active else "[OFF]"
            self.plants_listbox.insert(tk.END, f"{status} [{plant.id}] {plant.plant_description}")
            plant_names.append(plant.plant_description)
        self.plant_dropdown["values"] = plant_names

    def _refresh_all(self):
        self._detect_cameras()
        self._refresh_plants()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        self.manager.close_database()
        self.root.destroy()