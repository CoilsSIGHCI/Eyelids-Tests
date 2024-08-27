import tkinter as tk
from tkinter import messagebox
import random
import time
import pygame
import subprocess
import os

class ResponseTimeTest:
    def __init__(self, master):
        self.master = master
        self.master.title("Response Time Test")
        self.master.geometry("400x300")

        pygame.init()

        self.test_types = ["Directional", "Audio", "Speech", "Custom"]
        self.current_test = None
        self.start_time = None

        self.label = tk.Label(master, text="Click 'Start Test' to begin", font=("Arial", 14))
        self.label.pack(pady=20)

        self.start_button = tk.Button(master, text="Start Test", command=self.start_test)
        self.start_button.pack(pady=10)

        self.response_button = tk.Button(master, text="Respond", command=self.record_response, state=tk.DISABLED)
        self.response_button.pack(pady=10)

        self.results = []

    def start_test(self):
        self.current_test = random.choice(self.test_types)
        self.label.config(text=f"Prepare for {self.current_test} test")
        self.start_button.config(state=tk.DISABLED)
        self.master.after(2000, self.present_stimulus)

    def present_stimulus(self):
        self.start_time = time.time()

        if self.current_test == "Directional":
            directions = ["Up", "Down", "Left", "Right"]
            direction = random.choice(directions)
            self.label.config(text=f"Press 'Respond' when you see: {direction}")
        elif self.current_test == "Audio":
            self.label.config(text="Press 'Respond' when you hear the beep")
            pygame.mixer.Sound("beep.wav").play()
        elif self.current_test == "Speech":
            self.label.config(text="Press 'Respond' when you hear the word")
            text = random.choice(["Apple", "Banana", "Orange", "Grape"])
            subprocess.Popen(["say", text])
        elif self.current_test == "Custom":
            self.label.config(text="Press 'Respond' when the background changes color")
            self.master.configure(bg="yellow")

        self.response_button.config(state=tk.NORMAL)

    def record_response(self):
        if self.start_time:
            response_time = time.time() - self.start_time
            self.results.append((self.current_test, response_time))
            self.label.config(text=f"Response time: {response_time:.3f} seconds")
            self.response_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.NORMAL)
            self.master.configure(bg="white")  # Reset background color

            if len(self.results) == len(self.test_types):
                self.show_results()

    def show_results(self):
        result_string = "Test Results:\n"
        for test_type, time in self.results:
            result_string += f"{test_type}: {time:.3f} seconds\n"
        messagebox.showinfo("Test Complete", result_string)
        self.master.quit()

root = tk.Tk()
app = ResponseTimeTest(root)
root.mainloop()
