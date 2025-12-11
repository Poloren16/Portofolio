from ultralytics import YOLO
import cv2
import time

# === 1. Load model hasil training ===
model = YOLO(r"C:\Users\ASUS\dataset\runs\detect\train7\weights\best.pt")

# === 2. Inisialisasi kamera ===
cap = cv2.VideoCapture(0)  # gunakan 0 untuk webcam utama
if not cap.isOpened():
    print("❌ Gagal membuka kamera.")
    exit()

# === 3. Siapkan penulisan video output ===
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # codec mp4
timestamp = time.strftime("%Y%m%d-%H%M%S")
output_path = f"output_detection_{timestamp}.mp4"
out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))

print("🎥 Mulai deteksi real-time. Tekan 'q' untuk keluar.")

# === 4. Loop pengambilan frame ===
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Tidak dapat membaca frame dari kamera.")
        break

    # Jalankan deteksi
    results = model(frame, stream=True)

    # Tampilkan hasil deteksi di layar
    for r in results:
        annotated_frame = r.plot()  # frame dengan bounding box
        cv2.imshow("YOLOv8 Real-Time Bottle Detection", annotated_frame)
        out.write(annotated_frame)

    # Tekan 'q' untuk berhenti
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# === 5. Bersihkan semua resource ===
cap.release()
out.release()
cv2.destroyAllWindows()
print(f"✅ Video disimpan sebagai: {output_path}")
