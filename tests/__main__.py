"""
테스트 자동 실행 스크립트
- tests 디렉토리 내 모든 unittest 모듈을 자동으로 실행합니다.
"""
import unittest
import os
import sys

if __name__ == "__main__":
  # 현재 디렉토리를 sys.path에 추가
  sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
  # 테스트 디스커버리 및 실행
  loader = unittest.TestLoader()
  suite = loader.discover('.', pattern='*_test.py')
  runner = unittest.TextTestRunner(verbosity=2)
  result = runner.run(suite)
  # 실패 시 종료 코드 1 반환
  sys.exit(not result.wasSuccessful()) 