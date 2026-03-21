import cv2

def find_available_cameras():
    print("Buscando cámaras conectadas...")
    available_cameras = []
    
    # Probamos los puertos del 0 al 9
    for i in range(10):
        # cv2.CAP_DSHOW a veces ayuda en Windows a que abra más rápido, 
        # pero puedes dejar solo cv2.VideoCapture(i)
        cap = cv2.VideoCapture(i) 
        
        if cap.isOpened():
            print(f"✅ ¡Cámara detectada en el index: {i}!")
            available_cameras.append(i)
            cap.release() # La cerramos para que no quede bloqueada
            
    if not available_cameras:
        print("❌ No se detectó ninguna cámara. Revisa la conexión USB o los permisos de Windows.")
        
    return available_cameras

if __name__ == "__main__":
    find_available_cameras()