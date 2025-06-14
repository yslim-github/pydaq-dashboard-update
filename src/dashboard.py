from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QTextEdit, QListWidget, QGroupBox, QLabel, QMenu, QDialog, QFormLayout, QSpinBox, QComboBox
from PySide6.QtCore import Qt, QMimeData, QEvent
from PySide6.QtGui import QDrag, QMouseEvent, QDropEvent, QDragEnterEvent, QPixmap, QCursor
import json

class DraggableGroupBox(QGroupBox):
  """
  마우스 드래그&드롭이 가능한 QGroupBox (대시보드 위젯용)
  - 타이틀과 컨트롤 버튼이 겹치지 않도록 별도 레이아웃
  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.setAcceptDrops(True)
    self.setMouseTracking(True)
    # 타이틀 아래에 컨트롤 버튼을 별도 위젯으로 배치
    self.ctrl_widget = QWidget(self)
    ctrl_layout = QHBoxLayout()
    ctrl_layout.setContentsMargins(0, 0, 0, 0)
    ctrl_layout.setSpacing(4)
    self.ctrl_widget.setLayout(ctrl_layout)
    self.ctrl_widget.setFixedHeight(24)
    self.ctrl_widget.move(self.width() - 90, 2)  # 우측 상단에 위치(버튼 4개 기준)
    self.ctrl_widget.setStyleSheet("background:transparent;")
    self._ctrl_layout = ctrl_layout
    self.setStyleSheet(self.styleSheet() + "QGroupBox { border: 2px dashed #636e72; }")

  def mousePressEvent(self, event: QMouseEvent):
    if event.button() == Qt.LeftButton:
      drag = QDrag(self)
      mime = QMimeData()
      mime.setText(self.objectName())
      drag.setMimeData(mime)
      pixmap = QPixmap(self.size())
      self.render(pixmap)
      drag.setPixmap(pixmap)
      drag.setHotSpot(event.pos())
      drag.exec(Qt.MoveAction)
    super().mousePressEvent(event)

  def dragEnterEvent(self, event: QDragEnterEvent):
    if event.mimeData().hasText():
      event.acceptProposedAction()
    else:
      event.ignore()

  def dropEvent(self, event: QDropEvent):
    event.acceptProposedAction()

  def resizeEvent(self, event):
    # 우측 상단에 컨트롤 버튼 위치 고정
    self.ctrl_widget.move(self.width() - self.ctrl_widget.width() - 8, 2)
    super().resizeEvent(event)

class DashboardWidget(QWidget):
  """
  대시보드 컨테이너 위젯
  - 위젯 드래그&드롭, 추가/삭제/배치 지원
  - 레이아웃 저장/불러오기 지원
  - 플롯, 통계, 로그, 신호 목록 등 다양한 위젯 추가 지원
  - [프리셋/템플릿] 지원 (2024-06 추가)
  """
  def __init__(self, parent=None):
    super().__init__(parent)
    self.setAcceptDrops(True)
    self.layout = QVBoxLayout()
    self.setLayout(self.layout)
    self.widget_list = []  # 현재 배치된 위젯 목록

    # [프리셋/템플릿] 미리 정의된 프리셋 목록
    # 각 프리셋은 위젯 타입/설정 리스트로 구성
    self.presets = {
      "기본": [
        {"type": "RealtimePlotWidget", "channel_count": 1, "buffer_size": 10000},
        {"type": "QLabel"},
        {"type": "QTextEdit"},
        {"type": "QListWidget", "signals": ["채널 1"]},
      ],
      "오실로스코프": [
        {"type": "RealtimePlotWidget", "channel_count": 2, "buffer_size": 10000},
        {"type": "QTextEdit"},
      ],
      "통계+로그": [
        {"type": "QLabel"},
        {"type": "QTextEdit"},
      ],
    }

    # 레이아웃 저장/불러오기 버튼 + 위젯 추가 버튼
    btn_layout = QHBoxLayout()
    self.save_btn = QPushButton("레이아웃 저장")
    self.load_btn = QPushButton("레이아웃 불러오기")
    self.add_plot_btn = QPushButton("플롯 추가")
    self.add_stats_btn = QPushButton("통계 추가")
    self.add_log_btn = QPushButton("로그 추가")
    self.add_signal_btn = QPushButton("신호 목록 추가")
    btn_layout.addWidget(self.save_btn)
    btn_layout.addWidget(self.load_btn)
    btn_layout.addWidget(self.add_plot_btn)
    btn_layout.addWidget(self.add_stats_btn)
    btn_layout.addWidget(self.add_log_btn)
    btn_layout.addWidget(self.add_signal_btn)
    self.layout.addLayout(btn_layout)

    self.save_btn.clicked.connect(self.save_layout)
    self.load_btn.clicked.connect(self.load_layout)
    self.add_plot_btn.clicked.connect(self._add_plot)
    self.add_stats_btn.clicked.connect(self._add_stats)
    self.add_log_btn.clicked.connect(self._add_log)
    self.add_signal_btn.clicked.connect(self._add_signal)

  def _add_plot(self):
    from src.plot_widget import RealtimePlotWidget
    plot = RealtimePlotWidget(channel_count=1, buffer_size=10000)
    self.add_dashboard_widget(plot, widget_id=f"plot{len(self.widget_list)+1}", title="실시간 플롯")

  def _add_stats(self):
    self.add_statistics_widget("통계 정보 없음")

  def _add_log(self):
    self.add_log_widget()

  def _add_signal(self):
    self.add_signal_list_widget(["채널 1"])

  def add_dashboard_widget(self, widget, widget_id=None, title=None):
    """
    대시보드에 위젯 추가 (플롯, 통계, 로그, 신호 목록 등)
    title: QGroupBox 타이틀(옵션)
    """
    if title:
      group = DraggableGroupBox(title)
      vbox = QVBoxLayout()
      vbox.setContentsMargins(8, 24, 8, 8)  # 타이틀/버튼과 내용 간 여백 확보
      vbox.addWidget(widget)
      # 컨트롤 버튼(✕, ⚙, ▲, ▼)을 group.ctrl_widget에 배치
      btn_del = QPushButton("✕")
      btn_del.setFixedSize(20, 20)
      btn_del.setStyleSheet("font-size:12px;padding:0 2px;margin:0 2px;")
      btn_up = QPushButton("▲")
      btn_up.setFixedSize(20, 20)
      btn_up.setStyleSheet("font-size:12px;padding:0 2px;margin:0 2px;")
      btn_down = QPushButton("▼")
      btn_down.setFixedSize(20, 20)
      btn_down.setStyleSheet("font-size:12px;padding:0 2px;margin:0 2px;")
      btn_settings = None
      if type(widget).__name__ == "RealtimePlotWidget":
        btn_settings = QPushButton("⚙")
        btn_settings.setFixedSize(20, 20)
        btn_settings.setStyleSheet("font-size:13px;padding:0 2px;margin:0 2px;")
        group._ctrl_layout.addWidget(btn_settings)
      group._ctrl_layout.addWidget(btn_del)
      group._ctrl_layout.addWidget(btn_up)
      group._ctrl_layout.addWidget(btn_down)
      group._ctrl_layout.addStretch()
      group.setLayout(vbox)
      if type(widget).__name__ == "RealtimePlotWidget":
        self.layout.addWidget(group, stretch=3)
      else:
        self.layout.addWidget(group, stretch=1)
      self.widget_list.append({'id': widget_id or str(id(widget)), 'widget': group, 'type': type(widget).__name__})
      group.setObjectName(widget_id or str(id(widget)))
      group.setAttribute(Qt.WA_DeleteOnClose)
      btn_del.clicked.connect(lambda: self.remove_dashboard_widget(group))
      btn_up.clicked.connect(lambda: self.move_widget(group, -1))
      btn_down.clicked.connect(lambda: self.move_widget(group, 1))
      if btn_settings:
        btn_settings.clicked.connect(lambda: self.show_plot_settings_dialog(widget, group))
      group.installEventFilter(self)
    else:
      self.layout.addWidget(widget, stretch=1)
      self.widget_list.append({'id': widget_id or str(id(widget)), 'widget': widget, 'type': type(widget).__name__})
      widget.setObjectName(widget_id or str(id(widget)))
      widget.setAttribute(Qt.WA_DeleteOnClose)

  def move_widget(self, groupbox, direction):
    """
    위젯 순서 이동 (direction: -1=위, 1=아래)
    """
    idx = next((i for i, w in enumerate(self.widget_list) if w['widget'] == groupbox), -1)
    if idx == -1:
      return
    new_idx = idx + direction
    if 0 <= new_idx < len(self.widget_list):
      self.layout.removeWidget(groupbox)
      self.layout.insertWidget(new_idx+1, groupbox)  # +1: 버튼 레이아웃 보정
      self.widget_list.insert(new_idx, self.widget_list.pop(idx))

  def add_statistics_widget(self, stats_text=""):
    """
    통계 표시용 위젯 추가
    """
    label = QLabel(stats_text)
    label.setWordWrap(True)
    self.add_dashboard_widget(label, widget_id="stats", title="통계")
    return label

  def add_log_widget(self):
    """
    로그 표시용 QTextEdit 위젯 추가
    """
    log_widget = QTextEdit()
    log_widget.setReadOnly(True)
    self.add_dashboard_widget(log_widget, widget_id="log", title="로그")
    return log_widget

  def add_signal_list_widget(self, signals=None):
    """
    신호 목록 표시용 QListWidget 추가
    """
    list_widget = QListWidget()
    if signals:
      list_widget.addItems(signals)
    self.add_dashboard_widget(list_widget, widget_id="signal_list", title="신호 목록")
    return list_widget

  def remove_dashboard_widget(self, widget):
    """
    대시보드에서 위젯 삭제
    """
    self.layout.removeWidget(widget)
    widget.deleteLater()
    self.widget_list = [w for w in self.widget_list if w['widget'] != widget]

  def save_layout(self):
    """
    현재 위젯 배치 정보를 JSON 파일로 저장 (타입/설정 포함)
    """
    file_path, _ = QFileDialog.getSaveFileName(self, "레이아웃 저장", "", "JSON 파일 (*.json)")
    if file_path:
      try:
        layout_info = []
        for w in self.widget_list:
          info = {'id': w['id'], 'type': w['type']}
          # 주요 설정 저장(플롯: 채널수, 신호목록: 리스트 등)
          if w['type'] == 'RealtimePlotWidget':
            plot = w['widget'].findChild(QWidget)
            info['channel_count'] = getattr(plot, 'channel_count', 1)
            info['buffer_size'] = getattr(plot, 'buffer_size', 10000)
          elif w['type'] == 'QListWidget':
            list_widget = w['widget'].findChild(QListWidget)
            if list_widget:
              info['signals'] = [list_widget.item(i).text() for i in range(list_widget.count())]
          layout_info.append(info)
        with open(file_path, 'w', encoding='utf-8') as f:
          json.dump(layout_info, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "저장 완료", f"레이아웃이 저장되었습니다:\n{file_path}")
      except Exception as e:
        QMessageBox.critical(self, "저장 오류", str(e))

  def load_layout(self):
    """
    저장된 JSON 파일로 위젯 배치 복원 (타입/설정까지 복원)
    """
    file_path, _ = QFileDialog.getOpenFileName(self, "레이아웃 불러오기", "", "JSON 파일 (*.json)")
    if file_path:
      try:
        with open(file_path, 'r', encoding='utf-8') as f:
          layout_info = json.load(f)
        # 기존 위젯 모두 삭제
        for w in self.widget_list:
          self.layout.removeWidget(w['widget'])
          w['widget'].deleteLater()
        self.widget_list.clear()
        # 타입/설정에 따라 위젯 복원
        for info in layout_info:
          t = info.get('type')
          if t == 'RealtimePlotWidget':
            from src.plot_widget import RealtimePlotWidget
            plot = RealtimePlotWidget(
              channel_count=info.get('channel_count', 1),
              buffer_size=info.get('buffer_size', 10000)
            )
            self.add_dashboard_widget(plot, widget_id=info['id'], title="실시간 플롯")
          elif t == 'QListWidget':
            signals = info.get('signals', ["채널 1"])
            self.add_signal_list_widget(signals)
          elif t == 'QLabel':
            self.add_statistics_widget("통계 정보 없음")
          elif t == 'QTextEdit':
            self.add_log_widget()
        QMessageBox.information(self, "불러오기 완료", f"레이아웃을 불러왔습니다:\n{file_path}")
      except Exception as e:
        QMessageBox.critical(self, "불러오기 오류", f"불러오기 오류: {e}")

  # 드래그&드롭 이벤트 핸들러 (예시: 버튼만 지원)
  def dragEnterEvent(self, event):
    if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
      event.acceptProposedAction()

  def dropEvent(self, event):
    # 실제 위젯 드래그&드롭 구현은 커스텀 위젯/모델에 따라 확장 필요
    event.acceptProposedAction()

  def show_plot_settings_dialog(self, plot_widget, groupbox):
    """
    플롯 위젯 설정 다이얼로그(채널 수/버퍼/컬러맵 등) 표시 및 실시간 반영
    """
    dlg = QDialog(self)
    dlg.setWindowTitle("플롯 설정")
    form = QFormLayout(dlg)
    # 채널 수
    spin_channel = QSpinBox()
    spin_channel.setRange(1, 8)
    spin_channel.setValue(getattr(plot_widget, 'channel_count', 1))
    form.addRow("채널 수", spin_channel)
    # 버퍼 크기
    spin_buffer = QSpinBox()
    spin_buffer.setRange(100, 1000000)
    spin_buffer.setValue(getattr(plot_widget, 'buffer_size', 10000))
    form.addRow("버퍼 크기", spin_buffer)
    # 컬러맵
    combo_cmap = QComboBox()
    combo_cmap.addItems(["default", "viridis", "plasma", "magma"])
    form.addRow("컬러맵", combo_cmap)
    # 확인/취소 버튼
    btn_ok = QPushButton("확인")
    btn_cancel = QPushButton("취소")
    btn_layout = QHBoxLayout()
    btn_layout.addWidget(btn_ok)
    btn_layout.addWidget(btn_cancel)
    form.addRow(btn_layout)
    # 컬러맵 현재값 반영
    combo_cmap.setCurrentText(getattr(plot_widget, 'current_colormap', 'default'))
    # 이벤트
    btn_ok.clicked.connect(lambda: self.apply_plot_settings(plot_widget, spin_channel.value(), spin_buffer.value(), combo_cmap.currentText(), dlg))
    btn_cancel.clicked.connect(dlg.reject)
    dlg.exec()

  def apply_plot_settings(self, plot_widget, channel_count, buffer_size, cmap, dlg):
    """
    플롯 설정 적용(채널 수/버퍼/컬러맵 변경)
    """
    # 채널 수/버퍼 크기 변경(재생성 필요)
    if plot_widget.channel_count != channel_count or plot_widget.buffer_size != buffer_size:
      parent = plot_widget.parentWidget()
      layout = parent.layout() if parent else None
      if layout:
        # 기존 플롯 제거 후 새로 추가
        for i in reversed(range(layout.count())):
          w = layout.itemAt(i).widget()
          if w == plot_widget:
            layout.removeWidget(w)
            w.deleteLater()
        from src.plot_widget import RealtimePlotWidget
        new_plot = RealtimePlotWidget(channel_count=channel_count, buffer_size=buffer_size)
        layout.insertWidget(0, new_plot)
        # 컬러맵 적용
        new_plot.set_colormap(cmap)
    else:
      # 컬러맵만 변경
      plot_widget.set_colormap(cmap)
    # 현재 컬러맵 속성 저장(복원용)
    plot_widget.current_colormap = cmap
    dlg.accept()

  def eventFilter(self, obj, event):
    """
    QGroupBox(위젯) 드래그&드롭 순서 변경 처리
    """
    if isinstance(obj, DraggableGroupBox):
      if event.type() == QEvent.Drop:
        src_name = event.mimeData().text()
        dst_name = obj.objectName()
        if src_name != dst_name:
          self._swap_widgets(src_name, dst_name)
        return True
    return super().eventFilter(obj, event)

  def _swap_widgets(self, src_name, dst_name):
    """
    두 QGroupBox의 위치(순서) 교환
    """
    src_idx = next((i for i, w in enumerate(self.widget_list) if w['widget'].objectName() == src_name), -1)
    dst_idx = next((i for i, w in enumerate(self.widget_list) if w['widget'].objectName() == dst_name), -1)
    if src_idx == -1 or dst_idx == -1 or src_idx == dst_idx:
      return
    # 레이아웃에서 위젯 제거 후 재삽입
    src_widget = self.widget_list[src_idx]['widget']
    dst_widget = self.widget_list[dst_idx]['widget']
    self.layout.removeWidget(src_widget)
    self.layout.removeWidget(dst_widget)
    if src_idx < dst_idx:
      self.layout.insertWidget(dst_idx+1, src_widget)
      self.layout.insertWidget(src_idx, dst_widget)
    else:
      self.layout.insertWidget(src_idx+1, dst_widget)
      self.layout.insertWidget(dst_idx, src_widget)
    # 리스트 순서도 교환
    self.widget_list[src_idx], self.widget_list[dst_idx] = self.widget_list[dst_idx], self.widget_list[src_idx]

  def apply_preset(self, preset_name):
    """
    프리셋 이름에 해당하는 대시보드 구성을 적용
    기존 위젯을 모두 삭제하고, 프리셋에 정의된 위젯을 자동 배치
    """
    if preset_name not in self.presets:
      QMessageBox.warning(self, "프리셋 없음", f"'{preset_name}' 프리셋이 존재하지 않습니다.")
      return
    # 기존 위젯 모두 삭제
    for w in self.widget_list[:]:
      self.remove_dashboard_widget(w['widget'])
    # 프리셋에 정의된 위젯 순서대로 추가
    for idx, info in enumerate(self.presets[preset_name]):
      t = info.get('type')
      if t == 'RealtimePlotWidget':
        from src.plot_widget import RealtimePlotWidget
        plot = RealtimePlotWidget(
          channel_count=info.get('channel_count', 1),
          buffer_size=info.get('buffer_size', 10000)
        )
        self.add_dashboard_widget(plot, widget_id=f"plot{idx+1}", title="실시간 플롯")
      elif t == 'QLabel':
        self.add_statistics_widget("통계 정보 없음")
      elif t == 'QTextEdit':
        self.add_log_widget()
      elif t == 'QListWidget':
        signals = info.get('signals', ["채널 1"])
        self.add_signal_list_widget(signals) 