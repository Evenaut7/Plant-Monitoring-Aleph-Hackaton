from database.models import db, Specimen, Plant, Camera, PlantCamera, Observation
from database.plantManager import PlantManager
from datetime import date
from playhouse.shortcuts import model_to_dict
from pprint import pprint

def initialize_database():
    db.connect()
    db.create_tables([Specimen, Plant, Camera, PlantCamera, Observation], safe=True)

def main():
    initialize_database()
    print("--- Monitoring System Started ---\n")

    manager = PlantManager()

    print("Creating records...")
    my_plant = manager.create_complete_plant(
        specimen_name="Cherry Tomato",
        care_instructions="Lots of water and direct sunlight",
        color_desc="Dark green",
        maduration_desc="Deep red",
        plant_desc="Tomato plant in sector A"
    )
    
    my_camera = manager.register_camera(index=1, state="active")

    print("Assigning camera...")
    manager.assign_camera_to_plant(plant=my_plant, camera=my_camera, interval_hours=2.0)

    print("Registering observation...")
    manager.register_current_observation(
        plant=my_plant,
        health="Excellent",
        phase="Growth",
        color="Vibrant green",
        soil="Moist",
        pests="None",
        tendency="Improving"
    )

    history = manager.get_observation_history(my_plant, date.today())
    plant = manager.get_plant(my_plant)

    print(f"--- {plant.plant_description} History of Today ---")

    for obs in history:
        print(f"[{obs.date_time.strftime('%Y-%m-%d %H:%M:%S')}] (Camera {obs.plant_camera.camera.index})")
        print(f"  - Health: {obs.health_state}")
        print(f"  - Maturation Phase: {obs.maduration_phase}")
        print(f"  - Foliage Color: {obs.foliage_color}")
        print(f"  - Soil: {obs.soil_condition}")
        print(f"  - Pests: {obs.pests}")
        print(f"  - Tendency: {obs.health_tendence}")
        print("-" * 50)

    print("\n--- Testing New Methods ---")

    fetched_plant = manager.get_plant(my_plant.id)
    print("\nFetched Plant:")
    pprint(model_to_dict(fetched_plant))

    fetched_specimen = manager.get_specimen(my_plant.specimen.id)
    print("\nFetched Specimen:")
    pprint(model_to_dict(fetched_specimen))

    print("\nAll Specimens:")
    all_specimens = manager.get_specimens()
    for spec in all_specimens:
        pprint(model_to_dict(spec))

    print("\nActive Cameras:")
    active_cameras = manager.get_active_plantCameras()
    for cam in active_cameras:
        pprint(model_to_dict(cam))

    db.close()



if __name__ == '__main__':
    main()