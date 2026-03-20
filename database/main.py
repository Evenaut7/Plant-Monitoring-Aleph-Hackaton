from models import db, Specimen, Plant, Camera, PlantCamera, Observation
from use_cases import (create_complete_plant, register_camera, 
                       assign_camera_to_plant, register_current_observation, 
                       get_observation_history)

def initialize_database():
    """Connects to the DB and creates the tables if they don't exist."""
    db.connect()
    db.create_tables([Specimen, Plant, Camera, PlantCamera, Observation], safe=True)

def main():
    initialize_database()
    print("--- Monitoring System Started ---\n")

    # 1. Create test data using the use cases
    print("Creating records...")
    my_plant = create_complete_plant(
        specimen_name="Cherry Tomato",
        care_instructions="Lots of water and direct sunlight",
        color_desc="Dark green",
        maduration_desc="Deep red",
        plant_desc="Tomato plant in sector A"
    )
    
    # We added the 'index' field to match your updated Camera model!
    my_camera = register_camera(index=1, state="active")

    # 2. Assign the camera
    print("Assigning camera...")
    assign_camera_to_plant(plant=my_plant, camera=my_camera, interval_hours=2.0)

    # 3. Register an observation
    print("Registering observation...")
    register_current_observation(
        plant=my_plant,
        health="Excellent",
        phase="Growth",
        color="Vibrant green",
        soil="Moist",
        pests="None",
        tendency="Improving"
    )

    # 4. Check the history
    print("\n--- Plant History ---")
    history = get_observation_history(my_plant)
    
    for obs in history:
        # Notice we are printing the camera's index now
        print(f"Date: {obs.date_time.strftime('%Y-%m-%d %H:%M:%S')} | Health: {obs.health_state} | Camera Index: {obs.plant_camera.camera.index}")

    db.close()

if __name__ == '__main__':
    main()