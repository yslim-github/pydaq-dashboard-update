# ==========================================================
# [배포/업데이트/코드 서명 안내]
# - 실제 배포 시 PyInstaller 등으로 exe 패키징 권장
# - 자동 업데이트 체크 URL/서버는 운영 환경에 맞게 수정
# - 보안 강화를 위해 코드 서명(Windows: signtool 등) 적용 권장
# ==========================================================
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox, QFileDialog, QHBoxLayout, QFrame, QCheckBox, QGroupBox
from PySide6.QtCore import Qt
from src.daq_worker import DaqDataCollector
from src.plot_widget import RealtimePlotWidget
from src.data_io import save_data, load_data
from src.offline_player import OfflinePlayer
from src.dashboard import DashboardWidget
from src.settings_widget import SettingsWidget
import numpy as np
from src.update_checker import check_update_async
from src.admin_utils import is_user_admin, run_as_admin
from src import __version__

# 메인 윈도우 클래스 정의
class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("PyDAQ Dashboard 예제")
    self.resize(1200, 900)

    # ----------------------
    # 다크/라이트 테마 스타일 적용
    # ----------------------
    self.apply_theme("dark")  # "dark" 또는 "light" 선택 가능

    # 설정 위젯 (다국어/테마/컬러맵)
    self.settings_widget = SettingsWidget()
    # SettingsWidget 시그널 연결
    self.settings_widget.theme_changed.connect(self.apply_theme)
    self.settings_widget.colormap_changed.connect(self.apply_colormap)
    self.settings_widget.language_changed.connect(self.apply_language)

    # 좌측 툴바 (재생/정지/녹화/북마크)
    self.toolbar_frame = QFrame()
    self.toolbar_frame.setFrameShape(QFrame.StyledPanel)
    toolbar_layout = QVBoxLayout()
    self.btn_play = QPushButton("▶")
    self.btn_play.setStyleSheet("background:#27ae60;color:white;font-size:20px;")
    self.btn_stop = QPushButton("■")
    self.btn_stop.setStyleSheet("background:#e17055;color:white;font-size:20px;")
    self.btn_rec = QPushButton("●")
    self.btn_rec.setStyleSheet("background:#d72660;color:white;font-size:20px;")
    self.btn_mark = QPushButton("★")
    self.btn_mark.setStyleSheet("background:#f1c40f;color:#23272e;font-size:20px;")
    for btn in [self.btn_play, self.btn_stop, self.btn_rec, self.btn_mark]:
      btn.setFixedSize(48, 48)
      toolbar_layout.addWidget(btn)
    toolbar_layout.addStretch()
    self.toolbar_frame.setLayout(toolbar_layout)

    # 중앙 플롯 (대시보드)
    self.dashboard = DashboardWidget()
    self.plot_widget = RealtimePlotWidget(channel_count=1, buffer_size=10000)
    self.dashboard.add_dashboard_widget(self.plot_widget, widget_id="plot1", title="실시간 플롯")
    # 통계 위젯 추가
    self.stats_label = self.dashboard.add_statistics_widget("통계 정보 없음")
    # 로그 위젯 추가
    self.log_widget = self.dashboard.add_log_widget()
    # 신호 목록 위젯 추가(예시: 1채널)
    self.signal_list_widget = self.dashboard.add_signal_list_widget(["채널 1"])
    self.offline_player = OfflinePlayer()
    self.offline_player.frame_changed.connect(self.on_offline_frame_changed)
    self.offline_player.hide()

    # 하단 툴바 (마커/스케일/신호 선택)
    self.bottom_frame = QFrame()
    self.bottom_frame.setFrameShape(QFrame.StyledPanel)
    bottom_layout = QHBoxLayout()
    bottom_layout.addWidget(QLabel("Markers:"))
    # 마커/스케일/신호 체크박스 리스트 저장
    self.marker_checkboxes = []
    self.xaxis_checkboxes = []
    self.signal_checkboxes = []
    # 하단 툴바 위젯 생성 및 리스트에 저장
    for i in range(1, 4):
      cb = QCheckBox(f"M{i}")
      cb.setStyleSheet("color:#1971c2;font-weight:bold;")
      cb.stateChanged.connect(lambda state, idx=i: self.on_marker_toggled(idx, state))
      self.marker_checkboxes.append(cb)
      bottom_layout.addWidget(cb)
    bottom_layout.addSpacing(20)
    bottom_layout.addWidget(QLabel("X-Axis:"))
    for mode in ["Auto", "Manual"]:
      cb = QCheckBox(mode)
      cb.setStyleSheet("font-weight:bold;")
      cb.stateChanged.connect(lambda state, m=mode: self.on_xaxis_mode_changed(m, state))
      self.xaxis_checkboxes.append(cb)
      bottom_layout.addWidget(cb)
    bottom_layout.addSpacing(20)
    bottom_layout.addWidget(QLabel("Signals:"))
    for i in range(1, 4):
      cb = QCheckBox(f"S{i}")
      cb.setStyleSheet("color:#d72660;font-weight:bold;")
      cb.stateChanged.connect(lambda state, idx=i: self.on_signal_toggled(idx, state))
      self.signal_checkboxes.append(cb)
      bottom_layout.addWidget(cb)
    bottom_layout.addStretch()
    self.bottom_frame.setLayout(bottom_layout)

    # 상단 설정/상태
    self.status_label = QLabel("DAQ 상태: 대기 중", self)
    self.status_label.setAlignment(Qt.AlignCenter)
    self.data_label = QLabel("수집 데이터: 없음", self)
    self.data_label.setAlignment(Qt.AlignCenter)

    # 전체 레이아웃
    main_layout = QVBoxLayout()
    main_layout.addWidget(self.settings_widget)
    main_layout.addWidget(self.status_label)
    main_layout.addWidget(self.data_label)
    # 중앙부: 좌측 툴바 + 대시보드
    center_layout = QHBoxLayout()
    center_layout.addWidget(self.toolbar_frame)
    center_layout.addWidget(self.dashboard, stretch=1)
    main_layout.addLayout(center_layout)
    main_layout.addWidget(self.offline_player)
    main_layout.addWidget(self.bottom_frame)
    central_widget = QWidget()
    central_widget.setLayout(main_layout)
    self.setCentralWidget(central_widget)

    # DAQ 스레드 객체 초기화 (예시: Dev1/ai0, 실제 환경에 맞게 수정 필요)
    self.daq_thread = DaqDataCollector(device_name="Dev1", channel="ai0", sample_rate=10000, samples_per_read=1000)
    self.daq_thread.data_collected.connect(self.on_data_collected)
    self.daq_thread.error_occurred.connect(self.on_error_occurred)

    # 버튼 이벤트 연결 (함수 분리)
    self.btn_play.clicked.connect(self.start_daq)
    self.btn_stop.clicked.connect(self.stop_daq)
    self.btn_rec.clicked.connect(self.on_record_clicked)
    self.btn_mark.clicked.connect(self.on_mark_clicked)

    # 데이터 버퍼 (그래프와 동기화)
    self.collected_data = np.empty((0,))

  def apply_theme(self, theme="dark"):
    """다크/라이트 테마 및 위젯 스타일 적용 (SettingsWidget 시그널 연동)"""
    if theme == "dark":
      # 다크 테마 QSS
      qss = """
      QWidget {
        background: #23272e;
        color: #f1f1f1;
        font-family: '맑은 고딕', 'Malgun Gothic', Arial, sans-serif;
        font-size: 15px;
      }
      QFrame {
        background: #23272e;
        border: 1px solid #2d3436;
        border-radius: 8px;
      }
      QPushButton {
        background: #353b48;
        color: #f1f1f1;
        border: 1px solid #636e72;
        border-radius: 8px;
        padding: 8px 0;
        font-size: 20px;
        font-weight: bold;
      }
      QPushButton:hover {
        background: #636e72;
        color: #ffe066;
      }
      QPushButton:pressed {
        background: #00b894;
        color: #23272e;
      }
      QCheckBox {
        spacing: 8px;
        font-size: 15px;
      }
      QCheckBox::indicator {
        width: 20px;
        height: 20px;
        border-radius: 6px;
        border: 2px solid #636e72;
        background: #23272e;
      }
      QCheckBox::indicator:checked {
        background: #ffe066;
        border: 2px solid #fdcb6e;
      }
      QCheckBox:hover {
        color: #ffe066;
      }
      QLabel {
        color: #f1f1f1;
        font-size: 15px;
      }
      """
    else:
      # 라이트 테마 QSS
      qss = """
      QWidget {
        background: #f8f9fa;
        color: #23272e;
        font-family: '맑은 고딕', 'Malgun Gothic', Arial, sans-serif;
        font-size: 15px;
      }
      QFrame {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
      }
      QPushButton {
        background: #e9ecef;
        color: #23272e;
        border: 1px solid #adb5bd;
        border-radius: 8px;
        padding: 8px 0;
        font-size: 20px;
        font-weight: bold;
      }
      QPushButton:hover {
        background: #ffe066;
        color: #23272e;
      }
      QPushButton:pressed {
        background: #00b894;
        color: #f8f9fa;
      }
      QCheckBox {
        spacing: 8px;
        font-size: 15px;
      }
      QCheckBox::indicator {
        width: 20px;
        height: 20px;
        border-radius: 6px;
        border: 2px solid #adb5bd;
        background: #f8f9fa;
      }
      QCheckBox::indicator:checked {
        background: #00b894;
        border: 2px solid #00b894;
      }
      QCheckBox:hover {
        color: #00b894;
      }
      QLabel {
        color: #23272e;
        font-size: 15px;
      }
      """
    self.setStyleSheet(qss)
    # 플롯 위젯 배경 등 추가 스타일 적용(예시)
    try:
      self.plot_widget.setBackground("#23272e" if theme == "dark" else "#f8f9fa")
      self.plot_widget.setForeground("#ffe066" if theme == "dark" else "#23272e")
    except Exception:
      pass  # plot_widget이 없거나 오류 시 무시
    # 대시보드 내 위젯(QGroupBox 등) 스타일도 자동 반영됨

  def apply_colormap(self, cmap_name):
    """플롯 컬러맵 변경 (SettingsWidget 시그널 연동, 예시)"""
    try:
      # pyqtgraph 컬러맵 적용 예시 (실제 컬러맵은 plot_widget.py에서 지원 필요)
      # self.plot_widget.set_colormap(cmap_name)
      pass
    except Exception:
      pass

  def apply_language(self, lang):
    """언어 변경 시 UI 텍스트 동적 변경 (신호 목록/로그/통계 포함, 예외처리)"""
    def set_groupbox_title(obj_name, title):
      gb = self.dashboard.findChild(QGroupBox, obj_name)
      if gb is not None:
        gb.setTitle(title)
    if lang == "ko":
      self.status_label.setText("DAQ 상태: 대기 중")
      self.data_label.setText("수집 데이터: 없음")
      self.stats_label.setText("통계 정보 없음")
      set_groupbox_title("plot1", "실시간 플롯")
      set_groupbox_title("stats", "통계")
      set_groupbox_title("log", "로그")
      set_groupbox_title("signal_list", "신호 목록")
      # 신호 목록 항목 한글화 예시
      self.signal_list_widget.clear()
      self.signal_list_widget.addItems(["채널 1"])
    else:
      self.status_label.setText("DAQ Status: Idle")
      self.data_label.setText("No data collected")
      self.stats_label.setText("No statistics")
      set_groupbox_title("plot1", "Realtime Plot")
      set_groupbox_title("stats", "Statistics")
      set_groupbox_title("log", "Log")
      set_groupbox_title("signal_list", "Signal List")
      # 신호 목록 항목 영어화 예시
      self.signal_list_widget.clear()
      self.signal_list_widget.addItems(["Channel 1"])

  def log_event(self, message):
    """로그 위젯에 메시지 추가 (스크롤 자동 하단)"""
    try:
      self.log_widget.append(message)
      self.log_widget.moveCursor(self.log_widget.textCursor().End)
    except Exception:
      pass

  def start_daq(self):
    """
    데이터 수집 스레드 시작
    """
    self.status_label.setText("DAQ 상태: 수집 중...")
    self.btn_play.setEnabled(False)
    self.btn_stop.setEnabled(True)
    self.plot_widget.clear()  # 그래프 초기화
    self.collected_data = np.empty((0,))  # 데이터 버퍼 초기화
    self.offline_player.hide()  # 오프라인 컨트롤러 숨김
    try:
      self.daq_thread.start()
      self.log_event("[INFO] 데이터 수집 시작")
    except Exception as e:
      self.show_error_message(f"DAQ 스레드 시작 오류: {e}")
      self.log_event(f"[ERROR] DAQ 시작 오류: {e}")

  def stop_daq(self):
    """
    데이터 수집 스레드 정지
    """
    self.status_label.setText("DAQ 상태: 정지됨")
    self.btn_play.setEnabled(True)
    self.btn_stop.setEnabled(False)
    self.daq_thread.stop()
    self.log_event("[INFO] 데이터 수집 정지")
    # 전체 통계 기록
    try:
      if self.collected_data.size > 0:
        avg = np.mean(self.collected_data)
        mx = np.max(self.collected_data)
        mn = np.min(self.collected_data)
        self.log_event(f"[STATS] 전체 평균: {avg:.3f}, 최대: {mx:.3f}, 최소: {mn:.3f}")
    except Exception:
      pass

  def on_data_collected(self, data: np.ndarray, timestamp: float):
    """
    데이터 수집 신호 처리 (UI 및 그래프에 표시, 통계/로그/신호 목록 연동)
    """
    self.data_label.setText(f"수집 데이터: {data[:5]} ...")
    self.plot_widget.append_data(data)
    # 통계 위젯 업데이트
    try:
      if data.size > 0:
        avg = np.mean(data)
        mx = np.max(data)
        mn = np.min(data)
        stats = f"평균: {avg:.3f}\n최대: {mx:.3f}\n최소: {mn:.3f}"
        self.stats_label.setText(stats)
      else:
        self.stats_label.setText("통계 정보 없음")
    except Exception as e:
      self.stats_label.setText(f"통계 계산 오류: {e}")
    # 로그 위젯에 데이터 수집 로그 추가
    try:
      self.log_widget.append(f"[{timestamp:.2f}] 데이터 수집: {data[:5]} ...")
    except Exception:
      pass
    # 신호 목록 위젯(예시: 1채널, 실제 신호명/상태 연동)
    try:
      self.signal_list_widget.clear()
      # 예시: 1채널, 활성화 상태 표시
      self.signal_list_widget.addItem("채널 1 (활성)")
    except Exception:
      pass
    # 데이터 버퍼에 누적 (1차원/2차원 모두 지원)
    if self.collected_data.size == 0:
      self.collected_data = data.flatten()
    else:
      self.collected_data = np.concatenate([self.collected_data, data.flatten()])

  def save_data_to_file(self):
    """
    파일 다이얼로그로 데이터 저장
    """
    if self.collected_data.size == 0:
      self.show_error_message("저장할 데이터가 없습니다.")
      return
    file_path, _ = QFileDialog.getSaveFileName(self, "데이터 저장", "", "CSV 파일 (*.csv);;HDF5 파일 (*.h5 *.hdf5)")
    if file_path:
      try:
        save_data(file_path, self.collected_data)
        QMessageBox.information(self, "저장 완료", f"데이터가 저장되었습니다:\n{file_path}")
      except Exception as e:
        self.show_error_message(str(e))

  def load_data_from_file(self):
    """
    파일 다이얼로그로 데이터 불러오기 및 그래프/버퍼/오프라인 컨트롤러 반영
    """
    file_path, _ = QFileDialog.getOpenFileName(self, "데이터 불러오기", "", "CSV 파일 (*.csv);;HDF5 파일 (*.h5 *.hdf5)")
    if file_path:
      try:
        data = load_data(file_path)
        self.collected_data = data
        self.plot_widget.clear()
        self.plot_widget.append_data(data)
        self.offline_player.set_data(data)
        self.offline_player.show()
        QMessageBox.information(self, "불러오기 완료", f"데이터를 불러왔습니다:\n{file_path}")
      except Exception as e:
        self.show_error_message(str(e))

  def on_offline_frame_changed(self, frame_idx, frame_data):
    """
    오프라인 재생 시 프레임 변경 신호 처리 (그래프에 해당 프레임만 표시)
    """
    # frame_data shape: (채널,) 또는 (채널, 1)
    # 그래프에 해당 프레임만 표시
    if frame_data.ndim == 1:
      frame_data = frame_data.reshape(-1, 1)
    self.plot_widget.clear()
    self.plot_widget.append_data(frame_data)
    self.data_label.setText(f"오프라인 재생 프레임: {frame_idx+1}")

  def on_error_occurred(self, message: str):
    self.show_error_message(message)
    self.log_event(f"[ERROR] {message}")

  def show_error_message(self, message: str):
    QMessageBox.critical(self, "오류", message)

  # ----------------------
  # 툴바/하단바 기능 함수
  # ----------------------
  def on_record_clicked(self):
    """녹화 버튼 클릭 시 동작 (예외처리 포함)"""
    try:
      # TODO: 실제 녹화 기능 구현 필요
      QMessageBox.information(self, "녹화", "녹화 기능은 추후 지원 예정입니다.")
    except Exception as e:
      QMessageBox.critical(self, "에러", f"녹화 중 오류 발생: {e}")

  def on_mark_clicked(self):
    """북마크(마커) 버튼 클릭 시 플롯에 주석 추가 및 해당 시점 통계 로그 기록"""
    try:
      self.plot_widget.add_annotation(self.plot_widget.ptr, 0, "★ Marker", color="#f1c40f")
      # 북마크 시점 통계 기록
      if self.collected_data.size > 0:
        avg = np.mean(self.collected_data)
        mx = np.max(self.collected_data)
        mn = np.min(self.collected_data)
        self.log_event(f"[MARK] 북마크 시점 통계: 평균={avg:.3f}, 최대={mx:.3f}, 최소={mn:.3f}")
    except Exception as e:
      QMessageBox.critical(self, "에러", f"마커 추가 중 오류 발생: {e}")
      self.log_event(f"[ERROR] 마커 추가 오류: {e}")

  def on_marker_toggled(self, marker_idx, state):
    """마커 체크박스 토글 시 동작"""
    # 한글 주석: 마커 표시/해제 로직 구현 (예시)
    try:
      if state == Qt.Checked:
        # TODO: 해당 마커 활성화
        print(f"마커 {marker_idx} 활성화")
      else:
        # TODO: 해당 마커 비활성화
        print(f"마커 {marker_idx} 비활성화")
    except Exception as e:
      QMessageBox.critical(self, "에러", f"마커 토글 오류: {e}")

  def on_xaxis_mode_changed(self, mode, state):
    """X축 스케일 모드 변경 시 동작"""
    try:
      if state == Qt.Checked:
        # 한글 주석: Auto/Manual 중복 체크 방지
        for cb in self.xaxis_checkboxes:
          if cb.text() != mode:
            cb.setChecked(False)
        print(f"X축 모드: {mode}")
    except Exception as e:
      QMessageBox.critical(self, "에러", f"X축 모드 변경 오류: {e}")

  def on_signal_toggled(self, signal_idx, state):
    """신호 선택 체크박스 토글 시 동작"""
    try:
      if state == Qt.Checked:
        # TODO: 해당 신호 표시
        print(f"신호 {signal_idx} 표시")
      else:
        # TODO: 해당 신호 숨김
        print(f"신호 {signal_idx} 숨김")
    except Exception as e:
      QMessageBox.critical(self, "에러", f"신호 토글 오류: {e}")

if __name__ == "__main__":
  # 관리자 권한 확인 및 필요 시 UAC 프롬프트
  if not is_user_admin():
    # 관리자 권한이 아니면 UAC 프롬프트로 재실행 시도
    try:
      run_as_admin()
    except Exception as e:
      QMessageBox.critical(None, "권한 오류", f"관리자 권한이 필요합니다.\n{e}")
      sys.exit(1)

  # QApplication 객체 생성
  app = QApplication(sys.argv)

  # 메인 윈도우 생성 및 표시
  window = MainWindow()
  window.show()

  # 앱 실행 시 자동 업데이트 체크 (예시 URL, 실제 배포 시 서버 주소로 변경)
  version_url = "https://github.com/yslim-github/pydaq-dashboard-update/version.json"  # 실제 배포 시 수정
  check_update_async(window, __version__, version_url)

  # 이벤트 루프 실행
  sys.exit(app.exec()) 