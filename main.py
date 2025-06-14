# ==========================================================
# [배포/업데이트/코드 서명 안내]
# - 실제 배포 시 PyInstaller 등으로 exe 패키징 권장
# - 자동 업데이트 체크 URL/서버는 운영 환경에 맞게 수정
# - 보안 강화를 위해 코드 서명(Windows: signtool 등) 적용 권장
# ==========================================================
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox, QFileDialog, QHBoxLayout
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
    self.resize(1000, 850)

    # 설정 위젯 (다국어/테마/컬러맵)
    self.settings_widget = SettingsWidget()

    # UI 구성
    self.status_label = QLabel("DAQ 상태: 대기 중", self)
    self.status_label.setAlignment(Qt.AlignCenter)
    self.data_label = QLabel("수집 데이터: 없음", self)
    self.data_label.setAlignment(Qt.AlignCenter)
    self.start_button = QPushButton("데이터 수집 시작", self)
    self.stop_button = QPushButton("데이터 수집 정지", self)
    self.stop_button.setEnabled(False)
    self.save_button = QPushButton("데이터 저장", self)
    self.load_button = QPushButton("데이터 불러오기", self)

    # 대시보드 컨테이너
    self.dashboard = DashboardWidget()
    # 실시간 플로팅 위젯(1채널, 10000포인트 버퍼) 예시로 대시보드에 추가
    self.plot_widget = RealtimePlotWidget(channel_count=1, buffer_size=10000)
    self.dashboard.add_dashboard_widget(self.plot_widget, widget_id="plot1")
    # 오프라인 재생 컨트롤러
    self.offline_player = OfflinePlayer()
    self.offline_player.frame_changed.connect(self.on_offline_frame_changed)
    self.offline_player.hide()  # 기본은 숨김

    # 레이아웃 설정
    layout = QVBoxLayout()
    layout.addWidget(self.settings_widget)
    layout.addWidget(self.status_label)
    layout.addWidget(self.data_label)
    layout.addWidget(self.dashboard)
    layout.addWidget(self.offline_player)
    btn_layout = QHBoxLayout()
    btn_layout.addWidget(self.start_button)
    btn_layout.addWidget(self.stop_button)
    btn_layout.addWidget(self.save_button)
    btn_layout.addWidget(self.load_button)
    layout.addLayout(btn_layout)
    central_widget = QWidget()
    central_widget.setLayout(layout)
    self.setCentralWidget(central_widget)

    # DAQ 스레드 객체 초기화 (예시: Dev1/ai0, 실제 환경에 맞게 수정 필요)
    self.daq_thread = DaqDataCollector(device_name="Dev1", channel="ai0", sample_rate=10000, samples_per_read=1000)
    # 신호 연결
    self.daq_thread.data_collected.connect(self.on_data_collected)
    self.daq_thread.error_occurred.connect(self.on_error_occurred)

    # 버튼 이벤트 연결
    self.start_button.clicked.connect(self.start_daq)
    self.stop_button.clicked.connect(self.stop_daq)
    self.save_button.clicked.connect(self.save_data_to_file)
    self.load_button.clicked.connect(self.load_data_from_file)

    # 데이터 버퍼 (그래프와 동기화)
    self.collected_data = np.empty((0,))

  def start_daq(self):
    """
    데이터 수집 스레드 시작
    """
    self.status_label.setText("DAQ 상태: 수집 중...")
    self.start_button.setEnabled(False)
    self.stop_button.setEnabled(True)
    self.plot_widget.clear()  # 그래프 초기화
    self.collected_data = np.empty((0,))  # 데이터 버퍼 초기화
    self.offline_player.hide()  # 오프라인 컨트롤러 숨김
    try:
      self.daq_thread.start()
    except Exception as e:
      self.show_error_message(f"DAQ 스레드 시작 오류: {e}")

  def stop_daq(self):
    """
    데이터 수집 스레드 정지
    """
    self.status_label.setText("DAQ 상태: 정지됨")
    self.start_button.setEnabled(True)
    self.stop_button.setEnabled(False)
    self.daq_thread.stop()

  def on_data_collected(self, data: np.ndarray, timestamp: float):
    """
    데이터 수집 신호 처리 (UI 및 그래프에 표시)
    """
    # 데이터의 첫 5개 값만 표시
    preview = ", ".join(f"{v:.3f}" for v in data[:5])
    self.data_label.setText(f"수집 데이터: {preview} ... (총 {len(data)}개)")
    # 그래프에 데이터 추가
    self.plot_widget.append_data(data)
    # 데이터 버퍼에 누적 (1차원/2차원 모두 지원)
    if self.collected_data.size == 0:
      self.collected_data = data.copy()
    else:
      try:
        self.collected_data = np.concatenate([self.collected_data, data], axis=-1)
      except Exception:
        pass  # 데이터 shape 불일치 등 예외 무시

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
    """
    에러 신호 처리 (메시지 박스 표시)
    """
    self.show_error_message(message)
    self.stop_daq()

  def show_error_message(self, message: str):
    QMessageBox.critical(self, "오류", message)

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