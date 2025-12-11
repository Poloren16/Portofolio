# app/workers.py
from PyQt6.QtCore import QThread, pyqtSignal
from processing.exporter import render_with_effects


class RenderWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)


def __init__(self, video_path, effect_name, out_path=None):
    super().__init__()
    self.video_path = video_path
    self.effect_name = effect_name
    self.out_path = out_path


def run(self):
    def progress_cb(p):
    # p: float 0..1
        self.progress.emit(int(p * 100))


out = render_with_effects(self.video_path, self.effect_name, progress_cb, out_path=self.out_path)
self.finished.emit(out)