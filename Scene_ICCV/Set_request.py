"""
这部分模块的作用是接管提示内容设计


"""


import pygame

# 视觉接管提示内容
def Vision_request():
    print("Vision request")


# 听觉接管提示内容
def Video_requset():
    # 加载音频文件
    sound_file = 'asset/接管提示音.wav'  # 替换为你的WAV文件路径
    sound = pygame.mixer.Sound(sound_file)
    # 播放声音
    sound.play()