import unittest
from unittest.mock import patch, MagicMock
from src.daq_worker import DaqDataCollector
import numpy as np
from PySide6.QtCore import QCoreApplication, QTimer

class TestDaqDataCollector(unittest.TestCase):
  def setUp(self):
    # Qt 이벤트 루프 초기화 (시그널 테스트용)
    self.app = QCoreApplication.instance() or QCoreApplication([])
    # DAQ 하드웨어 없이 테스트를 위해 모킹
    self.collector = DaqDataCollector(device_name="Dev1", channel="ai0")

  @patch("nidaqmx.Task")
  def test_run_emits_data(self, mock_task):
    """
    정상적으로 데이터가 수집되어 data_collected 시그널이 emit되는지 테스트
    """
    mock_instance = mock_task.return_value.__enter__.return_value
    mock_instance.read.return_value = [1.0, 2.0, 3.0, 4.0, 5.0]
    emitted = []
    def on_data(data, ts):
      emitted.append((data, ts))
    self.collector.data_collected.connect(on_data)
    self.collector._running = True
    # run()을 직접 호출 (스레드 없이)
    with patch("time.time", return_value=123.456):
      self.collector._running = False  # 한 번만 실행
      self.collector.run()
    self.assertTrue(len(emitted) > 0)
    self.assertTrue(np.allclose(emitted[0][0], [1.0,2.0,3.0,4.0,5.0]))
    self.assertEqual(emitted[0][1], 123.456)

  @patch("nidaqmx.Task", side_effect=Exception("장치 없음"))
  def test_run_emits_error(self, mock_task):
    """
    DAQ 장치가 없을 때 error_occurred 시그널이 emit되는지 테스트
    """
    errors = []
    self.collector.error_occurred.connect(lambda msg: errors.append(msg))
    self.collector._running = True
    self.collector._running = False  # 한 번만 실행
    self.collector.run()
    self.assertTrue(any("장치 없음" in e for e in errors))

if __name__ == "__main__":
  unittest.main() 