import unittest
import numpy as np
import os
from src.signal_pipeline import apply_fft, apply_fir_lowpass, apply_iir_lowpass, calc_stats, run_plugin

class TestSignalPipeline(unittest.TestCase):
  def setUp(self):
    # 2채널, 100포인트 테스트 신호
    t = np.linspace(0, 1, 100, endpoint=False)
    self.data = np.vstack([np.sin(2*np.pi*5*t), np.cos(2*np.pi*5*t)])

  def test_fft(self):
    """
    FFT 변환 정상 동작 테스트
    """
    fft_result = apply_fft(self.data)
    self.assertEqual(fft_result.shape, self.data.shape)

  def test_fft_invalid_input(self):
    """
    잘못된 입력(리스트 등) 시 RuntimeError 발생 테스트
    """
    with self.assertRaises(RuntimeError):
      apply_fft([1,2,3])

  def test_fir_lowpass(self):
    """
    FIR 저역통과 필터 정상 동작 테스트
    """
    filtered = apply_fir_lowpass(self.data, cutoff_hz=10, fs=100)
    self.assertEqual(filtered.shape, self.data.shape)

  def test_fir_lowpass_invalid(self):
    """
    잘못된 cutoff 주파수 등 입력 시 RuntimeError 발생 테스트
    """
    with self.assertRaises(RuntimeError):
      apply_fir_lowpass(self.data, cutoff_hz=-1, fs=100)

  def test_iir_lowpass(self):
    """
    IIR 저역통과 필터 정상 동작 테스트
    """
    filtered = apply_iir_lowpass(self.data, cutoff_hz=10, fs=100)
    self.assertEqual(filtered.shape, self.data.shape)

  def test_iir_lowpass_invalid(self):
    """
    잘못된 cutoff 주파수 등 입력 시 RuntimeError 발생 테스트
    """
    with self.assertRaises(RuntimeError):
      apply_iir_lowpass(self.data, cutoff_hz=-1, fs=100)

  def test_stats(self):
    """
    통계 분석 함수 정상 동작 테스트
    """
    stats = calc_stats(self.data)
    self.assertIn('mean', stats)
    self.assertIn('std', stats)
    self.assertIn('min', stats)
    self.assertIn('max', stats)

  def test_stats_invalid(self):
    """
    잘못된 입력(빈 배열 등) 시 RuntimeError 발생 테스트
    """
    with self.assertRaises(RuntimeError):
      calc_stats(np.array([]))

  def test_run_plugin(self):
    """
    플러그인 정상 실행 테스트
    """
    plugin_code = """
def process(data):
  import numpy as np
  return data * 2
"""
    plugin_path = "temp_plugin.py"
    with open(plugin_path, "w", encoding="utf-8") as f:
      f.write(plugin_code)
    try:
      result = run_plugin(plugin_path, self.data)
      self.assertTrue(np.allclose(result, self.data * 2))
    finally:
      os.remove(plugin_path)

  def test_run_plugin_not_found(self):
    """
    플러그인 파일이 없을 때 FileNotFoundError 발생 테스트
    """
    with self.assertRaises(FileNotFoundError):
      run_plugin("not_exist_plugin.py", self.data)

  def test_run_plugin_no_process(self):
    """
    process 함수가 없는 플러그인 실행 시 RuntimeError 발생 테스트
    """
    plugin_code = """
def dummy():
  pass
"""
    plugin_path = "temp_plugin2.py"
    with open(plugin_path, "w", encoding="utf-8") as f:
      f.write(plugin_code)
    try:
      with self.assertRaises(RuntimeError):
        run_plugin(plugin_path, self.data)
    finally:
      os.remove(plugin_path)

if __name__ == "__main__":
  unittest.main() 