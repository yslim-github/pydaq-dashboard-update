from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer
import pyqtgraph as pg
import numpy as np

class RealtimePlotWidget(QWidget):
  """
  pyqtgraph 기반 실시간 플로팅 위젯
  - 다채널 지원
  - 컬러맵/테마 적용
  - 60 FPS 이상 렌더링
  """
  def __init__(self, channel_count=1, buffer_size=10000, parent=None):
    super().__init__(parent)
    self.channel_count = channel_count  # 표시할 채널 개수
    self.buffer_size = buffer_size      # 그래프에 유지할 데이터 개수
    self.data_buffer = np.zeros((channel_count, buffer_size))  # 데이터 버퍼
    self.ptr = 0  # 현재 데이터 위치

    # pyqtgraph PlotWidget 생성 및 레이아웃 배치
    self.plot_widget = pg.PlotWidget()
    self.plot_widget.setBackground('w')  # 배경색(테마)
    self.plot_widget.showGrid(x=True, y=True)
    self.plot_widget.setTitle("실시간 DAQ 데이터 플로팅")
    self.plot_widget.addLegend()
    self.curves = []
    colors = ['r', 'g', 'b', 'm', 'c', 'y']
    for i in range(channel_count):
      curve = self.plot_widget.plot(pen=pg.mkPen(colors[i % len(colors)], width=2), name=f"채널 {i+1}")
      self.curves.append(curve)

    layout = QVBoxLayout()
    layout.addWidget(self.plot_widget)
    self.setLayout(layout)

    # 60 FPS 타이머로 주기적 업데이트
    self.timer = QTimer()
    self.timer.timeout.connect(self.update_plot)
    self.timer.start(int(1000/60))  # 60 FPS

  def append_data(self, data: np.ndarray):
    """
    새로운 데이터를 버퍼에 추가
    data: (채널 수, 샘플 수) 형태의 numpy 배열
    """
    # 입력 데이터 shape/type 검사
    if not isinstance(data, np.ndarray):
      raise ValueError("입력 데이터는 numpy.ndarray여야 합니다.")
    if data.ndim == 1:
      if data.shape[0] != self.channel_count:
        raise ValueError(f"1차원 데이터의 길이({data.shape[0]})가 채널 수({self.channel_count})와 다릅니다.")
      data = data.reshape((self.channel_count, -1))
    if data.ndim != 2 or data.shape[0] != self.channel_count:
      raise ValueError(f"입력 데이터 shape는 ({self.channel_count}, N)이어야 합니다. 현재: {data.shape}")
    n_samples = data.shape[1]
    # 버퍼에 데이터 추가 (오버플로우 시 shift)
    if self.ptr + n_samples > self.buffer_size:
      overflow = self.ptr + n_samples - self.buffer_size
      self.data_buffer = np.roll(self.data_buffer, -overflow, axis=1)
      self.ptr = self.buffer_size - n_samples
    self.data_buffer[:, self.ptr:self.ptr+n_samples] = data
    self.ptr += n_samples

  def update_plot(self):
    """
    그래프를 최신 데이터로 갱신
    """
    try:
      for i, curve in enumerate(self.curves):
        curve.setData(self.data_buffer[i, :self.ptr])
    except Exception as e:
      print(f"[플롯 업데이트 오류] {e}")

  def clear(self):
    """
    버퍼 및 그래프 초기화
    """
    self.data_buffer[:] = 0
    self.ptr = 0
    for curve in self.curves:
      curve.clear() 