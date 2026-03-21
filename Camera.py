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

        if not self.cam.isOpened():
            raise RuntimeError(f"No se pudo abrir la cámara con índice {ID}")
        else:
            print(f"Cámara {ID} abierta correctamente")

    # Displays a real time video from the designated camera by index
    """
    def real_time_display(self):
        # Create a new VideoCapture object
        cam = cv2.VideoCapture(self.ID)

        # Initialise variables to store current time difference as well as previous time call value
        previous = time()
        delta = 0

        # Keep looping
        while True:
        # Get the current time, increase delta and update the previous variable
            current = time()
            delta += current - previous
            previous = current

            # Check if 3 (or some other value) seconds passed
            if delta > 3:
                # Operations on image
                # Reset the time counter
                delta = 0

            # Show the image and keep streaming
            _, img = cam.read()
            cv2.imshow("Frame", img)
            cv2.waitKey(1)
    """

    #Stores a photo taken from the designated camera by index in a designated path
    def take_photo(self, path):

        # Capture one frame
        ret, frame = self.cam.read()

        if not ret or frame is None:
            print("Error: no se pudo capturar el frame")
            return
        # Save frame in designated 'path'
        filepath = path + "temp.png"
        cv2.imwrite(filepath, frame)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Foto guardada en {filepath}")

    def release(self):
        self.cam.release()

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

camara = Camera(1, True)

schedule.every(5).seconds.do(camara.take_photo, path = "test/")

# Only the secondary thread runs scheduler
thread = threading.Thread(target=run_schedule, daemon=True)
thread.start()

print("Scheduler corriendo. Presioná Ctrl+C para salir.")
try:
    while True:
        time.sleep(1)  # ← ya no llama a run_pending() acá
except KeyboardInterrupt:
    print("Cerrando...")
    camara.release()