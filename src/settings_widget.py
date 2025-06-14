from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox
from PySide6.QtCore import QTranslator, QLocale, QLibraryInfo, Signal
import json
import os

class SettingsWidget(QWidget):
  """
  다국어(한/영) 및 컬러맵/테마 설정 위젯
  - 언어/테마 선택, 설정 저장/불러오기 지원
  - 테마/언어/컬러맵 변경 시그널 제공
  """
  # 테마/언어/컬러맵 변경 시그널
  theme_changed = Signal(str)
  language_changed = Signal(str)
  colormap_changed = Signal(str)

  def __init__(self, parent=None):
    super().__init__(parent)
    self.settings_file = "user_settings.json"
    self.translator = QTranslator()
    self.current_language = "ko"
    self.current_theme = "light"
    self.current_colormap = "default"

    # UI 구성
    layout = QHBoxLayout()
    layout.addWidget(QLabel("언어:"))
    self.lang_combo = QComboBox()
    self.lang_combo.addItems(["한국어", "English"])
    layout.addWidget(self.lang_combo)
    layout.addWidget(QLabel("테마:"))
    self.theme_combo = QComboBox()
    self.theme_combo.addItems(["light", "dark"])
    layout.addWidget(self.theme_combo)
    layout.addWidget(QLabel("컬러맵:"))
    self.colormap_combo = QComboBox()
    self.colormap_combo.addItems(["default", "viridis", "plasma", "magma"])
    layout.addWidget(self.colormap_combo)
    self.save_btn = QPushButton("설정 저장")
    layout.addWidget(self.save_btn)
    self.setLayout(layout)

    # 이벤트 연결
    self.lang_combo.currentIndexChanged.connect(self.change_language)
    self.theme_combo.currentIndexChanged.connect(self.change_theme)
    self.colormap_combo.currentIndexChanged.connect(self.change_colormap)
    self.save_btn.clicked.connect(self.save_settings)

    # 설정 불러오기
    self.load_settings()

  def change_language(self):
    """
    언어 변경 (시그널 emit 및 자동 저장)
    """
    idx = self.lang_combo.currentIndex()
    if idx == 0:
      self.current_language = "ko"
    else:
      self.current_language = "en"
    self.language_changed.emit(self.current_language)
    self.save_settings()  # 변경 시 자동 저장

  def change_theme(self):
    """
    테마 변경 (시그널 emit 및 자동 저장)
    """
    self.current_theme = self.theme_combo.currentText()
    self.theme_changed.emit(self.current_theme)
    self.save_settings()  # 변경 시 자동 저장

  def change_colormap(self):
    """
    컬러맵 변경 (시그널 emit 및 자동 저장)
    """
    self.current_colormap = self.colormap_combo.currentText()
    self.colormap_changed.emit(self.current_colormap)
    self.save_settings()  # 변경 시 자동 저장

  def save_settings(self):
    """
    현재 설정을 JSON 파일로 저장
    """
    settings = {
      "language": self.current_language,
      "theme": self.current_theme,
      "colormap": self.current_colormap
    }
    try:
      with open(self.settings_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
      QMessageBox.information(self, "저장 완료", "설정이 저장되었습니다.")
    except Exception as e:
      QMessageBox.critical(self, "저장 오류", str(e))

  def load_settings(self):
    """
    저장된 설정을 불러와 UI에 반영 (앱 시작 시 자동 복원)
    """
    if not os.path.exists(self.settings_file):
      return
    try:
      with open(self.settings_file, "r", encoding="utf-8") as f:
        settings = json.load(f)
      lang_idx = 0 if settings.get("language", "ko") == "ko" else 1
      self.lang_combo.setCurrentIndex(lang_idx)
      theme_idx = self.theme_combo.findText(settings.get("theme", "light"))
      if theme_idx >= 0:
        self.theme_combo.setCurrentIndex(theme_idx)
      cmap_idx = self.colormap_combo.findText(settings.get("colormap", "default"))
      if cmap_idx >= 0:
        self.colormap_combo.setCurrentIndex(cmap_idx)
    except Exception as e:
      QMessageBox.critical(self, "불러오기 오류", f"불러오기 오류: {e}") 