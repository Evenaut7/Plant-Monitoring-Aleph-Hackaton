from database.models import db, Specimen, Plant, Camera, PlantCamera, Observation
from database.plantManager import PlantManager
from datetime import date
from playhouse.shortcuts import model_to_dict
from pprint import pprint
from config.groq_assistant import analyze_plant
import json ## checkear

def main():

    manager = PlantManager()
    manager.initialize_database()

    ## Scheduler maneja todo esto

    ## Primero la camara saca foto, las guarda, con eso determinamos que camara le sacó la foto, y con eso determinamos 
    # a que planta corresponde, y con eso determinamos a que espécimen corresponde,
    #  y con eso le damos contexto a analyze_plant para que nos de un análisis más completo de la planta

    fetched_plant = manager.get_plant(1) ## Con el id obtenido por medio de la camara, usamos para obtener info de la planta y su espécimen asociado, para dar contexto a analyze_plant y obtener un análisis más completo de la planta
    print("\nFetched Plant:")
    pprint(model_to_dict(fetched_plant))

    fetched_specimen = manager.get_specimen(fetched_plant.specimen.id) ## usar para dar contexto a analyze_plant
    print("\nFetched Specimen:")
    pprint(model_to_dict(fetched_specimen))

    plant_data = analyze_plant(image_path="images/plant.jpg", context_path="config/groq_context.txt", specimen_data=model_to_dict(fetched_specimen))
    print("\nAnalyzed Plant Data from Groq Assistant:")
    pprint(plant_data)

    ## Aquí podríamos guardar la información obtenida de analyze_plant en la base de datos,
    #  asociada a la planta y al espécimen correspondiente

    manager.close_database()

if __name__ == '__main__':
    main()