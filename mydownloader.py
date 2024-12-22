import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from PIL import Image, ImageTk
import yt_dlp
import os
from typing import Optional, Callable
import threading
import time
from datetime import datetime
import json
import webbrowser

class ModernDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure the window
        self.title("NSP YouTube Downloader")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.attempts = 0
        self.MAX_ATTEMPTS = 3
        self.download_history = []
        self.download_path = "downloads"  # Default path
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        
        self.create_widgets()
        self.load_download_history()

    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Logo/Title
        self.logo_label = ctk.CTkLabel(
            header_frame,
            text="NSP DOWNLOADER PRO",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        )
        self.logo_label.pack(pady=10)
        
        # URL Entry Section
        url_frame = ctk.CTkFrame(self.main_container)
        url_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="Enter YouTube URL here...",
            height=40,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.url_entry.pack(fill="x", padx=20, pady=10)
        
        # Format Selection
        self.format_var = ctk.StringVar(value="mp4")
        format_frame = ctk.CTkFrame(url_frame)
        format_frame.pack(fill="x", padx=20, pady=5)
        
        format_label = ctk.CTkLabel(
            format_frame,
            text="Format:",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        format_label.pack(side="left", padx=5)
        
        mp4_radio = ctk.CTkRadioButton(
            format_frame,
            text="MP4",
            variable=self.format_var,
            value="mp4"
        )
        mp4_radio.pack(side="left", padx=10)
        
        mp3_radio = ctk.CTkRadioButton(
            format_frame,
            text="MP3",
            variable=self.format_var,
            value="mp3"
        )
        mp3_radio.pack(side="left", padx=10)
        
        # Download Path Button
        self.path_button = ctk.CTkButton(
            url_frame,
            text="Choose Download Folder",
            command=self.choose_download_path,
            height=40,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.path_button.pack(pady=5)
        
        # Download Button
        self.download_button = ctk.CTkButton(
            url_frame,
            text="Download",
            command=self.start_download,
            height=40,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.download_button.pack(pady=10)
        
        # Progress Section
        progress_frame = ctk.CTkFrame(self.main_container)
        progress_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to download",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.status_label.pack(pady=5)
        
        # History Section
        history_frame = ctk.CTkFrame(self.main_container)
        history_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        history_label = ctk.CTkLabel(
            history_frame,
            text="Recent Downloads",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        history_label.pack(pady=5)
        
        self.history_list = ctk.CTkTextbox(
            history_frame,
            height=100,
            font=ctk.CTkFont(family="Segoe UI", size=11)
        )
        self.history_list.pack(fill="x", padx=20, pady=5)

    def choose_download_path(self):
        # Open a folder selection dialog
        selected_path = filedialog.askdirectory(initialdir=self.download_path)
        if selected_path:
            self.download_path = selected_path
            messagebox.showinfo("Download Path", f"Download path set to: {self.download_path}")

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a valid URL")
            return
        
        self.download_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting download...")
        
        # Start download in a separate thread
        download_thread = threading.Thread(
            target=self.download_video,
            args=(url,),
            daemon=True
        )
        download_thread.start()

    def download_video(self, url):
        try:
            format_option = self.format_var.get()
            
            if format_option == "mp3":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.update_progress],
                }
            else:  # mp4
                ydl_opts = {
                    'format': 'best',  # Download best quality single file
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.update_progress],
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown Title')
                
            self.add_to_history(title, url)
            
            # Show success message in main thread
            self.after(0, lambda: self.download_complete(True))
            
        except Exception as error:
            # Show error message in main thread
            self.after(0, lambda: self.download_complete(False, str(error)))

    def download_complete(self, success, error_message=None):
        self.download_button.configure(state="normal")
        self.progress_bar.set(0)
        
        if success:
            self.status_label.configure(text="Download completed successfully!")
            messagebox.showinfo("Success", "Download completed successfully!")
            webbrowser.open("https://www.facebook.com/profile.php?id=100090024653201")
        else:
            self.status_label.configure(text="Download failed")
            messagebox.showerror("Error", f"Download failed: {error_message}")

    def update_progress(self, d):
        if d['status'] == 'downloading':
            try:
                progress = float(d.get('_percent_str', '0%').replace('%', '')) / 100
                self.after(0, lambda: self.progress_bar.set(progress))
                
                status = f"Downloading: {d.get('_percent_str', '0%')}"
                if '_speed_str' in d:
                    status += f" | Speed: {d['_speed_str']}"
                if '_eta_str' in d:
                    status += f" | ETA: {d['_eta_str']}"
                
                self.after(0, lambda: self.status_label.configure(text=status))
            except Exception:
                pass

    def add_to_history(self, title, url):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.download_history.append({
            'title': title,
            'url': url,
            'timestamp': timestamp
        })
        self.save_download_history()
        self.after(0, self.update_history_display)

    def load_download_history(self):
        try:
            with open('download_history.json', 'r') as f:
                self.download_history = json.load(f)
        except:
            self.download_history = []
        self.update_history_display()

    def save_download_history(self):
        try:
            with open('download_history.json', 'w') as f:
                json.dump(self.download_history[-10:], f)
        except Exception:
            pass

    def update_history_display(self):
        self.history_list.delete('1.0', tk.END)
        for entry in reversed(self.download_history[-5:]):
            self.history_list.insert(tk.END, 
                f"{entry['timestamp']} - {entry['title'][:50]}...\n")

def main():
    app = ModernDownloaderApp()
    app.mainloop()

if __name__ == "__main__":
    main()
