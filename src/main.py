from database.models import db, Specimen, Plant, Camera, PlantCamera, Observation
from database.plantManager import PlantManager
from groqConfig.groq_assistant import analyze_plant
from utilities.cameraManager import CameraDevice
from playhouse.shortcuts import model_to_dict
import time
import threading
import tkinter as tk
from UI.app import App


def build_callback(manager, plant, specimen_data, camera_id):
    def on_photo(image_path):
        if db.is_closed():
            db.connect()
        try:
            print(f"[Camera {camera_id}] Analyzing photo for Plant {plant.id}...")
            plant_data = analyze_plant(
                image_path=image_path,
                context_path="groqConfig/groq_context.txt",
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
            print(f"[Camera {camera_id} - Plant {plant.id}] Observation saved: {plant_data}")
        except Exception as e:
            print(f"[Camera {camera_id} - Plant {plant.id}] Error during analysis: {e}")
        finally:
            if not db.is_closed():
                db.close()
    return on_photo


def start_monitoring():
    manager = PlantManager()
    manager.initialize_database()

    active_plant_cameras = manager.get_active_plantCameras()

    if not active_plant_cameras:
        print("No active cameras found. Monitoring not started.")
        manager.close_database()
        return

    devices = []
    for plant_camera in active_plant_cameras:
        plant = plant_camera.plant
        camera_id = plant_camera.camera.index
        specimen_data = model_to_dict(manager.get_specimen(plant.specimen.id))
        callback = build_callback(manager, plant, specimen_data, camera_id)

        cam = CameraDevice(ID=camera_id, state="active")
        cam.activate_job(
            interval=plant_camera.observation_interval * 3600,
            path="temp/",
            on_photo=callback
        )
        devices.append(cam)
        print(f"Camera {camera_id} activated for plant '{plant.plant_description}'")

    print(f"\n{len(devices)} camera(s) running in background.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        for cam in devices:
            cam.deactivate_job()
            cam.release()
        manager.close_database()
        print("System stopped.")


if __name__ == '__main__':
    # 1. Corre la UI — bloquea hasta que se cierra la ventana
    root = tk.Tk()
    app = App(root)
    app.run()

    # 2. UI cerrada — arranca monitoreo en segundo plano
    print("UI closed. Starting monitoring...")
    monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
    monitor_thread.start()

    # 3. Mantiene el proceso vivo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("System stopped.")