import unittest
import numpy as np
from src.plot_widget import RealtimePlotWidget
from PySide6.QtWidgets import QApplication
import sys

# QApplication 인스턴스 생성 (GUI 위젯 테스트용)
app = QApplication.instance() or QApplication(sys.argv)

class TestRealtimePlotWidget(unittest.TestCase):
  def setUp(self):
    # 2채널, 100포인트 버퍼로 위젯 생성
    self.widget = RealtimePlotWidget(channel_count=2, buffer_size=100)

  def test_append_and_clear(self):
    """
    append_data, clear 함수가 정상 동작하는지 테스트
    """
    # 2채널, 10포인트 가상 데이터 추가
    data = np.ones((2, 10))
    self.widget.append_data(data)
    # 버퍼에 데이터가 잘 들어갔는지 확인
    self.assertTrue(np.all(self.widget.data_buffer[:, :10] == 1))
    # clear() 호출 후 버퍼가 0으로 초기화되는지 확인
    self.widget.clear()
    self.assertTrue(np.all(self.widget.data_buffer == 0))

  def test_update_plot(self):
    """
    update_plot 함수가 에러 없이 동작하는지 테스트
    """
    data = np.random.randn(2, 20)
    self.widget.append_data(data)
    try:
      self.widget.update_plot()
    except Exception as e:
      self.fail(f"update_plot에서 예외 발생: {e}")

  def test_append_invalid_shape(self):
    """
    잘못된 shape의 데이터 입력 시 예외가 발생하는지 테스트
    """
    # 1차원 데이터(채널 수 불일치)
    with self.assertRaises(Exception):
      self.widget.append_data(np.ones(10))
    # 3차원 데이터
    with self.assertRaises(Exception):
      self.widget.append_data(np.ones((2, 10, 2)))

if __name__ == "__main__":
  unittest.main() 