from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QSpinBox, QPushButton, QMessageBox
from PySide6.QtCore import Signal

class DaqConfigWidget(QWidget):
  # 설정값 변경 시 (device, channel, sample_rate) 시그널 발생
  config_changed = Signal(str, str, int)

  def __init__(self, parent=None):
    super().__init__(parent)
    self.setWindowTitle("DAQ 설정")

    # 입력 위젯 생성
    self.device_edit = QLineEdit("Dev1")
    self.channel_edit = QLineEdit("ai0")
    self.sample_rate_spin = QSpinBox()
    self.sample_rate_spin.setRange(1, 2000000)
    self.sample_rate_spin.setValue(10000)
    self.apply_button = QPushButton("설정 적용")

    # 폼 레이아웃 배치
    form = QFormLayout()
    form.addRow("디바이스명", self.device_edit)
    form.addRow("채널명", self.channel_edit)
    form.addRow("샘플링 속도(Hz)", self.sample_rate_spin)
    form.addRow(self.apply_button)
    self.setLayout(form)

    # 버튼 클릭 시 설정 적용
    self.apply_button.clicked.connect(self.on_apply_clicked)

  def on_apply_clicked(self):
    """
    입력값 유효성 검사 후 시그널 발생
    """
    device = self.device_edit.text().strip()
    channel = self.channel_edit.text().strip()
    sample_rate = self.sample_rate_spin.value()
    # 간단한 유효성 검사
    if not device:
      self.show_error("디바이스명을 입력하세요.")
      return
    if not channel:
      self.show_error("채널명을 입력하세요.")
      return
    if sample_rate < 1:
      self.show_error("샘플링 속도는 1Hz 이상이어야 합니다.")
      return
    # 설정값 변경 시그널 emit
    self.config_changed.emit(device, channel, sample_rate)

  def show_error(self, message):
    QMessageBox.critical(self, "입력 오류", message) 