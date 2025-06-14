import unittest
import numpy as np
import os
from src.data_io import save_data, load_data

class TestDataIO(unittest.TestCase):
  def setUp(self):
    # 임시 테스트 데이터 (2채널, 10포인트)
    self.data = np.arange(20).reshape(2, 10)
    self.csv_file = "test_data.csv"
    self.h5_file = "test_data.h5"
    self.invalid_file = "test_data.txt"

  def tearDown(self):
    # 테스트 후 파일 삭제
    for f in [self.csv_file, self.h5_file, self.invalid_file]:
      if os.path.exists(f):
        os.remove(f)

  def test_save_and_load_csv(self):
    """
    CSV 저장 및 불러오기 정상 동작 테스트
    """
    save_data(self.csv_file, self.data)
    loaded = load_data(self.csv_file)
    self.assertTrue(np.allclose(self.data, loaded))

  def test_save_and_load_hdf5(self):
    """
    HDF5 저장 및 불러오기 정상 동작 테스트
    """
    save_data(self.h5_file, self.data)
    loaded = load_data(self.h5_file)
    self.assertTrue(np.allclose(self.data, loaded))

  def test_save_unsupported_format(self):
    """
    지원하지 않는 포맷 저장 시 ValueError 발생 테스트
    """
    with self.assertRaises(ValueError):
      save_data(self.invalid_file, self.data)

  def test_load_unsupported_format(self):
    """
    지원하지 않는 포맷 불러오기 시 ValueError 발생 테스트
    """
    with open(self.invalid_file, "w") as f:
      f.write("dummy")
    with self.assertRaises(ValueError):
      load_data(self.invalid_file)

  def test_load_nonexistent_file(self):
    """
    존재하지 않는 파일 불러오기 시 IOError 발생 테스트
    """
    with self.assertRaises(IOError):
      load_data("not_exist.csv")

if __name__ == "__main__":
  unittest.main() 