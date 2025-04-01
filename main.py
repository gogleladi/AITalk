import io
import os
import sys
import json
import requests
from vosk import Model, KaldiRecognizer
import pygame
import pyttsx3

pygame.mixer.init()
# 初始化Vosk语音识别模型
vosk_model_path = "./vosk-model-small-cn-0.22"  # 替换为你的Vosk模型路径
if not os.path.exists(vosk_model_path):
    print(f"请下载并解压Vosk中文模型到: {vosk_model_path}")
    sys.exit(1)

vosk_model = Model(vosk_model_path)
recognizer = KaldiRecognizer(vosk_model, 16000)

# 初始化语音合成器
engine = pyttsx3.init()
engine.setProperty('rate', 200)  # 设置语速
engine.setProperty('volume', 1.0)  # 设置音量

# DeepSeek API 配置
DEEPSEEK_API_URL = ""  # 替换为实际的API端点
DEEPSEEK_API_KEY = ""  # 替换为你的API密钥

def listen_to_microphone():
    """通过麦克风采集语音并转换为文本"""
    import pyaudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    print("请说话...")
    while True:
        data = stream.read(4096)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            print(f"你说: {text}")
            return text
        else:
            continue

def generate_response(input_text):
    """调用DeepSeek API生成对话回复"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",  # 替换为实际的模型名称
        "messages": [
            {"role": "system", "content": '你的身份是我的女朋友：小玉，你性格时而热情，时而高冷，现在请跟我聊天吧'},
            {"role": "user", "content": input_text}
        ],
        "max_tokens": 50  # 控制回复长度
    }
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        print(f"API调用失败: {response.status_code}, {response.text}")
        return "抱歉，我暂时无法回答这个问题。"

def speak(text):
    """通过音响播放语音"""
    print(f"AI回复: {text}")
    response = requests.get("")
    # print(response.content)
    # 从二进制数据创建音频段
    # audio = AudioSegment.from_file(io.BytesIO(response.content), format='mp3')
    # # 播放音频
    # play(audio)
    audio_obj = pygame.mixer.Sound(io.BytesIO(response.content))
    audio_obj.play()
    # engine.say(response.content)
    # engine.runAndWait()

def main():
    print("AI语音对话系统已启动！")
    while True:
        # 采集语音并转换为文本
        user_input = listen_to_microphone()
        if user_input:
            # 生成AI回复
            response = generate_response(user_input)
            # 播放AI回复
            speak(response)

if __name__ == "__main__":
    main()