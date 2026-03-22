from datetime import datetime
import time
import cv2
import schedule
import threading

class CameraDevice:
    def __init__(self, ID, state, plant=None):
        self.ID = ID
        self.state = state
        self.plant = plant
        self.plant_name = plant.plant_description if plant else "Unknown Plant"
        self.cam = cv2.VideoCapture(ID, cv2.CAP_DSHOW)
        self.job = None
        self.scheduler = schedule.Scheduler()
        self.running = False
        
        # Shared state with Tkinter
        self.current_frame = None 
        self.latest_analysis_text = "Waiting for the first Groq analysis...\n(It will take a few seconds)"

        if not self.cam.isOpened():
            print(f"Warning: Could not open camera ID {ID}")
        else:
            print(f"Camera {ID} ({self.plant_name}) ready.")

    def _trigger_analysis(self, path, on_photo):
        if self.current_frame is None: return
            
        filepath = f"{path}cam_{self.ID}.png"
        cv2.imwrite(filepath, self.current_frame)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Photo sent for analysis...")
        
        if on_photo:
            try:
                result_data = on_photo(filepath)
                if result_data:
                    self.latest_analysis_text = (
                        f"• Health: {result_data.get('health_state', 'N/A')}\n\n"
                        f"• Phase: {result_data.get('maturation_phase', 'N/A')}\n\n"
                        f"• Color: {result_data.get('foliage_color', 'N/A')}\n\n"
                        f"• Soil: {result_data.get('soil_condition', 'N/A')}\n\n"
                        f"• Pests: {result_data.get('pests', 'N/A')}\n\n"
                        f"• Tendency: {result_data.get('health_tendency', 'N/A')}"
                    )
            except Exception as e:
                print(f"Analysis error (Camera {self.ID}): {e}")

    def activate_job(self, interval=5, path="temp/", on_photo=None):
        if self.job is None:
            def job():
                threading.Thread(target=self._trigger_analysis, args=(path, on_photo), daemon=True).start()

            self.job = self.scheduler.every(interval).seconds.do(job)
            self.running = True
            
            self.video_thread = threading.Thread(target=self._read_video_loop, daemon=True)
            self.video_thread.start()

    def _read_video_loop(self):
        while self.running:
            ret, frame = self.cam.read()
            if ret:
                self.current_frame = frame
            
            self.scheduler.run_pending()
            time.sleep(0.01)

    def get_tkinter_frame(self):
        """Returns the current frame in RGB format for Tkinter"""
        if self.current_frame is not None:
            return cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        return None

    def deactivate_job(self):
        self.running = False
        if self.job is not None:
            self.scheduler.cancel_job(self.job)
            self.job = None

    def release(self):
        self.running = False
        if self.cam.isOpened():
            self.cam.release()