import tkinter as tk
from tkinter import messagebox
import random
import time
import pygame
import subprocess
import os

test_setup = {
    "types": ["Baseline", "Speech", "Audio"],
    "repeats": 3,
    "directions": ["Forward", "Backward", "Left", "Right", "Stop"]
}

# Translation dictionary
translations = {
    "Response Time Test": "反应时间测试",
    "Click 'Start Test' to begin": "点击'开始测试'按钮开始",
    "Start Test": "开始测试",
    "Prepare for": "准备",
    "Press arrow key when you hear the sound": "听到声音后按相应方向键",
    "Press arrow key when you hear the direction": "听到方向后按相应方向键",
    "Incorrect! Expected": "错误！应为",
    "Response time": "反应时间",
    "seconds": "秒",
    "Test Results": "测试结果",
    "Test Complete": "测试完成",
    "Average": "平均",
    "Forward": "前进",
    "Backward": "后退",
    "Left": "左转",
    "Right": "右转",
    "Stop": "停止",
    "Baseline": "基准测试",
    "Speech": "语音",
    "Audio": "音频"
}

def translate(text):
    return translations.get(text, text)

class ResponseTimeTest:
    def __init__(self, master):
        self.master = master
        self.master.title(translate("Response Time Test"))
        self.master.geometry("400x300")

        pygame.init()

        self.test_types = test_setup["types"]
        self.directions = test_setup["directions"]
        self.repeats = int(test_setup["repeats"])
        self.current_test = None
        self.current_direction = None
        self.start_time = None
        self.test_count = 0

        self.label = tk.Label(master, text=translate("Click 'Start Test' to begin"), font=("SimHei", 14))
        self.label.pack(pady=20)

        self.start_button = tk.Button(master, text=translate("Start Test"), command=self.start_test)
        self.start_button.pack(pady=10)

        self.symbol_label = tk.Label(master, text="", font=("SimHei", 48))
        self.symbol_label.pack(pady=20)

        self.results = []

        # Bind arrow keys and space
        self.master.bind("<Up>", lambda event: self.key_response("Forward"))
        self.master.bind("<Down>", lambda event: self.key_response("Backward"))
        self.master.bind("<Left>", lambda event: self.key_response("Left"))
        self.master.bind("<Right>", lambda event: self.key_response("Right"))
        self.master.bind("<space>", lambda event: self.key_response("Stop"))

    def start_test(self):
        if self.test_count >= len(self.test_types) * self.repeats:
            self.show_results()
            return

        self.current_test = self.test_types[self.test_count // self.repeats]
        self.current_direction = random.choice(self.directions)
        self.label.config(text=f"{translate('Prepare for')} {translate(self.current_test)}")
        self.start_button.config(state=tk.DISABLED)
        self.symbol_label.config(text="")
        self.master.after(2000, self.present_stimulus)

    def present_stimulus(self):
        self.start_time = time.time()

        if self.current_test == "Baseline":
            self.show_direction_symbol()
        elif self.current_test == "Audio":
            self.label.config(text=translate("Press arrow key when you hear the sound"))
            pygame.mixer.Sound(f"./audio/{self.current_direction.lower()}.wav").play()
        elif self.current_test == "Speech":
            self.label.config(text=translate("Press arrow key when you hear the direction"))
            subprocess.Popen(["say", "-v", "Tingting", translate(self.current_direction)])

    def show_direction_symbol(self):
        symbols = {
            "Forward": "↑",
            "Backward": "↓",
            "Left": "←",
            "Right": "→",
            "Stop": "■"
        }
        self.symbol_label.config(text=symbols[self.current_direction])

    def key_response(self, key):
        if self.start_time:
            response_time = time.time() - self.start_time
            if key != self.current_direction:
                self.label.config(text=f"{translate('Incorrect! Expected')} {translate(self.current_direction)}")
                self.master.after(1000, self.start_test)
            else:
                self.results.append((self.current_test, self.current_direction, response_time))
                self.label.config(text=f"{translate('Response time')}: {response_time:.3f} {translate('seconds')}")
                self.symbol_label.config(text="")
                self.test_count += 1
                self.master.after(1000, self.start_test)

            self.start_time = None

    def show_results(self):
        result_string = f"{translate('Test Results')}:\n"
        for test_type in self.test_types:
            type_results = [time for t, d, time in self.results if t == test_type]
            avg_time = sum(type_results) / len(type_results) if type_results else 0
            result_string += f"{translate(test_type)}: {translate('Average')} {avg_time:.3f} {translate('seconds')}\n"
        messagebox.showinfo(translate("Test Complete"), result_string)

        self.master.quit()

root = tk.Tk()
app = ResponseTimeTest(root)
root.mainloop()
