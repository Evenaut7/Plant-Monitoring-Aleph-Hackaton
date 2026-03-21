from models import Specimen, Plant, Camera, PlantCamera, Observation
from peewee import IntegrityError
from datetime import date

class PlantManager:
    def create_complete_plant(self, specimen_name, care_instructions, color_desc, maduration_desc, plant_desc):
        specimen, created = Specimen.get_or_create(
            specimen_name=specimen_name,
            defaults={
                'care_instructions': care_instructions,
                'common_color_description': color_desc,
                'maduration_description': maduration_desc
            }
        )
        
        if created:
            print(f"New specimen registered: {specimen_name}")
        else:
            print(f"Using existing specimen: {specimen_name}")

        try:
            new_plant = Plant.create(
                plant_description=plant_desc,
                specimen=specimen
            )
            print(f"Plant successfully created: {plant_desc}")
            return new_plant
            
        except IntegrityError:
            print(f"ERROR! A plant with the description '{plant_desc}' is already registered.")
            
            existing_plant = Plant.get(Plant.plant_description == plant_desc)
            return existing_plant

    def register_camera(self, state, index):
        return Camera.create(state=state, index=index)

    def assign_camera_to_plant(self, plant, camera, interval_hours):
        deactivate_query = PlantCamera.update(is_active=False).where(
            (PlantCamera.plant == plant) & 
            (PlantCamera.is_active == True)
        )
        deactivate_query.execute()

        new_assignment = PlantCamera.create(
            plant=plant,
            camera=camera,
            observation_interval=interval_hours,
            is_active=True
        )
        return new_assignment

    def register_current_observation(self, plant, health, phase, color, soil, pests, tendency):
        active_assignment = PlantCamera.get_or_none(
            (PlantCamera.plant == plant) & 
            (PlantCamera.is_active == True)
        )

        if not active_assignment:
            print(f"Error: Plant ID {plant.id} does not have an active camera assigned.")
            return None

        new_obs = Observation.create(
            plant_camera=active_assignment,
            health_state=health,
            maduration_phase=phase,
            foliage_color=color,
            soil_condition=soil,
            pests=pests,
            health_tendence=tendency
        )
        return new_obs

    def get_observation_history(self, plant, fromDate = date.min):
        observations = (Observation
                          .select()
                          .join(PlantCamera)
                          .join(Plant)
                          .where(Plant.id == plant.id)
                          .where(Observation.date_time > fromDate)
                          .order_by(Observation.date_time.desc())) 
        return observations

    def get_plants(self):
        plants = (Plant
                    .select()
                    .join(Specimen)
                    .order_by(Plant.name))
        return plants
    
    def get_plant(self, idPlant):
        plant = Plant.get_or_none(idPlant)
        return plant
    
    def get_specimen(self, idSpecimen):
        specimen = Specimen.get_or_none(idSpecimen)
        return specimen
    
    def get_specimens(self):
        specimens = Specimen.select()
        return specimens
    
    def get_active_plantCameras(self):
        activeCameras = (Camera
                            .select()
                            .join(PlantCamera)
                            .where(PlantCamera.is_active == True))
        return activeCameras
                            