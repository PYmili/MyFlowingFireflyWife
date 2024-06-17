import wave
import pyaudio
from loguru import logger
from PySide6.QtCore import QThread, Signal


class AudioPlayer:
    def __init__(self, audioFilePath: str) -> None:
        self.audioFilePath = audioFilePath
        self.audio = None  # 初始化为None

    def load_audio(self) -> None:
        """加载WAV文件并存储wave对象"""
        try:
            self.audio = wave.open(self.audioFilePath, 'rb')
        except Exception as e:
            logger.error(f"Error loading audio file: {e}")

    def play(self) -> None:
        """播放音频"""
        if self.audio is None:
            self.load_audio()  # 确保音频文件已加载

        # 初始化pyaudio
        p = pyaudio.PyAudio()

        # 打开流
        stream = p.open(format=p.get_format_from_width(self.audio.getsampwidth()),
                        channels=self.audio.getnchannels(),
                        rate=self.audio.getframerate(),
                        output=True)

        try:
            # 读取数据并播放
            while True:
                data = self.audio.readframes(1024)  # 每次读取一定数量的帧
                if not data:
                    break
                stream.write(data)
        finally:
            # 清理资源
            stream.stop_stream()
            stream.close()
            self.audio.close()  # 关闭wave文件
            p.terminate()


class AudioPlayerQThread(QThread):
    # 定义一个信号，用于通知播放完成
    playbackFinished = Signal()

    def __init__(self, audioFilePath: str):
        super().__init__(parent=None)
        self.audioFilePath = audioFilePath
        self.player = AudioPlayer(self.audioFilePath)

    def run(self):
        """重写 QThread 的 run 方法来播放音频"""
        try:
            while self.player.play(): pass
        except Exception as e:
            logger.error(e)
        finally:
            # 播放完成后发出信号
            self.playbackFinished.emit()
