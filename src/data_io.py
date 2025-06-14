import numpy as np
import h5py
import os

# CSV 파일로 데이터 저장
def save_csv(file_path, data: np.ndarray):
  """
  numpy 배열 데이터를 CSV 파일로 저장
  """
  try:
    np.savetxt(file_path, data, delimiter=",", fmt="%.8f")
  except Exception as e:
    raise IOError(f"CSV 저장 오류: {e}")

# CSV 파일에서 데이터 불러오기
def load_csv(file_path) -> np.ndarray:
  """
  CSV 파일에서 numpy 배열 데이터 불러오기
  """
  try:
    return np.loadtxt(file_path, delimiter=",")
  except Exception as e:
    raise IOError(f"CSV 불러오기 오류: {e}")

# HDF5 파일로 데이터 저장
def save_hdf5(file_path, data: np.ndarray):
  """
  numpy 배열 데이터를 HDF5 파일로 저장
  """
  try:
    with h5py.File(file_path, "w") as f:
      f.create_dataset("data", data=data)
  except Exception as e:
    raise IOError(f"HDF5 저장 오류: {e}")

# HDF5 파일에서 데이터 불러오기
def load_hdf5(file_path) -> np.ndarray:
  """
  HDF5 파일에서 numpy 배열 데이터 불러오기
  """
  try:
    with h5py.File(file_path, "r") as f:
      return f["data"][:]
  except Exception as e:
    raise IOError(f"HDF5 불러오기 오류: {e}")

# 파일 확장자 기반 포맷 자동 감지 및 저장
def save_data(file_path, data: np.ndarray):
  """
  파일 확장자에 따라 데이터 저장 (csv/h5)
  """
  ext = os.path.splitext(file_path)[1].lower()
  if ext == ".csv":
    save_csv(file_path, data)
  elif ext in [".h5", ".hdf5"]:
    save_hdf5(file_path, data)
  else:
    raise ValueError("지원하지 않는 파일 포맷입니다. (csv, h5/hdf5)")

# 파일 확장자 기반 포맷 자동 감지 및 불러오기
def load_data(file_path) -> np.ndarray:
  """
  파일 확장자에 따라 데이터 불러오기 (csv/h5)
  """
  ext = os.path.splitext(file_path)[1].lower()
  if ext == ".csv":
    return load_csv(file_path)
  elif ext in [".h5", ".hdf5"]:
    return load_hdf5(file_path)
  else:
    raise ValueError("지원하지 않는 파일 포맷입니다. (csv, h5/hdf5)") 