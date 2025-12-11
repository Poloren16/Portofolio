from ultralytics import YOLO
import cv2

# === DETEKSI REAL-TIME ===
# Pastikan webcam kamu berfungsi

model = YOLO(r'C:\Users\ASUS\dataset\runs\detect\train7\weights\best.pt')

cap = cv2.VideoCapture(0)  # 0 = webcam default

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Jalankan deteksi
    results = model(frame, conf=0.5, show=True)

    # Tekan 'q' untuk keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("✅ Deteksi real-time selesai. Tekan 'q' untuk keluar dari jendela.")
