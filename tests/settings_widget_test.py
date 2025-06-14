import unittest
import os
import json
from src.settings_widget import SettingsWidget
from PySide6.QtWidgets import QApplication, QMessageBox
import sys

app = QApplication.instance() or QApplication(sys.argv)

class TestSettingsWidget(unittest.TestCase):
  def setUp(self):
    self.widget = SettingsWidget()
    self.settings_file = self.widget.settings_file
    # 테스트용 파일명으로 변경
    self.widget.settings_file = "test_user_settings.json"

  def tearDown(self):
    if os.path.exists(self.widget.settings_file):
      os.remove(self.widget.settings_file)

  def test_change_and_save_load_settings(self):
    """
    언어/테마/컬러맵 변경 및 저장/불러오기 동작 테스트
    """
    self.widget.lang_combo.setCurrentIndex(1)  # English
    self.widget.theme_combo.setCurrentIndex(1)  # dark
    self.widget.colormap_combo.setCurrentIndex(2)  # plasma
    self.widget.save_settings()
    # 저장된 파일 확인
    with open(self.widget.settings_file, "r", encoding="utf-8") as f:
      settings = json.load(f)
    self.assertEqual(settings["language"], "en")
    self.assertEqual(settings["theme"], "dark")
    self.assertEqual(settings["colormap"], "plasma")
    # 불러오기 동작 확인
    self.widget.lang_combo.setCurrentIndex(0)
    self.widget.theme_combo.setCurrentIndex(0)
    self.widget.colormap_combo.setCurrentIndex(0)
    self.widget.load_settings()
    self.assertEqual(self.widget.lang_combo.currentIndex(), 1)
    self.assertEqual(self.widget.theme_combo.currentIndex(), 1)
    self.assertEqual(self.widget.colormap_combo.currentIndex(), 2)
    # 내부 상태도 일치하는지 확인
    self.assertEqual(self.widget.current_language, "en")
    self.assertEqual(self.widget.current_theme, "dark")
    self.assertEqual(self.widget.current_colormap, "plasma")

  def test_invalid_settings_file(self):
    """
    잘못된 JSON 파일 불러오기 시 예외 발생 없이 오류 메시지 표시
    """
    with open(self.widget.settings_file, "w", encoding="utf-8") as f:
      f.write("not a json")
    called = {}
    def fake_critical(parent, title, msg):
      called['msg'] = msg
    orig_critical = QMessageBox.critical
    QMessageBox.critical = fake_critical
    try:
      self.widget.load_settings()
      self.assertTrue('msg' in called, "QMessageBox.critical이 호출되지 않았습니다.")
      self.assertIn("불러오기 오류", called['msg'])
    finally:
      QMessageBox.critical = orig_critical

  def test_combo_change_updates_state(self):
    """
    콤보박스 변경 시 내부 상태(current_language, current_theme, current_colormap) 동기화 테스트
    """
    self.widget.lang_combo.setCurrentIndex(0)
    self.assertEqual(self.widget.current_language, "ko")
    self.widget.lang_combo.setCurrentIndex(1)
    self.assertEqual(self.widget.current_language, "en")
    self.widget.theme_combo.setCurrentIndex(1)
    self.assertEqual(self.widget.current_theme, "dark")
    self.widget.colormap_combo.setCurrentIndex(3)
    self.assertEqual(self.widget.current_colormap, "magma")

if __name__ == "__main__":
  unittest.main() 