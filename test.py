import tkinter as tk
from tkinter import messagebox
import random
import time
import pygame
import asyncio
import subprocess
import csv
from connector import BluetoothConnector, BluetoothGUI

test_setup = {
    "types": ["Baseline", "Speech", "Audio", "Eyelids"],
    "repeats": 10,
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
    def __init__(self, master, loop: asyncio.AbstractEventLoop):
        self.master = master
        self.loop = loop
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

        self.label = tk.Label(master, text=translate("Click 'Connect' to begin"), font=("SimHei", 14))
        self.label.pack(pady=20)

        self.connect_button = tk.Button(master, text=translate("Connect"), command=self.open_bluetooth_gui)
        self.connect_button.pack(pady=10)

        self.start_button = tk.Button(master, text=translate("Start Test"), command=self.start_test, state=tk.DISABLED)
        self.start_button.pack(pady=10)

        self.symbol_label = tk.Label(master, text="", font=("SimHei", 48))
        self.symbol_label.pack(pady=20)

        self.results = []
        self.csv_filename = "test_result.csv"

        # Bind arrow keys and space
        self.master.bind("<Up>", lambda event: self.key_response("Forward"))
        self.master.bind("<Down>", lambda event: self.key_response("Backward"))
        self.master.bind("<Left>", lambda event: self.key_response("Left"))
        self.master.bind("<Right>", lambda event: self.key_response("Right"))
        self.master.bind("<space>", lambda event: self.key_response("Stop"))

        self.bluetooth_connector = BluetoothConnector()

    def open_bluetooth_gui(self):
        bluetooth_window = tk.Toplevel(self.master)
        bluetooth_gui = BluetoothGUI(bluetooth_window, self.loop)
        bluetooth_window.protocol("WM_DELETE_WINDOW", lambda: self.on_bluetooth_gui_close(bluetooth_window, bluetooth_gui))

    def on_bluetooth_gui_close(self, window, gui):
        if gui.connector.connected_device:
            self.bluetooth_connector = gui.connector
            self.start_button.config(state=tk.NORMAL)
            self.label.config(text="Connected to Eyelids. Click 'Start Test' to begin.")
        window.destroy()

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
        elif self.current_test == "Eyelids":
            self.label.config(text=translate("Press arrow key when you see the Eyelids signal"))
            task = self.loop.create_task(self.bluetooth_connector.eyelids_direction(self.current_direction))

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

        self.save_results_to_csv()

        self.loop.create_task(self.bluetooth_connector.disconnect())
        self.master.after(100, self.master.quit)

    def save_results_to_csv(self):
        with open(self.csv_filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Test Type', 'Direction', 'Response Time (seconds)'])
            for result in self.results:
                csv_writer.writerow(result)
        print(f"Results saved to {self.csv_filename}")

def run_test(loop):
    root = tk.Tk()
    app = ResponseTimeTest(root, loop)

    def update_gui():
        root.update()
        loop.call_later(0.05, update_gui)

    loop.call_soon(update_gui)
    loop.run_forever()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    run_test(loop)
