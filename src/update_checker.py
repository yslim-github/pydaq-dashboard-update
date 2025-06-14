import sys
import threading
import requests
from PySide6.QtWidgets import QMessageBox

# 최신 버전 정보를 가져오는 함수
# (실제 배포 시에는 서버 또는 GitHub Release 등에서 버전 정보를 받아오도록 수정)
def fetch_latest_version_info(version_url: str) -> dict:
  """
  최신 버전 정보를 서버에서 받아옵니다.
  오류 발생 시 None 반환
  """
  try:
    response = requests.get(version_url, timeout=5)
    response.raise_for_status()
    return response.json()
  except Exception as e:
    print(f"[업데이트 체크 오류] {e}")
    return None

# 버전 문자열을 비교하는 함수
def is_newer_version(current_version: str, latest_version: str) -> bool:
  """
  버전 문자열(예: '1.2.3')을 비교하여 최신 버전 여부를 반환합니다.
  """
  def parse_version(v):
    return tuple(map(int, (v.split("."))))
  try:
    return parse_version(latest_version) > parse_version(current_version)
  except Exception:
    return False

# 업데이트 알림 다이얼로그 표시 함수
def show_update_dialog(parent, latest_version: str, release_notes: str = ""):
  """
  새 버전이 있을 때 사용자에게 알림을 표시합니다.
  """
  msg = QMessageBox(parent)
  msg.setIcon(QMessageBox.Information)
  msg.setWindowTitle("업데이트 알림")
  msg.setText(f"새 버전({latest_version})이(가) 출시되었습니다!")
  if release_notes:
    msg.setInformativeText(release_notes)
  msg.setStandardButtons(QMessageBox.Ok)
  msg.exec()

# 비동기 업데이트 체크 스레드 함수
def check_update_async(parent, current_version: str, version_url: str):
  """
  별도 스레드에서 업데이트를 체크하고, 새 버전이 있으면 알림을 띄웁니다.
  """
  def worker():
    info = fetch_latest_version_info(version_url)
    if info and 'version' in info:
      latest_version = info['version']
      release_notes = info.get('notes', "")
      if is_newer_version(current_version, latest_version):
        # UI 스레드에서 다이얼로그 표시
        from PySide6.QtCore import QMetaObject, Qt
        QMetaObject.invokeMethod(
          parent,
          lambda: show_update_dialog(parent, latest_version, release_notes),
          Qt.QueuedConnection
        )
  threading.Thread(target=worker, daemon=True).start() 