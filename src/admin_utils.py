import sys
import os
import ctypes
import subprocess

# 현재 프로세스가 관리자 권한인지 확인하는 함수
def is_user_admin() -> bool:
  """
  현재 프로세스가 관리자 권한으로 실행 중인지 확인합니다.
  Windows가 아니면 항상 True 반환.
  """
  if os.name != 'nt':
    return True
  try:
    return ctypes.windll.shell32.IsUserAnAdmin() != 0
  except Exception as e:
    print(f"[관리자 권한 확인 오류] {e}")
    return False

# 관리자 권한으로 재실행하는 함수
def run_as_admin(argv=None, wait=True):
  """
  관리자 권한이 필요할 때 UAC 프롬프트를 띄워 재실행합니다.
  """
  if os.name != 'nt':
    raise RuntimeError('Windows에서만 지원됩니다.')
  if argv is None:
    argv = sys.argv
  try:
    params = ' '.join([f'"{x}"' for x in argv])
    # ShellExecuteEx로 관리자 권한 실행
    proc_info = ctypes.windll.shell32.ShellExecuteW(
      None, "runas", sys.executable, params, None, 1
    )
    if int(proc_info) <= 32:
      raise RuntimeError('UAC 권한 상승 실패')
    if wait:
      os._exit(0)
    return True
  except Exception as e:
    print(f"[UAC 프롬프트 오류] {e}")
    return False 