# ImageApp.py (Merged Batch1+2+3)
import sys, os
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog,
    QSlider, QGroupBox, QGridLayout, QMessageBox, QMenuBar, QMenu, QDialog,
    QFormLayout, QLineEdit, QDialogButtonBox, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QVBoxLayout as QVBoxLayoutAlias
)
from PyQt6.QtGui import QPixmap, QImage, QAction
from PyQt6.QtCore import Qt, QRectF

MAX_HISTORY = 100

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

class ImageView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._zoom = 0
        self._empty = True

    def setPhoto(self, pixmap=None):
        scene = QGraphicsScene(self)
        self.setScene(scene)
        if pixmap is None or pixmap.isNull():
            self._empty = True
            return
        self._empty = False
        item = QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        self.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom = 0

    def wheelEvent(self, event):
        if self._empty:
            return
        angle = event.angleDelta().y()
        factor = 1.25 if angle > 0 else 0.8
        self._zoom += 1 if angle > 0 else -1
        if self._zoom > 40:
            self._zoom = 40
            return
        if self._zoom < -40:
            self._zoom = -40
            return
        self.scale(factor, factor)

class FilterPreviewDialog(QDialog):
    """Dialog that shows a preview image and returns whether user applied it."""
    def __init__(self, parent=None, pixmap=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Preview")
        self.result_apply = False
        v = QVBoxLayout(self)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if pixmap is not None:
            self.label.setPixmap(pixmap.scaled(900,700, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        v.addWidget(self.label)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.on_apply)
        btns.rejected.connect(self.reject)
        v.addWidget(btns)

    def on_apply(self):
        self.result_apply = True
        self.accept()

class NumericCropDialog(QDialog):
    def __init__(self, parent=None, img_shape=None):
        super().__init__(parent)
        self.setWindowTitle("Crop (manual input)")
        layout = QFormLayout(self)
        self.x_in = QLineEdit("0")
        self.y_in = QLineEdit("0")
        self.w_in = QLineEdit(str(img_shape[1] if img_shape is not None else 100))
        self.h_in = QLineEdit(str(img_shape[0] if img_shape is not None else 100))
        layout.addRow("X:", self.x_in)
        layout.addRow("Y:", self.y_in)
        layout.addRow("Width:", self.w_in)
        layout.addRow("Height:", self.h_in)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def getValues(self):
        try:
            x = int(self.x_in.text())
            y = int(self.y_in.text())
            w = int(self.w_in.text())
            h = int(self.h_in.text())
            return x, y, w, h
        except:
            return None

class ResizeDialog(QDialog):
    def __init__(self, parent=None, current_w=0, current_h=0):
        super().__init__(parent)
        self.setWindowTitle("Resize Image")
        layout = QFormLayout(self)
        self.w_in = QLineEdit(str(current_w))
        self.h_in = QLineEdit(str(current_h))
        self.pct_in = QLineEdit("100")
        layout.addRow("Width (px):", self.w_in)
        layout.addRow("Height (px):", self.h_in)
        layout.addRow("Scale (%):", self.pct_in)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def getValues(self):
        try:
            w = int(self.w_in.text())
            h = int(self.h_in.text())
            pct = float(self.pct_in.text())
            return w, h, pct
        except:
            return None

class InfoDialog(QDialog):
    def __init__(self, parent=None, info_text=""):
        super().__init__(parent)
        self.setWindowTitle("Image Properties")
        layout = QVBoxLayout(self)
        label = QLabel(info_text)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

class ImageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ImageApp - Merged (Batch1+2+3)")
        self.image = None
        self.preview_image = None
        self.history = []
        self.redo_stack = []
        self.current_path = None
        self._init_ui()
        self.setAcceptDrops(True)

    def _init_ui(self):
        # Menu bar (Filters dropdown)
        self.menubar = QMenuBar(self)
        filters_menu = QMenu("Filters", self)
        acts = [
            ("Sepia", "sepia"),
            ("Negative/Invert", "negative"),
            ("Sharpen (Soft)", "sharpen_soft"),
            ("Sharpen (Strong)", "sharpen_strong"),
            ("Cartoon", "cartoon"),
            ("Auto Enhance", "auto_enhance")
        ]
        for title, name in acts:
            a = QAction(title, self)
            # lambda with default arg to capture name correctly
            a.triggered.connect(lambda checked=False, n=name: self.on_filter_menu(n))
            filters_menu.addAction(a)
        self.menubar.addMenu(filters_menu)

        # View
        self.view = ImageView(self)
        self.view.setMinimumSize(700, 480)

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

        crop_btn = QPushButton("Crop (manual)")
        crop_btn.clicked.connect(self.open_crop_dialog)
        resize_btn = QPushButton("Resize")
        resize_btn.clicked.connect(self.open_resize_dialog)
        info_btn = QPushButton("Info")
        info_btn.clicked.connect(self.show_info_dialog)

        # Apply/Cancel for filter previews (kept for backward compatibility; main preview uses dialog)
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
        btn_layout.addWidget(crop_btn)
        btn_layout.addWidget(resize_btn)
        btn_layout.addWidget(info_btn)
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

        main_layout = QVBoxLayout(self)
        main_layout.setMenuBar(self.menubar)
        main_layout.addWidget(self.view)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(group)
        self.setLayout(main_layout)

    # -------------------- Drag & drop --------------------
    def dragEnterEvent(self, event):
        mime = event.mimeData()
        if mime.hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        res = QMessageBox.question(self, "Open file?", f"Open dropped file?\n{path}", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if res == QMessageBox.StandardButton.Yes:
            self.load_image(path)
        else:
            return

    # -------------------- Image / history --------------------
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
        self.update_view()
        self.reset_sliders_preview()

    def redo(self):
        if not self.redo_stack:
            QMessageBox.information(self, "Redo", "No more redo steps available.")
            return
        img = self.redo_stack.pop()
        self.history.append(np.copy(img))
        self.image = np.copy(img)
        self.update_view()
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
    def load_image(self, path=None):
        if path is None:
            path, _ = QFileDialog.getOpenFileName(self, "Open image", "", "Images (*.png *.jpg *.jpeg *.bmp *.tif)")
            if not path:
                return
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            QMessageBox.critical(self, "Error", "Failed to load image.")
            return
        self.image = img
        self.current_path = path
        self.history = []
        self.redo_stack = []
        self.push_history(self.image)
        self.update_view()
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
        self.update_view()
        self.reset_sliders_preview()

    def update_view(self, img=None):
        if img is None:
            img = self.image
        if img is None:
            self.view.setPhoto(None)
            return
        pix = cv_img_to_qpixmap(img)
        self.view.setPhoto(pix)

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
        self.update_view(self.preview_image)
        # when adjustments produce preview, disable apply/cancel for filter previews
        self.apply_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)

    def commit_preview(self):
        if self.preview_image is None:
            return
        self.push_history(self.preview_image)
        self.image = np.copy(self.preview_image)
        self.preview_image = None

    # -------------------- Filter preview / apply / cancel (uses preview dialog) --------------------
    def on_filter_menu(self, name):
        if not self.history:
            return
        base = np.copy(self.history[-1])
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
        pix = cv_img_to_qpixmap(out)
        dlg = FilterPreviewDialog(self, pixmap=pix)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_apply:
            # apply
            self.push_history(out)
            self.image = np.copy(out)
            self.update_view()
            self.reset_sliders_preview()

    def apply_preview_filter(self):
        if self.preview_image is None:
            return
        self.push_history(self.preview_image)
        self.image = np.copy(self.preview_image)
        self.preview_image = None
        self.update_view()
        self.apply_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.reset_sliders_preview()

    def cancel_preview_filter(self):
        self.preview_image = None
        if self.history:
            self.update_view(self.history[-1])
        self.apply_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)

    # -------------------- Filter implementations --------------------
    @staticmethod
    def filter_sepia(img):
        if img is None:
            return None
        imgf = img.astype(np.float32)
        sepia_mat = np.array([[0.272, 0.534, 0.131],
                              [0.349, 0.686, 0.168],
                              [0.393, 0.769, 0.189]], dtype=np.float32)
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
            blur = cv2.GaussianBlur(img, (0,0), sigmaX=1.0)
            img_float = img.astype(np.float32)
            mask = img_float - blur.astype(np.float32)
            result = img_float + 0.7 * mask
            result = np.clip(result, 0, 255).astype(np.uint8)
            return result
        else:
            kernel = np.array([[0, -1, 0],
                               [-1, 5, -1],
                               [0, -1, 0]], dtype=np.float32)
            res = cv2.filter2D(img, -1, kernel)
            return np.clip(res, 0, 255).astype(np.uint8)

    @staticmethod
    def filter_cartoon(img):
        if img is None:
            return None
        img_small = cv2.pyrDown(img)
        for _ in range(5):
            img_small = cv2.bilateralFilter(img_small, d=9, sigmaColor=75, sigmaSpace=75)
        img_up = cv2.pyrUp(img_small)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(edges, 255,
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY,
                                      blockSize=9, C=2)
        color = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        cartoon = cv2.bitwise_and(color, edges_colored)
        return cartoon

    @staticmethod
    def filter_auto_enhance(img):
        if img is None:
            return None
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        lab_cl = cv2.merge((cl, a, b))
        enhanced = cv2.cvtColor(lab_cl, cv2.COLOR_LAB2BGR)
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

    # -------------------- Utility --------------------
    @staticmethod
    def apply_brightness_contrast(input_img, brightness=0, contrast=1.0):
        if input_img is None:
            return None
        img = input_img.astype(np.float32)
        img = img * contrast + brightness
        img = np.clip(img, 0, 255)
        return img.astype(np.uint8)

    # -------------------- Crop / Resize / Info dialogs --------------------
    def open_crop_dialog(self):
        if self.image is None:
            QMessageBox.information(self, "Crop", "Load an image first.")
            return
        dlg = NumericCropDialog(self, img_shape=self.image.shape)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            vals = dlg.getValues()
            if not vals:
                QMessageBox.warning(self, "Crop", "Invalid input.")
                return
            x, y, w, h = vals
            h_img, w_img = self.image.shape[:2]
            x = max(0, min(x, w_img-1))
            y = max(0, min(y, h_img-1))
            w = max(1, min(w, w_img - x))
            h = max(1, min(h, h_img - y))
            cropped = self.image[y:y+h, x:x+w].copy()
            self.push_history(cropped)
            self.image = np.copy(cropped)
            self.update_view()

    def open_resize_dialog(self):
        if self.image is None:
            QMessageBox.information(self, "Resize", "Load an image first.")
            return
        h_img, w_img = self.image.shape[:2]
        dlg = ResizeDialog(self, current_w=w_img, current_h=h_img)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            vals = dlg.getValues()
            if not vals:
                QMessageBox.warning(self, "Resize", "Invalid input.")
                return
            w, h, pct = vals
            if pct and abs(pct - 100.0) > 1e-6:
                scale = pct / 100.0
                new_w = max(1, int(w_img * scale))
                new_h = max(1, int(h_img * scale))
            else:
                new_w = max(1, int(w))
                new_h = max(1, int(h))
            resized = cv2.resize(self.image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            self.push_history(resized)
            self.image = np.copy(resized)
            self.update_view()

    def show_info_dialog(self):
        if self.image is None:
            QMessageBox.information(self, "Info", "Load an image first.")
            return
        h, w = self.image.shape[:2]
        channels = 1 if len(self.image.shape) == 2 else self.image.shape[2]
        mean = np.mean(self.image)
        std = np.std(self.image)
        size_info = ""
        if self.current_path and os.path.exists(self.current_path):
            size_info = f"File size: {os.path.getsize(self.current_path)} bytes\n"
        info_text = f"Resolution: {w} x {h}\nChannels: {channels}\nMean pixel: {mean:.2f}\nStd dev: {std:.2f}\n{size_info}"
        dlg = InfoDialog(self, info_text=info_text)
        dlg.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ImageApp()
    w.resize(1100, 820)
    w.show()
    sys.exit(app.exec())
