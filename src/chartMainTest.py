from database.models import Specimen, Plant, Camera, PlantCamera, Observation
from database.plantManager import PlantManager
from utilities.chartManager import ChartManager
from datetime import timedelta
import datetime

def main():
    manager = PlantManager()
    manager.initialize_database()

    plant1 = manager.create_complete_plant("Cherry Tomato", "Direct sunlight", "Green", "Red", "Tomato in Sector Arroyito")
    plant2 = manager.create_complete_plant("Basil", "Moderate water", "Light Green", "Dark Green", "Basil in Sector UTN")
    plant3 = manager.create_complete_plant("Bell Pepper", "Warm climate", "Green", "Yellow", "Pepper in Sector A")
    plant4 = manager.create_complete_plant("Lettuce", "Lots of water", "Light Green", "Green", "Lettuce in Sector B")

    cam1 = manager.register_camera("active", 1)
    cam2 = manager.register_camera("active", 2)
    cam3 = manager.register_camera("active", 3)
    cam4 = manager.register_camera("active", 4)

    manager.assign_camera_to_plant(plant1, cam1, 2.0)
    manager.assign_camera_to_plant(plant2, cam2, 4.0)
    manager.assign_camera_to_plant(plant3, cam3, 6.0)
    manager.assign_camera_to_plant(plant4, cam4, 1.0)

    health_states = ["Poor", "Fair", "Good", "Excellent"]
    for i, state in enumerate(health_states):
        obs = manager.register_current_observation(plant1, state, "Growth", "Green", "Moist", "None", "Improving")
        if obs:
            obs.date_time = datetime.datetime.now() - timedelta(days=(3 - i))
            obs.save()

    manager.register_current_observation(plant2, "Good", "Seedling", "Light Green", "Dry", "None", "Stable")
    manager.register_current_observation(plant3, "Poor", "Vegetative", "Yellowish", "Waterlogged", "Aphids", "Declining")
    manager.register_current_observation(plant4, "Excellent", "Harvest", "Vibrant Green", "Moist", "None", "Stable")

    all_plants = manager.get_plants()
    tomato_history = manager.get_observation_history(plant1)
    latest_observations = manager.get_latest_observations()

    ChartManager.plot_health_evolution(tomato_history, plant1.plant_description)
    ChartManager.plot_specimen_inventory(all_plants)
    ChartManager.plot_current_health_pie(latest_observations)
    ChartManager.plot_pests_incidence(latest_observations)
    ChartManager.plot_soil_vs_health(latest_observations)

    manager.close_database()

if __name__ == '__main__':
    main()