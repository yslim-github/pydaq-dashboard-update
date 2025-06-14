from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
import json

class DashboardWidget(QWidget):
  """
  대시보드 컨테이너 위젯
  - 위젯 드래그&드롭, 추가/삭제/배치 지원
  - 레이아웃 저장/불러오기 지원
  """
  def __init__(self, parent=None):
    super().__init__(parent)
    self.setAcceptDrops(True)
    self.layout = QVBoxLayout()
    self.setLayout(self.layout)
    self.widget_list = []  # 현재 배치된 위젯 목록

    # 레이아웃 저장/불러오기 버튼
    btn_layout = QHBoxLayout()
    self.save_btn = QPushButton("레이아웃 저장")
    self.load_btn = QPushButton("레이아웃 불러오기")
    btn_layout.addWidget(self.save_btn)
    btn_layout.addWidget(self.load_btn)
    self.layout.addLayout(btn_layout)

    self.save_btn.clicked.connect(self.save_layout)
    self.load_btn.clicked.connect(self.load_layout)

  def add_dashboard_widget(self, widget, widget_id=None):
    """
    대시보드에 위젯 추가
    """
    self.layout.addWidget(widget)
    self.widget_list.append({'id': widget_id or str(id(widget)), 'widget': widget})
    widget.setObjectName(widget_id or str(id(widget)))
    widget.setAttribute(Qt.WA_DeleteOnClose)

  def remove_dashboard_widget(self, widget):
    """
    대시보드에서 위젯 삭제
    """
    self.layout.removeWidget(widget)
    widget.deleteLater()
    self.widget_list = [w for w in self.widget_list if w['widget'] != widget]

  def save_layout(self):
    """
    현재 위젯 배치 정보를 JSON 파일로 저장
    """
    file_path, _ = QFileDialog.getSaveFileName(self, "레이아웃 저장", "", "JSON 파일 (*.json)")
    if file_path:
      try:
        layout_info = [{'id': w['id']} for w in self.widget_list]
        with open(file_path, 'w', encoding='utf-8') as f:
          json.dump(layout_info, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "저장 완료", f"레이아웃이 저장되었습니다:\n{file_path}")
      except Exception as e:
        QMessageBox.critical(self, "저장 오류", str(e))

  def load_layout(self):
    """
    저장된 JSON 파일로 위젯 배치 복원 (위젯은 예시로 버튼으로 대체)
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
        # 예시: 버튼 위젯으로 복원
        for info in layout_info:
          btn = QPushButton(f"위젯 {info['id']}")
          self.add_dashboard_widget(btn, widget_id=info['id'])
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