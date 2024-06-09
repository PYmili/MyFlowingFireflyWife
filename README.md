# MyFlowingFireflyWife

![icon](data\assets\images\firefly\default\bg.png)

## 项目简介

MyFlowingFireflyWife 是一个使用 Python 开发的桌面宠物应用，灵感来源于星穹铁道中的角色“流萤”。该应用旨在为用户提供一个可爱的虚拟角色，增添桌面的趣味性和活力。

### 注意事项

1. **使用魔撘的Liuying-GPT-Sovits项目**

   使用[Liuying-GPT-Sovits](https://modelscope.cn/studios/LHXCxyw/Liuying-GPT-Sovits/summary)项目的tts功能，将生成流萤语音。

2. **阿里云 API 申请**（非必须）

   为了使用 MyFlowingFireflyWife 应用的全部功能，您需要前往阿里云申请相应的 API。您可以点击[此链接](https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-qianwen-7b-14b-72b-quick-start)获取详细的申请步骤和文档。填写配置文件**src/firefly/configuration.json**。
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

### 使用说明

- 下载并安装 MyFlowingFireflyWife 应用。
- 按照文档申请所需的 API。
- 在应用中设置好 API 相关信息。
- 启动应用并享受与 MyFlowingFireflyWife 的互动。

### 结语

MyFlowingFireflyWife 是一个可爱而有趣的桌面宠物应用，为您的电脑桌面增添了一份活力和乐趣。感谢您选择并使用 MyFlowingFireflyWife，如果您有任何问题或建议，请随时与我们联系。
