import tkinter as tk
from tkinter import filedialog, messagebox, font as tkfont, ttk
import threading

import numpy as np
import pygame
import time
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image, ImageDraw, ImageFont
import os


class LyricVideoCreator:
    def __init__(self):
        self.frame = None
        self.lyrics_button = None
        self.vocal_button = None
        self.instrumental_button = None

        self.current_label = None
        self.next_label = None

        self.start_button = None
        self.next_button = None
        self.export_button = None

        # Progress bar components
        self.progress_frame = None
        self.progress_bar = None
        self.progress_label = None

        self.root = root
        self.root.title("Lyric Syncer")

        self.lyrics = []
        self.timestamps = []
        self.current_index = 0
        self.start_time = None

        self.lyrics_file = None
        self.vocal_audio_file = None
        self.instrumental_audio_file = None

        self.default_font = tkfont.Font(family="Segoe UI", size=11)
        self.heading_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.root.option_add("*Font", self.default_font)

        self.colors = {
            "bg": "#2b2b2b",
            "frame_bg": "#2b2b2b",
            "button_bg": "#444444",
            "button_fg": "white",
            "label_bg": "#000000",
            "label_fg": "white",
            "heading_fg": "#dddddd",
            "controls_bg": "#2b2b2b"
        }

        self.setup_gui()

        pygame.init()
        pygame.mixer.init()

#region GUI

    def center_window(self, width, height):
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")

    def create_button(self, text, command):
        button = tk.Button(
            self.frame,
            text=text,
            command=command,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"]
        )
        button.pack(fill="x", pady=3)
        return button

    def create_heading_label(self, text, pack_kwargs=None):
        if pack_kwargs is None:
            pack_kwargs = {"anchor": "w", "pady": (10, 2)}

        label = tk.Label(
            self.frame,
            text=text,
            font=self.heading_font,
            bg=self.colors["frame_bg"],
            fg=self.colors["heading_fg"]
        )
        label.pack(**pack_kwargs)
        return label

    def create_content_label(self, pad_bottom):
        label = tk.Label(
            self.frame,
            text="",
            fg=self.colors["label_fg"],
            bg=self.colors["label_bg"],
            height=4,
            padx=10,
            pady=10,
            anchor="nw",
            justify="left"
        )
        label.pack(fill="both", pady=(0, pad_bottom), expand=True)
        return label

    def setup_gui(self):
        self.center_window(800, 650)  # Slightly taller to accommodate progress bar

        self.root.configure(bg=self.colors["bg"])

        self.frame = tk.Frame(self.root, bg=self.colors["frame_bg"])
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.lyrics_button = self.create_button("📄 Load Lyrics", self.load_lyrics)
        self.vocal_button = self.create_button("🎤 Load Vocal Audio", self.load_vocal_audio)
        self.instrumental_button = self.create_button("🎵 Load Instrumental Audio", self.load_instrumental_audio)

        self.create_heading_label("Current Lyric:")
        self.current_label = self.create_content_label(5)

        self.create_heading_label("Next Lyric:")
        self.next_label = self.create_content_label(10)

        self.start_button = self.create_button("Start Playback", self.start_playback)
        self.next_button = self.create_button("Mark Timestamp / Next", self.mark_timestamp)
        self.export_button = self.create_button("🎬 Export Video", self.export_video)

        # Progress bar section (initially hidden)
        self.setup_progress_bar()

        self.export_button.config(state="disabled")
        self.next_button.config(state="disabled")

    #region Progressbar

    def setup_progress_bar(self):
        """Setup the progress bar components"""
        self.progress_frame = tk.Frame(self.frame, bg=self.colors["frame_bg"])

        # Progress label
        self.progress_label = tk.Label(
            self.progress_frame,
            text="",
            bg=self.colors["frame_bg"],
            fg=self.colors["heading_fg"],
            font=self.heading_font
        )
        self.progress_label.pack(pady=(5, 5))

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(pady=(0, 10))

    def show_progress_bar(self):
        self.progress_frame.pack(fill="x", pady=(10, 0))

    def hide_progress_bar(self):
        self.progress_frame.pack_forget()

    def update_progress(self, current, total, status_text):
        if self.progress_bar and self.progress_label:
            progress_percentage = (current / total) * 100
            self.progress_bar['value'] = progress_percentage
            self.progress_label.config(text=f"{status_text} ({current}/{total}) - {progress_percentage:.1f}%")
            self.root.update_idletasks()

    #endregion

