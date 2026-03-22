from datetime import datetime
import time
import cv2
import schedule
import threading

class CameraDevice:
    def __init__(self, ID, state, plant_name="Unknown Plant"):
        self.ID = ID
        self.state = state
        self.plant_name = plant_name
        self.cam = cv2.VideoCapture(ID, cv2.CAP_DSHOW)
        self.job = None
        self.scheduler = schedule.Scheduler()
        self.running = False
        self.latest_analysis_text = "Waiting for first analysis..." # Estado compartido
        self.current_frame = None

        if not self.cam.isOpened():
            raise RuntimeError(f"Couldn't open camera with ID {ID}")
        else:
            print(f"Camera {ID} opened correctly")

    def _trigger_analysis(self, path, on_photo):
        """Función interna que corre en un hilo separado para no congelar el video"""
        if self.current_frame is None:
            return
            
        filepath = f"{path}cam_{self.ID}.png"
        cv2.imwrite(filepath, self.current_frame)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Photo stored for analysis")
        
        # Ejecutamos el callback (Groq)
        if on_photo:
            try:
                # Asumimos que el callback devuelve el dict con los datos
                result_data = on_photo(filepath) 
                if result_data:
                    # Actualizamos el texto que se dibuja en pantalla
                    self.latest_analysis_text = (
                        f"Health: {result_data.get('health_state', 'N/A')} | "
                        f"Phase: {result_data.get('maturation_phase', 'N/A')}\n"
                        f"Pests: {result_data.get('pests', 'N/A')} | "
                        f"Trend: {result_data.get('health_tendency', 'N/A')}"
                    )
            except Exception as e:
                print(f"Callback error on Camera {self.ID}: {e}")

    def activate_job(self, interval=5, path="temp/", on_photo=None):
        if self.job is None:
            # En lugar de bloquear, lanzamos el análisis en un hilo secundario
            def job():
                threading.Thread(target=self._trigger_analysis, args=(path, on_photo), daemon=True).start()

            self.job = self.scheduler.every(interval).seconds.do(job)
            self.running = True
            
            # Iniciamos el bucle principal de video
            self.thread = threading.Thread(target=self._video_loop, daemon=True)
            self.thread.start()
            print(f"Camera {self.ID}: active capture every {interval} secs")

    def _video_loop(self):
        """Bucle infinito que lee la cámara y dibuja la interfaz en vivo"""
        window_name = f"Live Monitor - Camera {self.ID} ({self.plant_name})"
        
        while self.running:
            ret, frame = self.cam.read()
            if not ret:
                continue
                
            self.current_frame = frame.copy() # Guardamos copia limpia para el análisis
            
            # --- DIBUJAR INTERFAZ (HUD) ---
            # Fondo negro semitransparente para el texto
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (frame.shape[1], 80), (0, 0, 0), -1)
            frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
            
            # Dibujar el nombre de la planta
            cv2.putText(frame, f"Plant: {self.plant_name}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Dibujar el último análisis (dividimos por saltos de línea)
            y0, dy = 55, 20
            for i, line in enumerate(self.latest_analysis_text.split('\n')):
                y = y0 + i * dy
                cv2.putText(frame, line, (10, y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Mostrar cuadro
            cv2.imshow(window_name, frame)
            
            # Procesar eventos de ventana y scheduler
            self.scheduler.run_pending()
            
            # Si presiona 'q', cerramos esta cámara
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break
                
        cv2.destroyWindow(window_name)

    def deactivate_job(self):
        self.running = False
        if self.job is not None:
            self.scheduler.cancel_job(self.job)
            self.job = None
        print(f"Camera {self.ID}: capture deactivated")

    def release(self):
        self.running = False
        if self.cam.isOpened():
            self.cam.release()