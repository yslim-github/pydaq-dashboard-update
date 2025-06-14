import numpy as np
from scipy import signal
import importlib.util
import os

# FFT 변환 함수
def apply_fft(data: np.ndarray) -> np.ndarray:
  """
  입력 데이터에 대해 FFT(고속 푸리에 변환) 수행
  """
  # 입력 타입 검사
  if not isinstance(data, np.ndarray):
    raise RuntimeError("입력 데이터는 numpy.ndarray여야 합니다.")
  try:
    return np.fft.fft(data, axis=-1)
  except Exception as e:
    raise RuntimeError(f"FFT 처리 오류: {e}")

# FIR 저역통과 필터 적용 함수
def apply_fir_lowpass(data: np.ndarray, cutoff_hz: float, fs: float, order=64) -> np.ndarray:
  """
  FIR 저역통과 필터 적용
  """
  try:
    taps = signal.firwin(order, cutoff_hz, fs=fs)
    return signal.lfilter(taps, 1.0, data, axis=-1)
  except Exception as e:
    raise RuntimeError(f"FIR 필터 처리 오류: {e}")

# IIR 저역통과 필터 적용 함수
def apply_iir_lowpass(data: np.ndarray, cutoff_hz: float, fs: float, order=4) -> np.ndarray:
  """
  IIR 저역통과 필터 적용
  """
  try:
    b, a = signal.butter(order, cutoff_hz, fs=fs, btype='low')
    return signal.lfilter(b, a, data, axis=-1)
  except Exception as e:
    raise RuntimeError(f"IIR 필터 처리 오류: {e}")

# 통계 분석 함수 (평균, 표준편차)
def calc_stats(data: np.ndarray) -> dict:
  """
  데이터의 평균, 표준편차 등 통계값 반환
  """
  try:
    return {
      'mean': np.mean(data, axis=-1),
      'std': np.std(data, axis=-1),
      'min': np.min(data, axis=-1),
      'max': np.max(data, axis=-1)
    }
  except Exception as e:
    raise RuntimeError(f"통계 분석 오류: {e}")

# 외부 파이썬 플러그인(스크립트) 로딩 및 실행 함수
def run_plugin(plugin_path: str, data: np.ndarray) -> np.ndarray:
  """
  플러그인 파이썬 파일에서 process(data) 함수를 실행
  """
  if not os.path.exists(plugin_path):
    raise FileNotFoundError(f"플러그인 파일이 존재하지 않습니다: {plugin_path}")
  try:
    spec = importlib.util.spec_from_file_location("plugin_module", plugin_path)
    plugin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plugin)
    if not hasattr(plugin, "process"):
      raise AttributeError("플러그인에 process(data) 함수가 없습니다.")
    return plugin.process(data)
  except Exception as e:
    raise RuntimeError(f"플러그인 실행 오류: {e}") 