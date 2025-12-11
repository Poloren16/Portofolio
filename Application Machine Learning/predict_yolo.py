from ultralytics import YOLO

# === PREDIKSI GAMBAR ===
# Ganti path di bawah sesuai lokasi model dan gambar kamu

model = YOLO(r'C:\Users\ASUS\dataset\runs\detect\train7\weights\best.pt')

results = model.predict(
    source=r'C:\Users\ASUS\dataset\images\bottle.v1i.yolov8\train\images',  # folder gambar
    save=True,    # simpan hasil di folder runs/detect/predict
    show=True     # tampilkan hasil di jendela
)

print("✅ Prediksi selesai! Cek folder runs/detect/predict untuk hasilnya.")
