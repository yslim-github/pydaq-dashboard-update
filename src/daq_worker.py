from PySide6.QtCore import QThread, Signal
import nidaqmx
import numpy as np
import time

class DaqDataCollector(QThread):
  # 데이터 수집 신호: (numpy 배열, 타임스탬프)
  data_collected = Signal(np.ndarray, float)
  # 에러 발생 신호: (에러 메시지)
  error_occurred = Signal(str)

  def __init__(self, device_name, channel, sample_rate=10000, samples_per_read=1000, parent=None):
    super().__init__(parent)
    self.device_name = device_name  # DAQ 디바이스 이름
    self.channel = channel          # 수집 채널명 (예: 'ai0')
    self.sample_rate = sample_rate  # 샘플링 속도(Hz)
    self.samples_per_read = samples_per_read  # 한 번에 읽을 샘플 개수
    self._running = False           # 스레드 실행 플래그

  def run(self):
    """
    QThread 실행 함수. DAQ 하드웨어에서 데이터를 실시간으로 수집.
    """
    self._running = True
    try:
      # DAQmx Task 생성
      with nidaqmx.Task() as task:
        # 아날로그 입력 채널 추가
        task.ai_channels.add_ai_voltage_chan(f"{self.device_name}/{self.channel}")
        # 샘플 클럭 설정
        task.timing.cfg_samp_clk_timing(self.sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        while self._running:
          try:
            # 데이터 읽기
            data = task.read(number_of_samples_per_channel=self.samples_per_read)
            np_data = np.array(data)
            timestamp = time.time()
            # 데이터 수집 신호 발생
            self.data_collected.emit(np_data, timestamp)
          except Exception as e:
            # 데이터 읽기 중 에러 발생 시 에러 신호 발생
            self.error_occurred.emit(f"데이터 수집 중 오류: {e}")
            break
    except Exception as e:
      # DAQ Task 생성/설정 중 에러 발생 시 에러 신호 발생
      self.error_occurred.emit(f"DAQ 초기화 오류: {e}")

  def stop(self):
    """
    스레드 종료 요청 함수
    """
    self._running = False 