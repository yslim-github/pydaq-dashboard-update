import unittest
from src.daq_config_widget import DaqConfigWidget
from PySide6.QtWidgets import QApplication, QMessageBox
import sys

app = QApplication.instance() or QApplication(sys.argv)

class TestDaqConfigWidget(unittest.TestCase):
  def setUp(self):
    self.widget = DaqConfigWidget()
    self.signal_emitted = False
    def on_config(device, channel, rate):
      self.signal_emitted = True
      self.last_device = device
      self.last_channel = channel
      self.last_rate = rate
    self.widget.config_changed.connect(on_config)

  def test_valid_input_emits_signal(self):
    """
    정상 입력 시 config_changed 시그널이 emit되는지 테스트
    """
    self.widget.device_edit.setText("Dev2")
    self.widget.channel_edit.setText("ai1")
    self.widget.sample_rate_spin.setValue(5000)
    self.widget.on_apply_clicked()
    self.assertTrue(self.signal_emitted)
    self.assertEqual(self.last_device, "Dev2")
    self.assertEqual(self.last_channel, "ai1")
    self.assertEqual(self.last_rate, 5000)

  def test_invalid_device_shows_error(self):
    """
    빈 디바이스명 입력 시 시그널 emit 안 되고 오류 메시지 표시
    """
    self.widget.device_edit.setText("")
    self.widget.channel_edit.setText("ai0")
    self.widget.sample_rate_spin.setValue(1000)
    self.signal_emitted = False
    # QMessageBox.critical 모킹
    called = {}
    def fake_critical(parent, title, msg):
      called['msg'] = msg
    orig_critical = QMessageBox.critical
    QMessageBox.critical = fake_critical
    self.widget.on_apply_clicked()
    QMessageBox.critical = orig_critical
    self.assertFalse(self.signal_emitted)
    self.assertIn("디바이스명", called['msg'])

  def test_invalid_channel_shows_error(self):
    """
    빈 채널명 입력 시 시그널 emit 안 되고 오류 메시지 표시
    """
    self.widget.device_edit.setText("Dev1")
    self.widget.channel_edit.setText("")
    self.widget.sample_rate_spin.setValue(1000)
    self.signal_emitted = False
    called = {}
    def fake_critical(parent, title, msg):
      called['msg'] = msg
    orig_critical = QMessageBox.critical
    QMessageBox.critical = fake_critical
    self.widget.on_apply_clicked()
    QMessageBox.critical = orig_critical
    self.assertFalse(self.signal_emitted)
    self.assertIn("채널명", called['msg'])

  def test_invalid_sample_rate_shows_error(self):
    """
    샘플링 속도 0 입력 시 시그널 emit 안 되고 오류 메시지 표시
    """
    self.widget.device_edit.setText("Dev1")
    self.widget.channel_edit.setText("ai0")
    # 샘플링 속도 spinbox의 최소값을 0으로 임시로 낮춤
    self.widget.sample_rate_spin.setRange(0, 2000000)
    self.widget.sample_rate_spin.setValue(0)
    self.signal_emitted = False
    called = {}
    def fake_critical(parent, title, msg):
      called['msg'] = msg
    orig_critical = QMessageBox.critical
    QMessageBox.critical = fake_critical
    self.widget.on_apply_clicked()
    QMessageBox.critical = orig_critical
    self.assertFalse(self.signal_emitted)
    self.assertIn("샘플링 속도", called['msg'])

if __name__ == "__main__":
  unittest.main() 