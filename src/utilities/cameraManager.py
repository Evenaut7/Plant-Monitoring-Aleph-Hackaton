from datetime import datetime
import time
import cv2
import schedule
import threading

class Camera:

    def __init__(self, ID, state):
        self.ID = ID
        self.state = state
        # Create a new VideoCapture object
        self.cam = cv2.VideoCapture(ID)
        self.job = None #Job starts deactivated
        self.scheduler = schedule.Scheduler() #Each instance has its own scheduler

        if not self.cam.isOpened():
            raise RuntimeError(f"Couldn't open camera with ID {ID}")
        else:
            print(f"Camera {ID} opened correctly")

    #Stores a photo taken from the designated camera by index in a designated path
    def take_photo(self, path):

        #Empties the frames in buffer
        for _ in range(5):
            self.cam.grab()
        # Capture one frame
        ret, frame = self.cam.read()

        if not ret or frame is None:
            print("Error: couldn't capture frame")
            return
        # Save frame in designated 'path'
        filepath = path + "temp.png"
        cv2.imwrite(filepath, frame)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Photo stored in {filepath}")

    def release(self):
        self.cam.release()

    #Starts running the secondary thread
    def run_schedule(self):
        while self.running:
            self.scheduler.run_pending()
            time.sleep(1)

    #Takes photos from this camera every {interval} seconds
    def activate_job(self, interval = 5, path = "temp/"):
        if self.job is None:
            #If the camera is not taking pictures, starts job
            self.job = self.scheduler.every(interval).seconds.do(self.take_photo, path=path)
            #Starts a thread to run in the background
            self.running = True
            self.thread = threading.Thread(target=self.run_schedule, daemon=True)
            self.thread.start()
            print("Camera {self.ID}: active capture every {interval} secs")

    #Ends the job that "activate_job" starts
    def deactivate_job(self):
        if self.job is not None:
            #If the camera is taking pictures, ends job
            self.scheduler.cancel_job(self.job)
            self.job = None
            print("Camera {self.ID}: capture deactivated")