from .models import db, Specimen, Plant, Camera, PlantCamera, Observation
from peewee import IntegrityError, fn
from datetime import date

class PlantManager:
    def initialize_database(self):
        db.connect()
        db.create_tables([Specimen, Plant, Camera, PlantCamera, Observation], safe=True)

    def close_database(self):
        db.close()

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
        # Usamos get_or_create en lugar de create
        camera, created = Camera.get_or_create(
            index=index,
            defaults={'state': state}
        )
        
        if created:
            print(f"New camera registered with index: {index}")
        else:
            print(f"Using existing camera with index: {index}")
            # Si ya existía pero le pasamos un estado distinto, lo actualizamos
            if camera.state != state:
                camera.state = state
                camera.save()
                
        return camera

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

    def unsign_camera_from_plant(self, plant):
        update_query = PlantCamera.update(is_active=False).where(
            (PlantCamera.plant == plant) & 
            (PlantCamera.is_active == True)
        )
        updated_rows = update_query.execute()
        if updated_rows > 0:
            print(f"Camera successfully unassigned from plant ID {plant.id}.")
        else:
            print(f"No active camera found for plant ID {plant.id} to unassign.")

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
    
    def get_latest_observations(self):
        subquery = (Observation
                    .select(fn.MAX(Observation.id))
                    .join(PlantCamera)
                    .where(PlantCamera.is_active == True)
                    .group_by(Observation.plant_camera))

        latest_obs = (Observation
                      .select(Observation, PlantCamera, Plant)
                      .join(PlantCamera)
                      .join(Plant)
                      .where(Observation.id.in_(subquery)))
        return latest_obs

    def get_plants(self):
        plants = (Plant
                    .select()
                    .join(Specimen)
                    .order_by(Plant.plant_description))
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
    
    def get_last_plantCamera_for_every_plant(self):
        subquery = (PlantCamera
                    .select(fn.MAX(PlantCamera.assignament_date))
                    .group_by(PlantCamera.plant))

        last_plant_cameras = (PlantCamera
                                .select(PlantCamera, Plant)
                                .seleect(PlantCamera, Camera)
                                .join(Plant)
                                .where(PlantCamera.id.in_(subquery)))
        return last_plant_cameras

    def get_active_plantCameras(self):
        return (PlantCamera
                    .select(PlantCamera, Camera, Plant)
                    .join(Camera)
                    .switch(PlantCamera)
                    .join(Plant)
                    .where(PlantCamera.is_active == True))
    
    def get_active_Cameras(self):
        activeCameras = (Camera
                            .select()
                            .join(PlantCamera)
                            .where(PlantCamera.is_active == True))
        return activeCameras
    
    def get_plant_by_camera(self, camera):
        plant_camera = PlantCamera.get_or_none(
            (PlantCamera.camera == camera) & 
            (PlantCamera.is_active == True)
        )
        if plant_camera:
            return plant_camera.plant
        return None
                            
    def get_camera_by_index(self, index):
        camera = Camera.get_or_none(Camera.index == index)
        return camera
    
    def get_plant_by_description(self, description):
        plant = Plant.get_or_none(Plant.plant_description == description)
        return plant

    def delete_plant(self, plant):
        plant.delete_instance(recursive=True)

    def delete_specimen(self, specimen):
        specimen.delete_instance(recursive=True)
    
