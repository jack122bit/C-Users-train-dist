import os
import tkinter as tk
from tkinter import filedialog, messagebox
import vlc
import time
import threading  # For background task of calculating duration


class RadioStationGUI:
    def __init__(self, master):
        self.master = master
        master.title("Quit Crying Stones Radio")

        self.downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        self.playlist = []  # List to store file paths
        self.current_index = 0 # to keep track of the track
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.is_playing = False

        # GUI Elements
        self.playlist_label = tk.Label(master, text="Playlist:")
        self.playlist_label.pack()

        self.playlist_box = tk.Listbox(master, width=60, height=10)
        self.playlist_box.pack()

        self.add_button = tk.Button(master, text="Add Song", command=self.add_song)
        self.add_button.pack()

        self.play_button = tk.Button(master, text="Play", command=self.play)
        self.play_button.pack()

        self.pause_button = tk.Button(master, text="Pause", command=self.pause)
        self.pause_button.pack()

        self.next_button = tk.Button(master, text="Next", command=self.next_song)
        self.next_button.pack()

        self.previous_button = tk.Button(master, text="Previous", command=self.previous_song)
        self.previous_button.pack()

        self.duration_label = tk.Label(master, text="Total Duration: Calculating...")
        self.duration_label.pack()

        self.load_playlist()  # Load initial playlist from Downloads

        # Start calculating total duration in a background thread.  This prevents the GUI from freezing.
        threading.Thread(target=self.calculate_total_duration, daemon=True).start()


    def load_playlist(self):
        """Loads MP3 files from the Downloads folder into the playlist."""
        try:
            for filename in os.listdir(self.downloads_folder):
                if filename.endswith(".mp3"):
                    filepath = os.path.join(self.downloads_folder, filename)
                    self.playlist.append(filepath)
                    self.playlist_box.insert(tk.END, filename)  # Add to GUI listbox

        except FileNotFoundError:
            messagebox.showerror("Error", "Downloads folder not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading playlist: {e}")

    def add_song(self):
        """Opens a file dialog to allow the user to add MP3 files to the playlist."""
        filepaths = filedialog.askopenfilenames(filetypes=[("MP3 Files", "*.mp3")])  # Allow multiple selections

        if filepaths:  # Check if the user selected any files
            for filepath in filepaths:
                filename = os.path.basename(filepath)  # Extract filename from path
                self.playlist.append(filepath)
                self.playlist_box.insert(tk.END, filename)
            threading.Thread(target=self.calculate_total_duration, daemon=True).start()  # Recalculate duration

    def play(self):
        """Plays the currently selected song."""
        if not self.playlist:
            messagebox.showinfo("Info", "Playlist is empty.")
            return

        if not self.is_playing: # if the program is paused
            media = self.instance.media_new(self.playlist[self.current_index])
            self.player.set_media(media)
            self.player.play()
            self.is_playing = True


        # Optionally, you could start a thread here to monitor playback and automatically advance to the next song when one finishes.  I'll add that as an extension.

    def pause(self):
        """Pauses or resumes playback."""
        if self.is_playing and self.player.is_playing():
            self.player.pause()  # Toggle pause
        else:
            self.player.play() # resume play
        self.is_playing = not self.is_playing # switch the boolean
    def next_song(self):
        """Plays the next song in the playlist."""
        if not self.playlist:
            messagebox.showinfo("Info", "Playlist is empty.")
            return

        self.current_index = (self.current_index + 1) % len(self.playlist)  # Wrap around to start
        self.player.stop()
        media = self.instance.media_new(self.playlist[self.current_index])
        self.player.set_media(media)
        self.player.play()

    def previous_song(self):
        """Plays the previous song in the playlist."""
        if not self.playlist:
            messagebox.showinfo("Info", "Playlist is empty.")
            return

        self.current_index = (self.current_index - 1) % len(self.playlist)  # Wrap around to end
        self.player.stop()
        media = self.instance.media_new(self.playlist[self.current_index])
        self.player.set_media(media)
        self.player.play()

    def calculate_total_duration(self):
        """Calculates the total duration of all songs in the playlist and updates the label."""
        total_seconds = 0
        for filepath in self.playlist:
            try:
                media = self.instance.media_new(filepath)
                media.parse()  # Important to parse the media to get duration
                duration_ms = media.get_duration()  # Duration in milliseconds
                if duration_ms > 0:  # Check if duration is valid
                    total_seconds += duration_ms / 1000  # Convert to seconds
                else:
                    print(f"Warning: Could not get duration for {filepath}")  # Log a warning
            except Exception as e:
                print(f"Error getting duration for {filepath}: {e}")
        total_minutes = total_seconds / 60
        self.duration_label.config(text=f"Total Duration: {total_minutes:.2f} minutes")

root = tk.Tk()
gui = RadioStationGUI(root)
root.mainloop()