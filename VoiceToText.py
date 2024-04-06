import os
import json
import wave
import base64
from typing import *

import pyaudio
import requests
from funasr import AutoModel
from loguru import logger

BAIDUYUN_API = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id="



class BaiduYun_STT:
    def __init__(self) -> None:
        """
        生成向百度云发送请求链接
        写入 APIKey SecretKey 两个参数值
        可更改当前目录下config.json文件中的值
        :return: str or False
        """
        stt_config = "assets\\data\\stt_config.json"
        if os.path.isfile(stt_config):
            with open(stt_config, "r") as rfp:
                __JSON = json.loads(rfp.read())
            self.BaseUrl = BAIDUYUN_API + f"{__JSON['APIKey']}&client_secret={__JSON['SecretKey']}"
        else:
            with open(stt_config, "w+") as wfp:
                wfp.write(json.dumps({
                    "APIKey": "",
                    "SecretKey": ""
                }, indent=4))
            self.BaseUrl = None

    def getToken(self) -> str:
        """
        获取百度云API的Token值
        :param host: str
        :return: str or False
        """
        if self.BaseUrl is None:
            logger.error("未生成 BaseUrl")
            return None
        
        with requests.post(self.BaseUrl) as post:
            try:
                __access_token = post.json()['access_token']
                post.close()
                return __access_token
            except KeyError:
                logger.error("未识别到配置数据")
                # TTS("未识别到配置数据，请选择配置。否则无法正常使用哦!")
                pass

        return False

    def SpeechToText(
            self,
            _SpeechData: bytes,
            _dev_pid: int = 1537,
            _format: str = 'wav',
            _rate: str = '16000',
            _channel: int = 1,
            _cuid: str = '*******'
    ) -> Union[str, None]:
        """
        将音频数据传输到百度云API接口，再获取到API识别到的文本信息。
        :param _SpeechData: bytes
        :param _dev_pid: int = 1537
        :param _format: str = 'wav'
        :param _rate: str = '16000'
        :param _channel: int = 1
        :param _cuid: str = '*******'
        :return: str
        """
        __data = {
            'format': _format,
            'rate': _rate,
            'channel': _channel,
            'cuid': _cuid,
            'len': len(_SpeechData),
            'speech': base64.b64encode(
                _SpeechData
            ).decode('utf-8'),
            'token': self.getToken(),
            'dev_pid': _dev_pid
        }
        with requests.post(
            'http://vop.baidu.com/server_api',
            json=__data,
            headers={'Content-Type': 'application/json'}
        ) as post:
            if 'result' in post.json():
                post.close()
                return post.json()['result'][0]
            else:
                post.close()
                return None
            

class Funasr_STT:
    def __init__(self) -> None:
        try:
            self.model = AutoModel(
                model="paraformer-zh", model_revision="v2.0.4",
                vad_model="fsmn-vad", vad_model_revision="v2.0.4",
                punc_model="ct-punc-c", punc_model_revision="v2.0.4",
                # spk_model="cam++", spk_model_revision="v2.0.2",
            )
        except Exception as e:
            logger.error(f"Funasr TTS 初始化失败！：{e}")
            raise Exception("Funasr TTS 初始化失败！")
        
    def SpeechToText(self, _SpeechData: bytes) -> Union[str, None]:
        """
        TTS
        :return Union[str, None]
        """
        if not self.model:
            return None
        
        funasr_cache_file = os.path.join(os.getcwd(), "funasr_cache.wav")
        with open(funasr_cache_file, "wb") as wfp:
            wfp.write(_SpeechData)
        
        result = self.model.generate(
            input=funasr_cache_file, 
            batch_size_s=300, 
            hotword='魔搭'
        )
        if not result:
            return None
        return result[0].get("text")


def SoundRecording(
        _format: object = pyaudio.paInt16,
        _WaveOutPath: str = "assets\\audio\\tape.wav",
        _time: int = 3,
        _rate: int = 16000,
        _channels: int = 1,
        _chunk: int = 1024
) -> bytes:
    """
    使用pyaudio模块调用系统麦克风进行录音操作
    :param _format: pyaudio.paInt16
    :param _WaveOutPath: str
    :param _time: int = 3
    :param _rate: inr = 16000
    :param _channels: int = 1
    :param _chunk: int = 1024
    :return: bytes
    """
    logger.info("开始录音")
    __audioP = pyaudio.PyAudio()
    __stream = __audioP.open(
        format=_format,
        channels=_channels,
        rate=_rate,
        input=True,
        frames_per_buffer=_chunk
        )

    with wave.open(_WaveOutPath, 'wb') as wa_wfp:
        wa_wfp.setnchannels(_channels)
        wa_wfp.setsampwidth(__audioP.get_sample_size(_format))
        wa_wfp.setframerate(_rate)
        RangeEnd: int = int(_rate / _chunk * _time)
        for _ in range(RangeEnd):
            wa_wfp.writeframes(__stream.read(_chunk))

    __stream.stop_stream()
    __stream.close()
    __audioP.terminate()

    with open(_WaveOutPath, "rb") as rfp:
        __AudioData = rfp.read()
    logger.info("录音结束")
    return __AudioData
