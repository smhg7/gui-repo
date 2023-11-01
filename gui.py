import tkinter as tk
import cv2
import os
from pydub import AudioSegment
from pydub.playback import play

# Define a list of common bit rates
common_bitrates = ["500", "1000", "2000", "3000", "5000"]

class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Video Player")

        self.video_path = None
        self.playing = False
        self.cap = None
        self.selected_bitrate = tk.StringVar()
        self.selected_bitrate.set(common_bitrates[0])
        self.volume = tk.DoubleVar()
        self.volume.set(100)  # Default volume is 100%

        self.create_widgets()

    def create_widgets(self):
        # Video Frame
        self.video_frame = tk.Label(self.root)
        self.video_frame.pack()

        # Control Buttons
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack()

        self.play_button = tk.Button(self.control_frame, text="Play", command=self.toggle_play)
        self.pause_button = tk.Button(self.control_frame, text="Pause", command=self.toggle_play)
        self.stop_button = tk.Button(self.control_frame, text="Stop", command=self.stop)

        self.play_button.grid(row=0, column=0)
        self.pause_button.grid(row=0, column=1)
        self.stop_button.grid(row=0, column=2)

        self.pause_button["state"] = "disabled"

        # File Selection
        self.file_label = tk.Label(self.control_frame, text="Video File:")
        self.file_label.grid(row=1, column=0)

        self.file_entry = tk.Entry(self.control_frame)
        self.file_entry.grid(row=1, column=1)

        self.browse_button = tk.Button(self.control_frame, text="Browse", command=self.browse)
        self.browse_button.grid(row=1, column=2)

        # Bit Rate Control - Using a dropdown menu
        self.bitrate_label = tk.Label(self.control_frame, text="Bit Rate (kbps):")
        self.bitrate_label.grid(row=2, column=0)

        self.bitrate_dropdown = tk.OptionMenu(self.control_frame, self.selected_bitrate, *common_bitrates)
        self.bitrate_dropdown.grid(row=2, column=1)

        self.bitrate_button = tk.Button(self.control_frame, text="Apply Bit Rate", command=self.apply_bitrate)
        self.bitrate_button.grid(row=2, column=2)

        # Volume Control
        self.volume_label = tk.Label(self.control_frame, text="Volume:")
        self.volume_label.grid(row=3, column=0)

        self.volume_slider = tk.Scale(self.control_frame, from_=0, to=100, variable=self.volume, orient=tk.HORIZONTAL)
        self.volume_slider.grid(row=3, column=1)

    def toggle_play(self):
        if self.playing:
            self.pause_button["state"] = "disabled"
            self.play_button["state"] = "active"
            self.playing = False
        else:
            self.play_button["state"] = "disabled"
            self.pause_button["state"] = "active"
            self.playing = True
            if not self.cap:
                self.cap = cv2.VideoCapture(self.video_path)
                self.update_video()

    def stop(self):
        self.playing = False
        self.play_button["state"] = "active"
        self.pause_button["state"] = "disabled"
        if self.cap:
            self.cap.release()

    def update_video(self):
        if self.playing:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.video_frame.configure(image=photo)
                self.video_frame.image = photo

                # Adjust the audio volume
                selected_volume = self.volume.get() / 100.0
                audio = AudioSegment.from_file(self.video_path)
                adjusted_audio = audio - (selected_volume - 1.0) * 100
                play(adjusted_audio)

                self.root.after(10, self.update_video)
            else:
                self.stop()

    def browse(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.video_path = file_path
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, self.video_path)

    def apply_bitrate(self):
        if self.video_path:
            selected_bitrate = self.selected_bitrate.get()
            if selected_bitrate:
                new_bitrate = selected_bitrate
                output_file = "output.mp4"
                cmd = f'ffmpeg -i "{self.video_path}" -b:v {new_bitrate}k -c:v libx264 -c:a aac -strict experimental "{output_file}"'
                os.system(cmd)
                self.video_path = output_file
                self.file_entry.delete(0, tk.END)
                self.file_entry.insert(0, self.video_path)

if __name__ == "__main__":
    import os
    from tkinter import filedialog
    from PIL import Image, ImageTk

    root = tk.Tk()
    app = VideoPlayerApp(root)
    root.mainloop()
