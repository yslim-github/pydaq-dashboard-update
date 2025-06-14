from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Qt
import pyqtgraph as pg
import numpy as np

class RealtimePlotWidget(QWidget):
  """
  오실로스코프 스타일 실시간 플로팅 위젯
  - 검은 배경, 노란/흰색 파형, 두꺼운 그리드, 범례, 통계, 텍스트 주석 지원
  """
  def __init__(self, channel_count=1, buffer_size=10000, parent=None):
    super().__init__(parent)
    self.channel_count = channel_count
    self.buffer_size = buffer_size
    self.data_buffer = np.zeros((channel_count, buffer_size))
    self.ptr = 0

    # pyqtgraph PlotWidget 생성 및 레이아웃 배치
    self.plot_widget = pg.PlotWidget()
    self.plot_widget.setBackground('k')  # 검은 배경
    self.plot_widget.showGrid(x=True, y=True, alpha=0.6)
    self.plot_widget.setTitle("실시간 DAQ 데이터 플로팅", color='#fff', size='16pt')
    self.plot_widget.getAxis('left').setPen('#fff')
    self.plot_widget.getAxis('bottom').setPen('#fff')
    self.plot_widget.getAxis('left').setTextPen('#fff')
    self.plot_widget.getAxis('bottom').setTextPen('#fff')
    self.plot_widget.addLegend(offset=(30, 30))
    self.curves = []
    # 오실로스코프 스타일 컬러
    colors = ['#ffe600', '#ffffff', '#00e6ff', '#ff5e00', '#00ff85', '#ff00c8']
    for i in range(channel_count):
      curve = self.plot_widget.plot(
        pen=pg.mkPen(colors[i % len(colors)], width=2.5, style=Qt.SolidLine),
        name=f"채널 {i+1}"
      )
      self.curves.append(curve)
    # 통계/주석용 텍스트 아이템
    self.text_items = []
    for i in range(channel_count):
      txt = pg.TextItem(color=colors[i % len(colors)], anchor=(0,1))
      self.plot_widget.addItem(txt)
      self.text_items.append(txt)
    # 레이아웃
    layout = QVBoxLayout()
    layout.addWidget(self.plot_widget)
    self.setLayout(layout)
    # 60 FPS 타이머로 주기적 업데이트
    self.timer = QTimer()
    self.timer.timeout.connect(self.update_plot)
    self.timer.start(int(1000/60))

  def append_data(self, data: np.ndarray):
    """
    새로운 데이터를 버퍼에 추가
    data: (채널 수, 샘플 수) 형태의 numpy 배열
    """
    if not isinstance(data, np.ndarray):
      raise ValueError("입력 데이터는 numpy.ndarray여야 합니다.")
    if data.ndim == 1:
      if data.shape[0] != self.channel_count:
        raise ValueError(f"1차원 데이터의 길이({data.shape[0]})가 채널 수({self.channel_count})와 다릅니다.")
      data = data.reshape((self.channel_count, -1))
    if data.ndim != 2 or data.shape[0] != self.channel_count:
      raise ValueError(f"입력 데이터 shape는 ({self.channel_count}, N)이어야 합니다. 현재: {data.shape}")
    n_samples = data.shape[1]
    if self.ptr + n_samples > self.buffer_size:
      overflow = self.ptr + n_samples - self.buffer_size
      self.data_buffer = np.roll(self.data_buffer, -overflow, axis=1)
      self.ptr = self.buffer_size - n_samples
    self.data_buffer[:, self.ptr:self.ptr+n_samples] = data
    self.ptr += n_samples

  def update_plot(self):
    """
    그래프를 최신 데이터로 갱신 + 통계/주석 표시
    """
    try:
      for i, curve in enumerate(self.curves):
        curve.setData(self.data_buffer[i, :self.ptr])
        # 통계 표시 (평균/최대/최소)
        if self.ptr > 0:
          d = self.data_buffer[i, :self.ptr]
          stats = f"avg={np.mean(d):.3f}\nmax={np.max(d):.3f}\nmin={np.min(d):.3f}"
          self.text_items[i].setText(stats)
          self.text_items[i].setPos(self.ptr, np.max(d))
    except Exception as e:
      print(f"[플롯 업데이트 오류] {e}")

  def add_annotation(self, x, y, text, color='#ff4444'):
    """
    플롯 위에 텍스트(주석) 추가
    """
    ann = pg.TextItem(text, color=color, anchor=(0.5,0))
    ann.setPos(x, y)
    self.plot_widget.addItem(ann)
    return ann

  def clear(self):
    """
    버퍼 및 그래프 초기화
    """
    self.data_buffer[:] = 0
    self.ptr = 0
    for curve in self.curves:
      curve.clear()
    for txt in self.text_items:
      txt.setText("")

  def set_colormap(self, cmap_name):
    """
    플롯 곡선/통계 컬러맵 동적 변경
    cmap_name: 'default', 'viridis', 'plasma', 'magma' 등 지원
    """
    # 컬러맵 정의
    colormaps = {
      'default': ['#ffe600', '#ffffff', '#00e6ff', '#ff5e00', '#00ff85', '#ff00c8'],
      'viridis': ['#440154', '#3b528b', '#21918c', '#5ec962', '#fde725', '#fee825'],
      'plasma': ['#0d0887', '#7e03a8', '#cc4778', '#f89441', '#f0f921', '#f9d923'],
      'magma': ['#000004', '#3b0f70', '#8c2981', '#de4968', '#fe9f6d', '#fcfdbf'],
    }
    colors = colormaps.get(cmap_name, colormaps['default'])
    # 곡선 색상 변경
    for i, curve in enumerate(self.curves):
      curve.setPen(pg.mkPen(colors[i % len(colors)], width=2.5, style=Qt.SolidLine))
    # 통계 텍스트 색상 변경
    for i, txt in enumerate(self.text_items):
      txt.setColor(colors[i % len(colors)]) 