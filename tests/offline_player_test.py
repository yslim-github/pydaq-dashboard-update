import unittest
import numpy as np
from src.offline_player import OfflinePlayer
from PySide6.QtWidgets import QApplication
import sys

app = QApplication.instance() or QApplication(sys.argv)

class TestOfflinePlayer(unittest.TestCase):
  def setUp(self):
    self.player = OfflinePlayer()
    self.data = np.arange(20).reshape(2, 10)  # 2채널, 10프레임
    self.player.set_data(self.data)
    self.frame_emitted = False
    def on_frame(idx, frame):
      self.frame_emitted = True
      self.last_idx = idx
      self.last_frame = frame
    self.player.frame_changed.connect(on_frame)
    self.finished_emitted = False
    self.player.playback_finished.connect(lambda: setattr(self, 'finished_emitted', True))

  def test_seek_and_emit(self):
    """
    슬라이더로 프레임 이동 시 시그널 emit 및 데이터 일치 확인
    """
    self.player.seek(5)
    self.assertTrue(self.frame_emitted)
    self.assertEqual(self.last_idx, 5)
    self.assertTrue(np.allclose(self.last_frame, self.data[..., 5]))

  def test_play_and_pause(self):
    """
    play/pause 동작 (상태만 확인)
    """
    self.player.play()
    self.assertTrue(self.player.playing)
    self.player.pause()
    self.assertFalse(self.player.playing)

  def test_change_speed(self):
    """
    배속 변경 동작
    """
    self.player.speed_combo.setCurrentIndex(1)  # 2x
    self.player.change_speed()
    self.assertEqual(self.player.playback_speed, 2)
    self.player.speed_combo.setCurrentIndex(2)  # 4x
    self.player.change_speed()
    self.assertEqual(self.player.playback_speed, 4)

  def test_seek_out_of_range(self):
    """
    슬라이더 범위 초과 시 예외 없이 동작 (내부적으로 무시)
    """
    try:
      self.player.seek(100)  # 실제 프레임 수보다 큼
    except Exception as e:
      self.fail(f"슬라이더 범위 초과에서 예외 발생: {e}")

  def test_no_data_behavior(self):
    """
    데이터가 없는 상태에서 play/seek 등 호출 시 예외 없이 동작
    """
    player = OfflinePlayer()
    try:
      player.play()
      player.seek(0)
      player.change_speed()
    except Exception as e:
      self.fail(f"데이터 없음 상태에서 예외 발생: {e}")

  def test_playback_finished_signal(self):
    """
    마지막 프레임까지 재생 시 playback_finished 시그널 emit
    """
    self.player.current_frame = self.data.shape[-1] - 2
    self.player.play()
    # 타이머 tick 직접 호출 (실제 시간 대기 없이)
    self.player._on_timer_tick()
    self.player._on_timer_tick()
    self.assertTrue(self.finished_emitted)

if __name__ == "__main__":
  unittest.main() 