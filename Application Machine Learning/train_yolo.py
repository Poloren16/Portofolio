from ultralytics import YOLO

# === TRAIN YOLO MODEL ===
# Pastikan file dataset.yaml berada di folder yang sama dengan script ini
# dan sudah mengarah ke folder train/valid yang benar

model = YOLO('yolov8n.pt')  # model dasar

model.train(
    data='dataset.yaml',  # file konfigurasi dataset
    epochs=50,            # jumlah epoch
    imgsz=320,            # ukuran gambar
    batch=8,              # ukuran batch
    device='cpu'          # jika ada GPU, bisa ganti 'cuda'
)

print("Training selesai! Model disimpan di folder runs/detect/trainX/weights/best.pt")
