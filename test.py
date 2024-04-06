from funasr import AutoModel
# paraformer-zh is a multi-functional asr model
# use vad, punc, spk or not as you need
model = AutoModel(
    model="paraformer-zh", model_revision="v2.0.4",
    vad_model="fsmn-vad", vad_model_revision="v2.0.4",
    punc_model="ct-punc-c", punc_model_revision="v2.0.4",
    # spk_model="cam++", spk_model_revision="v2.0.2",
)
res = model.generate(
    input=f"result_audio.wav", 
    batch_size_s=300, 
    hotword='魔搭'
)
print(res)