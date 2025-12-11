import sys
left = QVBoxLayout()
self.btn_open = QPushButton('Open Video')
self.btn_open.clicked.connect(self.open_file)
left.addWidget(self.btn_open)


self.effects_list = QListWidget()
self.effects_list.addItems(['grayscale', 'brightness', 'contrast', 'rotate'])
left.addWidget(QLabel('Effects'))
left.addWidget(self.effects_list)


# Center: video preview
center = QVBoxLayout()
self.video_widget = QVideoWidget()
self.player = QMediaPlayer()
self.audio_output = QAudioOutput()
self.player.setVideoOutput(self.video_widget)
self.player.setAudioOutput(self.audio_output)


center.addWidget(self.video_widget)


# Playback controls (simple)
play_btn = QPushButton('Play')
play_btn.clicked.connect(self.player.play)
stop_btn = QPushButton('Stop')
stop_btn.clicked.connect(self.player.stop)
center.addWidget(play_btn)
center.addWidget(stop_btn)


# Right: audio controls + export
right = QVBoxLayout()
right.addWidget(QLabel('Audio'))
self.slider_volume = QSlider(Qt.Orientation.Horizontal)
self.slider_volume.setRange(0, 100)
self.slider_volume.setValue(100)
self.slider_volume.valueChanged.connect(self.set_volume)
right.addWidget(QLabel('Volume'))
right.addWidget(self.slider_volume)


self.btn_export = QPushButton('Export (Apply Effects)')
self.btn_export.clicked.connect(self.export)
right.addWidget(self.btn_export)


self.progress = QProgressBar()
right.addWidget(self.progress)


main_layout.addLayout(left, 2)
main_layout.addLayout(center, 6)
main_layout.addLayout(right, 2)
self.setLayout(main_layout)


def open_file(self):
    path, _ = QFileDialog.getOpenFileName(self, 'Open video', '', 'Video Files (*.mp4 *.avi *.mov *.mkv)')
if path:
    self.video_path = path
    self.player.setSource(QUrl.fromLocalFile(path))


def set_volume(self, v):
    self.audio_output.setVolume(v / 100.0)


def export(self):
    if not self.video_path:
    return
# pilih effect sederhana: ambil item terpilih
effect = self.effects_list.currentItem().text() if self.effects_list.currentItem() else None
# jalankan thread render
self.worker = RenderWorker(self.video_path, effect)
self.worker.progress.connect(self.progress.setValue)
self.worker.finished.connect(lambda out: print('Done', out))
self.worker.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())