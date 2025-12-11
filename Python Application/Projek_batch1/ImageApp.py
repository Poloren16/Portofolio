import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog,
    QSlider, QGroupBox, QGridLayout, QMessageBox
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

MAX_HISTORY = 20

def cv_img_to_qpixmap(cv_img):
    """Convert OpenCV image (BGR or Gray) to QPixmap"""
    if cv_img is None:
        return QPixmap()
    if len(cv_img.shape) == 2:
        h, w = cv_img.shape
        bytes_per_line = w
        qimg = QImage(cv_img.data, w, h, bytes_per_line, QImage.Format.Format_Grayscale8)
    else:
        h, w, ch = cv_img.shape
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        bytes_per_line = 3 * w
        qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(qimg.copy())


class ImageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ImageApp - Batch1 (Brightness, Contrast, Blur, Undo/Redo)")
        self.image = None  # current committed image (numpy array BGR)
        self.preview_image = None  # current preview (numpy array BGR)
        self.history = []  # list of numpy arrays
        self.redo_stack = []

        self._init_ui()

    def _init_ui(self):
        # Image display
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(640, 360)
        self.image_label.setStyleSheet("background-color: #222; color: #ddd;")

        # Buttons
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_image)
        save_btn = QPushButton("Save As...")
        save_btn.clicked.connect(self.save_image)
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_image)

        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.undo)
        redo_btn = QPushButton("Redo")
        redo_btn.clicked.connect(self.redo)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(undo_btn)
        btn_layout.addWidget(redo_btn)

        # Sliders group (Adjustments)
        group = QGroupBox("Adjustments (preview realtime; release to commit)")
        grid = QGridLayout()

        # Brightness slider (-100 .. +100)
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.on_adjustment_change)
        self.brightness_slider.sliderReleased.connect(self.commit_preview)

        self.brightness_label = QLabel("Brightness: 0")

        # Contrast slider (10 .. 300 -> 0.1 .. 3.0)
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(10, 300)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self.on_adjustment_change)
        self.contrast_slider.sliderReleased.connect(self.commit_preview)

        self.contrast_label = QLabel("Contrast: 1.00x")

        # Blur slider (1 .. 31 odd only)
        self.blur_slider = QSlider(Qt.Orientation.Horizontal)
        self.blur_slider.setRange(1, 31)
        self.blur_slider.setValue(1)
        self.blur_slider.setSingleStep(2)
        self.blur_slider.valueChanged.connect(self.on_adjustment_change)
        self.blur_slider.sliderReleased.connect(self.commit_preview)

        self.blur_label = QLabel("Blur kernel: 1")

        grid.addWidget(self.brightness_label, 0, 0)
        grid.addWidget(self.brightness_slider, 0, 1)
        grid.addWidget(self.contrast_label, 1, 0)
        grid.addWidget(self.contrast_slider, 1, 1)
        grid.addWidget(self.blur_label, 2, 0)
        grid.addWidget(self.blur_slider, 2, 1)

        group.setLayout(grid)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(group)
        self.setLayout(main_layout)

    # -------------------- Image / history helpers --------------------
    def push_history(self, img):
        if img is None:
            return
        # keep copies as contiguous arrays
        arr = np.copy(img)
        self.history.append(arr)
        # limit history size
        if len(self.history) > MAX_HISTORY:
            self.history.pop(0)
        # clear redo stack on new commit
        self.redo_stack.clear()

    def undo(self):
        if len(self.history) <= 1:
            QMessageBox.information(self, "Undo", "No more undo steps available.")
            return
        # pop current to redo stack, set previous as current
        last = self.history.pop()
        self.redo_stack.append(last)
        self.image = np.copy(self.history[-1])
        self.show_image(self.image)
        # reset sliders to neutral
        self.reset_sliders_preview()

    def redo(self):
        if not self.redo_stack:
            QMessageBox.information(self, "Redo", "No more redo steps available.")
            return
        img = self.redo_stack.pop()
        self.history.append(np.copy(img))
        self.image = np.copy(img)
        self.show_image(self.image)
        self.reset_sliders_preview()

    def reset_sliders_preview(self):
        # reset slider values without emitting commit events
        self.brightness_slider.blockSignals(True)
        self.contrast_slider.blockSignals(True)
        self.blur_slider.blockSignals(True)
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(100)
        self.blur_slider.setValue(1)
        self.brightness_slider.blockSignals(False)
        self.contrast_slider.blockSignals(False)
        self.blur_slider.blockSignals(False)
        self.brightness_label.setText("Brightness: 0")
        self.contrast_label.setText("Contrast: 1.00x")
        self.blur_label.setText("Blur kernel: 1")

    # -------------------- Load / Save / Display --------------------
    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open image", "", "Images (*.png *.jpg *.jpeg *.bmp *.tif)")
        if not path:
            return
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            QMessageBox.critical(self, "Error", "Failed to load image.")
            return
        self.image = img
        self.history = []
        self.redo_stack = []
        self.push_history(self.image)
        self.show_image(self.image)
        self.reset_sliders_preview()

    def save_image(self):
        if self.image is None:
            QMessageBox.information(self, "Save", "No image to save.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save image as", "", "PNG (*.png);;JPEG (*.jpg *.jpeg)")
        if not path:
            return
        # Use imencode + tofile for unicode paths on Windows/Linux compat
        ext = Path(path).suffix.lower()
        success, buf = cv2.imencode(ext if ext else ".png", self.image)
        if success:
            buf.tofile(path)
            QMessageBox.information(self, "Saved", f"Saved to: {path}")
        else:
            QMessageBox.critical(self, "Error", "Failed to save image.")

    def reset_image(self):
        if not self.history:
            return
        self.image = np.copy(self.history[0])
        self.history = [np.copy(self.image)]
        self.redo_stack.clear()
        self.show_image(self.image)
        self.reset_sliders_preview()

    def show_image(self, img):
        pix = cv_img_to_qpixmap(img)
        self.image_label.setPixmap(pix.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    # -------------------- Adjustments (preview & commit) --------------------
    def on_adjustment_change(self, value):
        # Called for realtime preview: apply adjustments to the top-of-history image
        if not self.history:
            return
        base = np.copy(self.history[-1])
        b = self.brightness_slider.value()
        c_val = self.contrast_slider.value()
        contrast = c_val / 100.0  # map 10..300 to 0.1..3.0
        k = self.blur_slider.value()
        # ensure k odd and >=1
        if k % 2 == 0:
            k = k + 1
        self.blur_label.setText(f"Blur kernel: {k}")
        self.brightness_label.setText(f"Brightness: {b}")
        self.contrast_label.setText(f"Contrast: {contrast:.2f}x")

        preview = self.apply_brightness_contrast(base, brightness=b, contrast=contrast)
        if k > 1:
            preview = cv2.GaussianBlur(preview, (k, k), 0)
        self.preview_image = preview
        self.show_image(self.preview_image)

    def commit_preview(self):
        # Commit current preview to history (only if changed)
        if self.preview_image is None:
            return
        # push preview as new committed image
        self.push_history(self.preview_image)
        self.image = np.copy(self.preview_image)
        self.preview_image = None
        # After commit, keep sliders' current values but allow further edits
        # We won't auto-reset sliders here; user can continue adjusting or use Reset button.
        # (Optionally, you may reset sliders to neutral if desired)
        # For better UX, leave them as-is so user can tweak further quickly.

    @staticmethod
    def apply_brightness_contrast(input_img, brightness=0, contrast=1.0):
        """brightness: -100..100, contrast: 0.1..3.0"""
        if input_img is None:
            return None
        img = input_img.astype(np.float32)
        # Apply contrast then brightness: new = img*contrast + brightness
        img = img * contrast + brightness
        img = np.clip(img, 0, 255)
        return img.astype(np.uint8)


if __name__ == '__main__':
    from pathlib import Path
    app = QApplication(sys.argv)
    w = ImageApp()
    w.resize(900, 700)
    w.show()
    sys.exit(app.exec())
