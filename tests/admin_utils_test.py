import unittest
from src import admin_utils

class TestAdminUtils(unittest.TestCase):
  def test_is_user_admin(self):
    # 실제 관리자 권한 여부는 환경에 따라 다름 (모킹 필요)
    result = admin_utils.is_user_admin()
    self.assertIsInstance(result, bool)

  def test_run_as_admin(self):
    # 실제 UAC 프롬프트는 테스트에서 실행하지 않음 (모킹 필요)
    pass

if __name__ == '__main__':
  unittest.main() 