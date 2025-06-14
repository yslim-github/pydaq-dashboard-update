from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QLabel, QComboBox
from PySide6.QtCore import Qt, QTimer, Signal
import numpy as np

class OfflinePlayer(QWidget):
  # 재생 위치가 변경될 때 (프레임 인덱스, 데이터) 시그널 발생
  frame_changed = Signal(int, np.ndarray)
  # 재생이 끝났을 때 시그널
  playback_finished = Signal()

  def __init__(self, parent=None):
    super().__init__(parent)
    self.setFixedHeight(60)
    self.data = None  # 전체 데이터 (numpy 배열)
    self.current_frame = 0
    self.playing = False
    self.playback_speed = 1  # 1x, 2x, 4x 등
    self.timer = QTimer(self)
    self.timer.timeout.connect(self._on_timer_tick)

    # UI 구성
    self.play_button = QPushButton("▶")
    self.pause_button = QPushButton("⏸")
    self.speed_combo = QComboBox()
    self.speed_combo.addItems(["1x", "2x", "4x"])
    self.slider = QSlider(Qt.Horizontal)
    self.slider.setMinimum(0)
    self.slider.setMaximum(0)
    self.position_label = QLabel("0 / 0")

    layout = QHBoxLayout()
    layout.addWidget(self.play_button)
    layout.addWidget(self.pause_button)
    layout.addWidget(QLabel("배속:"))
    layout.addWidget(self.speed_combo)
    layout.addWidget(self.slider)
    layout.addWidget(self.position_label)
    self.setLayout(layout)

    # 이벤트 연결
    self.play_button.clicked.connect(self.play)
    self.pause_button.clicked.connect(self.pause)
    self.speed_combo.currentIndexChanged.connect(self.change_speed)
    self.slider.valueChanged.connect(self.seek)

  def set_data(self, data: np.ndarray):
    """
    재생할 데이터 설정
    """
    self.data = data
    self.current_frame = 0
    self.slider.setMaximum(data.shape[-1] - 1)
    self.slider.setValue(0)
    self._update_position_label()

  def play(self):
    """
    재생 시작
    """
    if self.data is None:
      return
    self.playing = True
    self.timer.start(int(1000 / (60 * self.playback_speed)))  # 60FPS 기준 배속 적용

  def pause(self):
    """
    일시정지
    """
    self.playing = False
    self.timer.stop()

  def change_speed(self):
    """
    배속 변경
    """
    speed_text = self.speed_combo.currentText().replace("x", "")
    try:
      self.playback_speed = int(speed_text)
    except ValueError:
      self.playback_speed = 1
    if self.playing:
      self.timer.start(int(1000 / (60 * self.playback_speed)))

  def seek(self, frame_idx):
    """
    슬라이더로 재생 위치 이동 (범위 초과 시 자동 보정)
    """
    if self.data is None:
      return
    # 프레임 인덱스가 범위를 벗어나면 자동 보정
    total_frames = self.data.shape[-1]
    if frame_idx < 0:
      frame_idx = 0
    elif frame_idx >= total_frames:
      frame_idx = total_frames - 1
    self.current_frame = frame_idx
    self._emit_frame()
    self._update_position_label()

  def _on_timer_tick(self):
    if self.data is None:
      return
    if self.current_frame < self.data.shape[-1] - 1:
      self.current_frame += 1
      self.slider.setValue(self.current_frame)
      self._emit_frame()
      self._update_position_label()
    else:
      self.pause()
      self.playback_finished.emit()

  def _emit_frame(self):
    # 현재 프레임 데이터 시그널 emit
    if self.data is not None:
      frame_data = self.data[..., self.current_frame]
      self.frame_changed.emit(self.current_frame, frame_data)

  def _update_position_label(self):
    if self.data is not None:
      total = self.data.shape[-1]
      self.position_label.setText(f"{self.current_frame+1} / {total}")
    else:
      self.position_label.setText("0 / 0") 