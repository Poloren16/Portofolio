import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QSlider, QGroupBox, QGridLayout, QMessageBox, QMenuBar, QMenu
)

from PyQt6.QtGui import QPixmap, QImage, QAction
from PyQt6.QtCore import Qt

MAX_HISTORY = 50

def cv_img_to_qpixmap(cv_img):
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
        self.setWindowTitle("ImageApp - Batch1+2 (Adjustments + Filters)")
        self.image = None  # committed image (numpy BGR)
        self.preview_image = None  # current preview (numpy BGR)
        self.history = []
        self.redo_stack = []

        self._init_ui()

    def _init_ui(self):
        # Menu bar (Filters dropdown)
        self.menubar = QMenuBar(self)
        filters_menu = QMenu("Filters", self)
        # Add filter actions
        sepia_act = QAction("Sepia (Preview)", self)
        sepia_act.triggered.connect(lambda: self.preview_filter("sepia"))
        neg_act = QAction("Negative / Invert (Preview)", self)
        neg_act.triggered.connect(lambda: self.preview_filter("negative"))
        sharp_soft_act = QAction("Sharpen (Soft) (Preview)", self)
        sharp_soft_act.triggered.connect(lambda: self.preview_filter("sharpen_soft"))
        sharp_strong_act = QAction("Sharpen (Strong) (Preview)", self)
        sharp_strong_act.triggered.connect(lambda: self.preview_filter("sharpen_strong"))
        cartoon_act = QAction("Cartoon (Preview)", self)
        cartoon_act.triggered.connect(lambda: self.preview_filter("cartoon"))
        auto_act = QAction("Auto Enhance (Preview)", self)
        auto_act.triggered.connect(lambda: self.preview_filter("auto_enhance"))

        filters_menu.addAction(sepia_act)
        filters_menu.addAction(neg_act)
        filters_menu.addSeparator()
        filters_menu.addAction(sharp_soft_act)
        filters_menu.addAction(sharp_strong_act)
        filters_menu.addSeparator()
        filters_menu.addAction(cartoon_act)
        filters_menu.addSeparator()
        filters_menu.addAction(auto_act)
        self.menubar.addMenu(filters_menu)

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

        # Apply / Cancel for previews
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setEnabled(False)
        self.apply_btn.clicked.connect(self.apply_preview_filter)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_preview_filter)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(undo_btn)
        btn_layout.addWidget(redo_btn)
        btn_layout.addSpacing(10)
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.cancel_btn)

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
        main_layout.setMenuBar(self.menubar)
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(group)
        self.setLayout(main_layout)

    # -------------------- Image / history helpers --------------------
    def push_history(self, img):
        if img is None:
            return
        arr = np.copy(img)
        self.history.append(arr)
        if len(self.history) > MAX_HISTORY:
            self.history.pop(0)
        self.redo_stack.clear()

    def undo(self):
        if len(self.history) <= 1:
            QMessageBox.information(self, "Undo", "No more undo steps available.")
            return
        last = self.history.pop()
        self.redo_stack.append(last)
        self.image = np.copy(self.history[-1])
        self.show_image(self.image)
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
        from pathlib import Path
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
        if not self.history:
            return
        base = np.copy(self.history[-1])
        b = self.brightness_slider.value()
        c_val = self.contrast_slider.value()
        contrast = c_val / 100.0
        k = self.blur_slider.value()
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
        # when adjustments produce preview, we disable Apply/Cancel for filter previews
        self.apply_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)

    def commit_preview(self):
        if self.preview_image is None:
            return
        self.push_history(self.preview_image)
        self.image = np.copy(self.preview_image)
        self.preview_image = None

    # -------------------- Filter preview / apply / cancel --------------------
    def preview_filter(self, name):
        if not self.history:
            return
        base = np.copy(self.history[-1])
        # produce preview based on filter name
        if name == "sepia":
            out = self.filter_sepia(base)
        elif name == "negative":
            out = self.filter_negative(base)
        elif name == "sharpen_soft":
            out = self.filter_sharpen(base, strength="soft")
        elif name == "sharpen_strong":
            out = self.filter_sharpen(base, strength="strong")
        elif name == "cartoon":
            out = self.filter_cartoon(base)
        elif name == "auto_enhance":
            out = self.filter_auto_enhance(base)
        else:
            return
        self.preview_image = out
        self.show_image(self.preview_image)
        # enable Apply/Cancel buttons for filter previews
        self.apply_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)

    def apply_preview_filter(self):
        if self.preview_image is None:
            return
        self.push_history(self.preview_image)
        self.image = np.copy(self.preview_image)
        self.preview_image = None
        self.apply_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        # reset sliders to neutral so adjustments start fresh after filter
        self.reset_sliders_preview()

    def cancel_preview_filter(self):
        # drop preview and show current committed image
        self.preview_image = None
        if self.history:
            self.show_image(self.history[-1])
        self.apply_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)

    # -------------------- Filter implementations --------------------
    @staticmethod
    def filter_sepia(img):
        """Apply sepia tone"""
        if img is None:
            return None
        imgf = img.astype(np.float32)
        # sepia matrix (BGR input -> BGR output)
        sepia_mat = np.array([[0.272, 0.534, 0.131],
                              [0.349, 0.686, 0.168],
                              [0.393, 0.769, 0.189]], dtype=np.float32)
        # convert BGR to RGB order for matrix multiply convenience, then back
        rgb = cv2.cvtColor(imgf, cv2.COLOR_BGR2RGB)
        sepia_rgb = cv2.transform(rgb, sepia_mat)
        sepia_rgb = np.clip(sepia_rgb, 0, 255).astype(np.uint8)
        sepia_bgr = cv2.cvtColor(sepia_rgb, cv2.COLOR_RGB2BGR)
        return sepia_bgr

    @staticmethod
    def filter_negative(img):
        if img is None:
            return None
        return cv2.bitwise_not(img)

    @staticmethod
    def filter_sharpen(img, strength="soft"):
        if img is None:
            return None
        if strength == "soft":
            # mild sharpening (unsharp mask style)
            blur = cv2.GaussianBlur(img, (0,0), sigmaX=1.0)
            img_float = img.astype(np.float32)
            mask = img_float - blur.astype(np.float32)
            result = img_float + 0.7 * mask  # factor controls sharpness
            result = np.clip(result, 0, 255).astype(np.uint8)
            return result
        else:
            # stronger sharpen kernel
            kernel = np.array([[0, -1, 0],
                               [-1, 5, -1],
                               [0, -1, 0]], dtype=np.float32)
            res = cv2.filter2D(img, -1, kernel)
            return np.clip(res, 0, 255).astype(np.uint8)

    @staticmethod
    def filter_cartoon(img):
        if img is None:
            return None
        # downscale for speed
        img_small = cv2.pyrDown(img)
        # bilateral filter multiple times for smoothing while preserving edges
        for _ in range(5):
            img_small = cv2.bilateralFilter(img_small, d=9, sigmaColor=75, sigmaSpace=75)
        img_up = cv2.pyrUp(img_small)
        # Edge detection on grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(edges, 255,
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY,
                                      blockSize=9, C=2)
        # combine edges with color
        color = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        cartoon = cv2.bitwise_and(color, edges_colored)
        return cartoon

    @staticmethod
    def filter_auto_enhance(img):
        if img is None:
            return None
        # Use CLAHE on L channel in LAB color space for local contrast enhancement
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        lab_cl = cv2.merge((cl, a, b))
        enhanced = cv2.cvtColor(lab_cl, cv2.COLOR_LAB2BGR)
        # mild color balance: simple scaling by histogram stretching per channel
        result = np.zeros_like(enhanced)
        for ch in range(3):
            channel = enhanced[:,:,ch]
            lo, hi = np.percentile(channel, (1, 99))
            if hi - lo > 0:
                stretch = np.clip((channel - lo) * (255.0 / (hi - lo)), 0, 255).astype(np.uint8)
            else:
                stretch = channel
            result[:,:,ch] = stretch
        return result

    # -------------------- Utility: brightness/contrast --------------------
    @staticmethod
    def apply_brightness_contrast(input_img, brightness=0, contrast=1.0):
        if input_img is None:
            return None
        img = input_img.astype(np.float32)
        img = img * contrast + brightness
        img = np.clip(img, 0, 255)
        return img.astype(np.uint8)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ImageApp()
    w.resize(1000, 760)
    w.show()
    sys.exit(app.exec())
