import unittest
import os
import json
from PySide6.QtWidgets import QApplication, QPushButton, QMessageBox, QFileDialog
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
import sys
import traceback

# 메인 윈도우 임포트
sys.path.insert(0, '../src')
from main import MainWindow

app = QApplication.instance() or QApplication(sys.argv)

class TestDashboardWidget(unittest.TestCase):
  def setUp(self):
    self.dashboard = DashboardWidget()
    self.btn1 = QPushButton("위젯1")
    self.btn2 = QPushButton("위젯2")
    self.dashboard.add_dashboard_widget(self.btn1, widget_id="w1")
    self.dashboard.add_dashboard_widget(self.btn2, widget_id="w2")
    self.layout_file = "test_layout.json"

  def tearDown(self):
    if os.path.exists(self.layout_file):
      os.remove(self.layout_file)

  def test_add_and_remove_widget(self):
    """
    위젯 추가/삭제 동작 테스트
    """
    self.assertEqual(len(self.dashboard.widget_list), 2)
    self.dashboard.remove_dashboard_widget(self.btn1)
    self.assertEqual(len(self.dashboard.widget_list), 1)

  def test_save_and_load_layout(self):
    """
    레이아웃 저장/불러오기 동작 테스트
    """
    layout_info = [{'id': w['id']} for w in self.dashboard.widget_list]
    with open(self.layout_file, 'w', encoding='utf-8') as f:
      json.dump(layout_info, f)
    # 기존 위젯 삭제
    for w in self.dashboard.widget_list[:]:
      self.dashboard.remove_dashboard_widget(w['widget'])
    self.assertEqual(len(self.dashboard.widget_list), 0)
    # 레이아웃 불러오기 (예시: 버튼으로 복원)
    with open(self.layout_file, 'r', encoding='utf-8') as f:
      loaded = json.load(f)
    for info in loaded:
      btn = QPushButton(f"위젯 {info['id']}")
      self.dashboard.add_dashboard_widget(btn, widget_id=info['id'])
    self.assertEqual(len(self.dashboard.widget_list), 2)

  def test_add_duplicate_id(self):
    """
    중복 id로 위젯 추가 시 리스트에 중복 id가 들어가는지 확인(허용/비허용 정책에 따라 다름)
    """
    btn3 = QPushButton("위젯3")
    self.dashboard.add_dashboard_widget(btn3, widget_id="w1")
    ids = [w['id'] for w in self.dashboard.widget_list]
    # 현재 정책상 중복 허용(append), 중복 id가 2개 이상 존재
    self.assertTrue(ids.count("w1") >= 2)

  def test_load_invalid_layout_file(self):
    """
    잘못된 JSON 파일 불러오기 시 예외 발생 없이 오류 메시지 표시
    """
    with open(self.layout_file, 'w', encoding='utf-8') as f:
      f.write("not a json")
    called = {}
    def fake_critical(parent, title, msg):
      called['msg'] = msg
    orig_critical = QMessageBox.critical
    orig_getopen = QFileDialog.getOpenFileName
    QMessageBox.critical = fake_critical
    QFileDialog.getOpenFileName = lambda *a, **k: (self.layout_file, None)
    try:
      self.dashboard.load_layout()
      self.assertIn("불러오기 오류", called['msg'])
    finally:
      QMessageBox.critical = orig_critical
      QFileDialog.getOpenFileName = orig_getopen

class TestToolbarAndBottomBar(unittest.TestCase):
  def setUp(self):
    self.window = MainWindow()
    self.window.show()

  def tearDown(self):
    self.window.close()

  def test_toolbar_buttons(self):
    """툴바 버튼(재생/정지/녹화/북마크) 클릭 동작 테스트"""
    # 재생 버튼 클릭
    QTest.mouseClick(self.window.btn_play, Qt.LeftButton)
    self.assertFalse(self.window.btn_play.isEnabled())
    self.assertTrue(self.window.btn_stop.isEnabled())
    # 정지 버튼 클릭
    QTest.mouseClick(self.window.btn_stop, Qt.LeftButton)
    self.assertTrue(self.window.btn_play.isEnabled())
    self.assertFalse(self.window.btn_stop.isEnabled())
    # 녹화 버튼 클릭(예외 없음)
    try:
      QTest.mouseClick(self.window.btn_rec, Qt.LeftButton)
    except Exception:
      self.fail("녹화 버튼 클릭 시 예외 발생")
    # 북마크 버튼 클릭(예외 없음)
    try:
      QTest.mouseClick(self.window.btn_mark, Qt.LeftButton)
    except Exception:
      self.fail("북마크 버튼 클릭 시 예외 발생")

  def test_marker_checkboxes(self):
    """마커 체크박스 토글 동작 테스트"""
    for i, cb in enumerate(self.window.marker_checkboxes):
      QTest.mouseClick(cb, Qt.LeftButton)
      self.assertTrue(cb.isChecked())
      QTest.mouseClick(cb, Qt.LeftButton)
      self.assertFalse(cb.isChecked())

  def test_xaxis_checkboxes(self):
    """X축 스케일 체크박스(중복 방지) 테스트"""
    auto_cb, manual_cb = self.window.xaxis_checkboxes
    QTest.mouseClick(auto_cb, Qt.LeftButton)
    self.assertTrue(auto_cb.isChecked())
    self.assertFalse(manual_cb.isChecked())
    QTest.mouseClick(manual_cb, Qt.LeftButton)
    self.assertTrue(manual_cb.isChecked())
    self.assertFalse(auto_cb.isChecked())

  def test_signal_checkboxes(self):
    """신호 선택 체크박스 토글 동작 테스트"""
    for i, cb in enumerate(self.window.signal_checkboxes):
      QTest.mouseClick(cb, Qt.LeftButton)
      self.assertTrue(cb.isChecked())
      QTest.mouseClick(cb, Qt.LeftButton)
      self.assertFalse(cb.isChecked())

if __name__ == "__main__":
  unittest.main() 