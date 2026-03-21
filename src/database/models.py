import datetime
from peewee import *

db = SqliteDatabase('database/plant_monitoring.db')

class BaseModel(Model):
    class Meta:
        database = db

class Specimen(BaseModel):
    specimen_name = CharField(unique=True)
    care_instructions = CharField()
    common_color_description = CharField()
    maduration_description = CharField()

class Plant(BaseModel):
    plant_description = CharField(unique=True)
    specimen = ForeignKeyField(Specimen, backref='plants') 

class Camera(BaseModel):
    STATE_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive')
    )
    index = IntegerField(unique=True)
    state = CharField(choices=STATE_CHOICES)    
    
class PlantCamera(BaseModel):
    plant = ForeignKeyField(Plant, backref='camera_assignments')
    camera = ForeignKeyField(Camera, backref='plant_assignments')
    assignament_date = DateTimeField(default=datetime.datetime.now)
    is_active = BooleanField(default=True)
    observation_interval = FloatField() #In Hours 

class Observation(BaseModel):
    plant_camera = ForeignKeyField(PlantCamera, backref='observations')
    health_state = CharField()
    maduration_phase = CharField()
    foliage_color = CharField()
    soil_condition = CharField()
    pests = CharField()
    health_tendence = CharField()
    date_time = DateTimeField(default=datetime.datetime.now)