import os
import subprocess
from typing import Union

from PyQt5.QtWidgets import QLabel
import requests
from loguru import logger

GENSHINVOICE_API = "https://bv2.firefly.matce.cn"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Cookie": "_gid=GA1.2.925120628.1711724248; Hm_lvt_d67baafd318097a18e70ee8d8d1de57a=1711724642,1711808299,1711818468; _gat_gtag_UA_156449732_1=1; Hm_lpvt_d67baafd318097a18e70ee8d8d1de57a=1711819807; _ga_R1FN4KJKJH=GS1.1.1711819775.4.1.1711819807.0.0.0; _ga=GA1.1.1713498848.1711724248",
    "Origin": GENSHINVOICE_API,
    "Referer": GENSHINVOICE_API + "/"
}


class FireFlyTTS:
    def __init__(self, content: str, text_prompt: str = "Happy") -> None:
        """
        通过 genshinvoice.top API 生成tts音频链接
        :param content: str 需要生成的文字
        :param text_prompt: str 文字提示 Test Prompt
        """
        logger.info(f"TTS -> {content}")
        self.post_data = {
            "data": [
                content,
                "流萤_ZH",
                0.5,
                0.6,
                0.9,
                1,
                "ZH",
                "True",
                1,
                0.2,
                None,
                text_prompt,
                "",
                0.7
            ],
            "event_data": None,
            "fn_index": 0,
            "session_hash": "20nl3dktjcb"
        }
        self.content = content

    def play(self, label: QLabel) -> Union[str, None]:
        """
        运行
        :return Union[str, None]
        """
        with requests.post(GENSHINVOICE_API + "/run/predict", headers=HEADERS, json=self.post_data) as response:
            if response.status_code == 200:
                if response.json()['data'][0] != 'Success':
                    return None
                tmp_wav = response.json()['data'][-1]['name']
            else:
                tmp_wav = None

        if not tmp_wav:
            logger.error("未获取到音频文件！")
            return None
        
        tts_wav = GENSHINVOICE_API + "/file=" + tmp_wav
        with requests.get(tts_wav, headers=HEADERS) as response:
            if response.status_code == 200:
                with open("result_audio.wav", "wb+") as wfp:
                    wfp.write(response.content)
            else:
                return None
        
        # 为了同步消息与播放音频，将在此设置QLabel文本
        label.setWordWrap(True)
        label.setText(self.content)
        label.adjustSize()
        label.show()
        FFplayPlay(os.path.join(os.getcwd(), "result_audio.wav")).play()

        return tts_wav


class FFplayPlay:
    def __init__(self, audio_path: str) -> None:
        """
        使用FFplay播放网络音频
        :param audio_url: str 需要播放的音频URL
        """
        self.audio_path = audio_path

    def play(self) -> None:
        """
        播放音频
        """
        if os.name == 'nt':  # Windows platform
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # 隐藏控制台窗口
            process = subprocess.Popen(
                ['ffplay', '-nodisp', '-autoexit', self.audio_path],
                startupinfo=startupinfo
            )
        else:  # Unix-like platforms (Linux, macOS)
            with open(os.devnull, 'w') as devnull:
                process = subprocess.Popen(
                    ['ffplay', '-nodisp', '-autoexit', self.audio_path],
                    stdout=devnull, stderr=devnull
                )

        # 等待ffplay进程结束（由于指定了-autoexit，它会在播放完毕后自动退出）
        process.wait()
