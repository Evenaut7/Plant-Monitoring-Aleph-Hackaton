from database.models import db, Specimen, Plant, Camera, PlantCamera, Observation
from database.plantManager import PlantManager
from playhouse.shortcuts import model_to_dict
from groqConfig.groq_assistant import analyze_plant
from utilities.cameraManager import CameraDevice
import time

def build_callback(manager, plant, specimen_data):
    def on_photo(image_path):
        try:
            plant_data = analyze_plant(
                image_path=image_path,
                context_path="config/groq_context.txt",
                specimen_data=specimen_data
            )
            manager.register_current_observation(
                plant=plant,
                health=plant_data["health_state"],
                phase=plant_data["maturation_phase"],
                color=plant_data["foliage_color"],
                soil=plant_data["soil_condition"],
                pests=plant_data["pests"],
                tendency=plant_data["health_tendency"]
            )
            print(f"[Plant {plant.id}] Observation saved: {plant_data}")
        except Exception as e:
            print(f"[Plant {plant.id}] Error during analysis: {e}")
    return on_photo

def main():
    manager = PlantManager()
    manager.initialize_database()

    active_plant_cameras = manager.get_active_plantCameras()

    if not active_plant_cameras:
        print("No active cameras found.")
        manager.close_database()
        return

    devices = []

    for plant_camera in active_plant_cameras:
        plant = plant_camera.plant
        specimen_data = model_to_dict(manager.get_specimen(plant.specimen.id))
        callback = build_callback(manager, plant, specimen_data)
        ## plant_camera.observation_interval * 3600 esto va en interval, pero para pruebas lo dejo en 10 segundos
        cam = CameraDevice(ID=plant_camera.camera.index, state="active")
        cam.activate_job(
            interval=10,  # 10 seconds for testing
            path="temp/",
            on_photo=callback
        )
        devices.append(cam)
        print(f"Camera {plant_camera.camera.index} activated for plant '{plant.plant_description}'")

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
    main()