import os
import sys
import vlc
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

def fix_vlc_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS

        os.environ["PATH"] = (
            base_path + os.pathsep +
            os.environ.get("PATH", "")
        )

        os.environ["VLC_PLUGIN_PATH"] = os.path.join(base_path, "plugins")


class FullscreenPlayer(QWidget):
    def __init__(self, screen_geometry):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setGeometry(screen_geometry)

        # Área do vídeo
        self.video_frame = QLabel()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.video_frame)
        self.setLayout(layout)

        # Instancia o player VLC
        self.instance = vlc.Instance("--no-xlib")
        self.player = self.instance.media_player_new()

    def play_media(self, file_path):
        media = self.instance.media_new(file_path)
        self.player.set_media(media)
        self.player.set_hwnd(self.video_frame.winId())
        self.showFullScreen()
        self.player.play()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.player.stop()
            self.close()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Player Simples • Telas da Igreja")
        self.resize(600, 400)

        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_add = QPushButton("Adicionar Mídias")
        btn_add.clicked.connect(self.add_files)
        layout.addWidget(btn_add)

        self.setLayout(layout)

        self.list_widget.itemDoubleClicked.connect(self.play_selected)

        # Detecta telas
        screens = QApplication.screens()
        self.output_screen = screens[1] if len(screens) > 1 else screens[0]

        # Player fullscreen
        self.player_window = FullscreenPlayer(self.output_screen.geometry())

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Selecione mídias", "", 
            "Mídias (*.mp4 *.mov *.jpg *.png *.mkv)"
        )
        for file in files:
            self.list_widget.addItem(file)

    def play_selected(self):
        item = self.list_widget.currentItem()
        if item:
            self.player_window.play_media(item.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
