from database.models import db, Specimen, Plant, Camera, PlantCamera, Observation
from database.plantManager import PlantManager
from groqConfig.groq_assistant import analyze_plant
from utilities.cameraManager import CameraDevice
from playhouse.shortcuts import model_to_dict
import time
import tkinter as tk
from UI.app import App


def build_callback(manager, plant, specimen_data, camera_id):
    
    def on_photo(image_path):
        # ¡La conexión debe ir AQUÍ ADENTRO para que la abra el hilo secundario!
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

def main():
    manager = PlantManager()
    manager.initialize_database()
    
    manager.create_complete_plant(
        specimen_name="Ficus Elastica",
        care_instructions="Water weekly, indirect sunlight, well-draining soil.",
        color_desc="Dark green glossy leaves",
        maduration_desc="Matures in 2-3 years, can grow up to 10 feet indoors.",
        plant_desc="Large indoor plant with broad leaves."
    )
    manager.create_complete_plant(
        specimen_name="Monstera Deliciosa",
        care_instructions="Water when top inch of soil is dry, bright indirect light.",
        color_desc="Green leaves with natural holes",
        maduration_desc="Matures in 1-2 years, can grow up to 6 feet indoors.",
        plant_desc="Tropical plant with distinctive split leaves."
    )
    manager.register_camera(state="active", index=0) 
    manager.register_camera(state="active", index=1)
    manager.assign_camera_to_plant(
        plant=manager.get_plant_by_description("Large indoor plant with broad leaves."),
        camera=manager.get_camera_by_index(0),
        interval_hours=0.01 
    )
    manager.assign_camera_to_plant(
        plant=manager.get_plant_by_description("Tropical plant with distinctive split leaves."),
        camera=manager.get_camera_by_index(1),
        interval_hours=0.01 
    )
    active_plant_cameras = manager.get_active_plantCameras()

    if not active_plant_cameras:
        print("No active cameras found.")
        manager.close_database()
        return

    devices = []

    for plant_camera in active_plant_cameras:
        plant = plant_camera.plant
        camera_id = plant_camera.camera.index  # 1. Sacamos el ID
        
        specimen_data = model_to_dict(manager.get_specimen(plant.specimen.id))
        
        # 2. ¡Aquí está la corrección! Le pasamos el camera_id al final
        callback = build_callback(manager, plant, specimen_data, camera_id) 
        
        cam = CameraDevice(ID=camera_id, state="active")
        cam.activate_job(
            interval=10,  # 10 seconds for testing
            path="temp/",
            on_photo=callback
        )
        devices.append(cam)
        print(f"Camera {camera_id} activated for plant '{plant.plant_description}'")

    print(f"\n{len(devices)} camera(s) running. Press Ctrl+C to stop.\n")

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
    root = tk.Tk()
    app = App(root)
    app.run()