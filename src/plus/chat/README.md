# chat

一个可以通过API生成流萤语音实现stt/tts，与用户进行交流的plus。

---

## 注意事项

1. **使用魔撘的Liuying-GPT-Sovits项目**

   使用[Liuying-GPT-Sovits](https://modelscope.cn/studios/LHXCxyw/Liuying-GPT-Sovits/summary)项目的tts功能，将生成流萤语音。

2. **阿里云 API 申请**（非必须）

   为了使用 MyFlowingFireflyWife 应用的全部功能，您需要前往阿里云申请相应的 API。您可以点击[此链接](https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-qianwen-7b-14b-72b-quick-start)获取详细的申请步骤和文档。填写配置文件 **src/firefly/configuration.json**。

   ```json
   {
      "QWen_API_KEY": "阿里云api"
   }
   ```

3. **百度云短语音识别 API 申请 (非必要)**

   为了实现 MyFlowingFireflyWife 应用中的语音识别功能，您需要申请百度云的短语音识别 API。您可以点击[此链接](https://cloud.baidu.com/product/speech/realtime_asr)了解如何申请并获取更多信息。

4. **语音转文字功能**

   目前项目采用两种方案实现，一种为百度云API接口，第二方案使用[funasr](https://github.com/OpenRL-Lab/FunASR)，可通过更改stt_config.json文件中的**stt**进行设置。

   ```json
   {
      "stt": "funasr"
   }
   ```

   ```json
   {
      "stt": "BaiDuYun"
   }
   ```
