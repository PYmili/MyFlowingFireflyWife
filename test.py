from firefly import gpt

gptChat = gpt.Chat(gpt.callbackDemo)
gptChat.addMessage("你是谁？")
gptChat.run()