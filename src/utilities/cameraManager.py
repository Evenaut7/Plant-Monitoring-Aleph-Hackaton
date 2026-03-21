from datetime import datetime
import time
import cv2
import schedule
import threading

class CameraDevice:

    def __init__(self, ID, state):
        self.ID = ID
        self.state = state
        
        # ¡Agregamos cv2.CAP_DSHOW aquí!
        self.cam = cv2.VideoCapture(ID, cv2.CAP_DSHOW)
        
        self.job = None 
        self.scheduler = schedule.Scheduler() 

        if not self.cam.isOpened():
            raise RuntimeError(f"Couldn't open camera with ID {ID}")
        else:
            print(f"Camera {ID} opened correctly")

    #Stores a photo taken from the designated camera by index in a designated path
    def take_photo(self, path):
        for _ in range(5):
            self.cam.grab()
        ret, frame = self.cam.read()
        if not ret or frame is None:
            print("Error: couldn't capture frame")
            return None
        filepath = f"{path}cam_{self.ID}.png"
        cv2.imwrite(filepath, frame)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Photo stored in {filepath}")
        return filepath

    def release(self):
        self.cam.release()

    #Starts running the secondary thread
    def run_schedule(self):
        while self.running:
            self.scheduler.run_pending()
            time.sleep(1)

    #Takes photos from this camera every {interval} seconds
    def activate_job(self, interval=5, path="temp/", on_photo=None):
        if self.job is None:
            def job():
                filepath = self.take_photo(path)
                if filepath and on_photo:
                    on_photo(filepath)

            self.job = self.scheduler.every(interval).seconds.do(job)
            self.running = True
            self.thread = threading.Thread(target=self.run_schedule, daemon=True)
            self.thread.start()
            print(f"Camera {self.ID}: active capture every {interval} secs") 

    #Ends the job that "activate_job" starts
    def deactivate_job(self):
        if self.job is not None:
            self.scheduler.cancel_job(self.job)
            self.job = None
            self.running = False
            print(f"Camera {self.ID}: capture deactivated")