#endregion

    def load_lyrics(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not path: return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.lyrics = [p.strip() for p in f.read().split("\n\n") if p.strip()]

            self.lyrics_file = path
            filename = os.path.basename(path)
            self.lyrics_button.config(text=f"📄 Load Lyrics: {filename}")
            self.update_lyrics_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load lyrics file: {str(e)}")

    def load_vocal_audio(self):
        path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.flac")])
        if path:
            filename = os.path.basename(path)
            self.vocal_button.config(text=f"🎤 Load Vocal Audio: {filename}")
            self.vocal_audio_file = path

    def load_instrumental_audio(self):
        path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.flac")])
        if path:
            filename = os.path.basename(path)
            self.instrumental_button.config(text=f"🎵 Load Instrumental Audio: {filename}")
            self.instrumental_audio_file = path

    def start_playback(self):
        if not all([self.lyrics, self.vocal_audio_file, self.instrumental_audio_file]):
            messagebox.showerror("Missing Input", "Please load all required files.")
            return

        pygame.mixer.music.load(self.vocal_audio_file)
        pygame.mixer.music.play()
        self.start_time = time.time()
        self.timestamps = []
        self.current_index = 0
        self.update_lyrics_display()
        self.next_button.config(state="normal")

    def mark_timestamp(self):
        now = time.time() - self.start_time
        self.timestamps.append(now)
        self.current_index += 1
        self.update_lyrics_display()

        if self.current_index >= len(self.lyrics):
            pygame.mixer.music.stop()
            self.next_button.config(state="disabled")
            self.export_button.config(state="normal")
            messagebox.showinfo("Done", "Timestamps completed! You can now export the video.")

    def update_lyrics_display(self):
        current = self.lyrics[self.current_index] if self.current_index < len(self.lyrics) else ""
        next_lyric = self.lyrics[self.current_index + 1] if self.current_index + 1 < len(self.lyrics) else ""
        self.current_label.config(text=current)
        self.next_label.config(text=next_lyric)

    def export_video(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4")])
        if not output_path: return

        # Show progress bar and disable export button
        self.show_progress_bar()
        self.export_button.config(state="disabled")

        # Start export in separate thread
        export_thread = threading.Thread(target=self.export_video_thread, args=(output_path,))
        export_thread.daemon = True
        export_thread.start()

    def export_video_thread(self, output_path):
        try:
            width, height = 1920, 1080
            clips = []
            total_steps = len(self.timestamps) + 2  # +2 for concatenation and audio steps

            for i in range(len(self.timestamps)):
                start = self.timestamps[i]
                end = self.timestamps[i + 1] if i + 1 < len(self.timestamps) else None
                duration = (end - start) if end else 2

                current = self.lyrics[i]
                next_line = self.lyrics[i + 1] if i + 1 < len(self.lyrics) else ""

                # Update progress
                self.update_progress(i + 1, total_steps, f"Processing lyric: {current[:30]}...")

                # Create background image
                bg_img = Image.new('RGB', (width, height), (0, 0, 0))  # Black background

                # Create current text image
                current_img = self.create_text_image(
                    current, width, height, 72, (255, 255, 255, 255), is_current=True
                )

                # Composite current text onto background
                bg_img.paste(current_img, (0, 0), current_img)

                # Create next text image if there is one
                if next_line:
                    next_img = self.create_text_image(
                        next_line, width, height, 64, (128, 128, 128, 255), is_current=False
                    )
                    bg_img.paste(next_img, (0, 0), next_img)

                # Create video clip from image
                img_clip = ImageClip(np.array(bg_img)).set_duration(duration)
                clips.append(img_clip)

            # Concatenating video clips
            self.update_progress(len(self.timestamps) + 1, total_steps, "Concatenating video clips...")
            final_output = concatenate_videoclips(clips)

            # Adding audio
            self.update_progress(len(self.timestamps) + 2, total_steps, "Adding audio and writing video file...")
            final_output = final_output.set_audio(AudioFileClip(self.instrumental_audio_file))

            # Writing video file
            final_output.write_videofile(output_path, fps=24, verbose=False, logger=None)
            self.root.after(0, self.export_success)
        except Exception as e:
            # Error - schedule GUI update in main thread
            self.root.after(0, lambda: self.export_error(str(e)))

    def export_success(self):
        self.hide_progress_bar()
        self.export_button.config(state="normal")
        messagebox.showinfo("Success", "Video exported successfully!")

    def export_error(self, error_msg):
        self.hide_progress_bar()
        self.export_button.config(state="normal")
        messagebox.showerror("Export Error", f"Failed to export video: {error_msg}")

    def create_text_image(self, text, width, height, font_size, color, is_current=True):
        # Create a transparent image
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default(font_size)

        # Wrap text to fit width
        max_width = width - 100  # Leave some margin
        wrapped_text = self.wrap_text(text, font, max_width)

        # Calculate text dimensions
        lines = wrapped_text.split('\n')
        line_height = font_size + 10
        total_height = len(lines) * line_height

        # Calculate starting position based on whether it's current or next text
        if is_current:
            # Current text: position it in upper portion of screen
            start_y = (height // 2) - total_height - 50
        else:
            # Next text: position it in lower portion of screen
            start_y = (height // 2) + 50

        # Make sure text doesn't go off-screen
        if start_y < 0:
            start_y = 10
        elif start_y + total_height > height:
            start_y = height - total_height - 10

        # Draw each line
        for i, line in enumerate(lines):
            if line.strip():  # Only draw non-empty lines
                # Get text width for centering
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                y = start_y + i * line_height

                draw.text((x, y), line, font=font, fill=color)

        return img

    def wrap_text(self, text, font, max_width):
        original_lines = text.split('\n')
        final_lines = []

        for line in original_lines:
            if not line.strip():
                final_lines.append("")
                continue

            # Check if the line needs wrapping
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]

            if line_width <= max_width:
                # Line fits, keep as is
                final_lines.append(line)
            else:
                # Line is too long, wrap it
                words = line.split()
                current_line = ""

                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
                    text_width = bbox[2] - bbox[0]

                    if text_width <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            final_lines.append(current_line)
                        current_line = word

                if current_line:
                    final_lines.append(current_line)

        return '\n'.join(final_lines)


# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = LyricVideoCreator()
    root.mainloop()
