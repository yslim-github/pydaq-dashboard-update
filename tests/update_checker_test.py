import unittest
from src import update_checker

class TestUpdateChecker(unittest.TestCase):
  def test_fetch_latest_version_info(self):
    # 실제 네트워크 호출 대신 모킹 필요
    pass

  def test_is_newer_version(self):
    self.assertTrue(update_checker.is_newer_version('1.0.0', '1.1.0'))
    self.assertFalse(update_checker.is_newer_version('1.2.0', '1.1.0'))
    self.assertFalse(update_checker.is_newer_version('1.0.0', '1.0.0'))

  def test_show_update_dialog(self):
    # GUI 다이얼로그는 수동 테스트 또는 모킹 필요
    pass

  def test_check_update_async(self):
    # 비동기 동작, 네트워크 모킹 필요
    pass

if __name__ == '__main__':
  unittest.main() 