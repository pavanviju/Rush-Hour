import tkinter as tk
from tkinter import messagebox
import random
import json
import os
from PIL import ImageTk, Image
import pygame  # Import pygame for audio handling

# Load the word list from the JSON file
with open("C:/Users/pavan/OneDrive/Documents/OS Game/words_dictionary.json", "r") as file:
    word_data = json.load(file)
    word_list = list(word_data.keys())  # Extract the words from the dictionary keys

# Initialize pygame mixer for background music
pygame.mixer.init()

# Function to load music files from the Music directory
def load_music_files(music_folder):
    music_files = []
    for file in os.listdir(music_folder):
        if file.endswith(".mp3"):
            music_files.append(os.path.join(music_folder, file))
    return music_files

# Function to play random music
def play_random_music(music_files):
    pygame.mixer.music.load(random.choice(music_files))
    pygame.mixer.music.play(-1)  # Loop indefinitely

class BombPartyGame:
    def __init__(self, root, player1_name, player2_name):
        self.root = root
        self.root.title("Rush Hour(Round Robin)")

        # Set the size of the window (increased size)
        self.window_width = 600
        self.window_height = 400
        
        # Center the window on the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (self.window_width // 2)
        y = (screen_height // 2) - (self.window_height // 2)
        
        # Configure window size and position
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        
        # Dark mode colors
        bg_color = "#2E2E2E"  # Dark background
        fg_color = "#FFFFFF"  # Light text
        btn_color = "#444444"  # Button background
        self.root.configure(bg=bg_color)  # Set window background color

        # Player-specific variables
        self.players = [
            {"name": player1_name, "lives": 5, "score": 0, "used_words": set()},
            {"name": player2_name, "lives": 5, "score": 0, "used_words": set()}
        ]
        self.current_player_index = 0
        self.time_slice = 12  # Time limit for each round is now 12 seconds
        self.prompt = ""
        self.round_number = 0
        self.game_over = False  # Flag to track game-over state
        self.time_left = self.time_slice  # Initialize time left
        self.timer_running = False  # Flag to track if the timer is running
        self.timer_id = None  # Store the timer ID for cancelling

        # Load music files from the "Music" folder
        self.music_files = load_music_files("Music")
        play_random_music(self.music_files)  # Play random music on loop

        # UI Elements
        self.label_prompt = tk.Label(root, text="Round Prompt:", font=("Arial", 14), bg=bg_color, fg=fg_color)
        self.label_prompt.pack(pady=10)
        
        self.label_player = tk.Label(root, text=f"{self.players[self.current_player_index]['name']}'s Turn", font=("Arial", 12), bg=bg_color, fg=fg_color)
        self.label_player.pack(pady=10)
        
        self.label_round = tk.Label(root, text="Round: 1", font=("Arial", 12), bg=bg_color, fg=fg_color)
        self.label_round.pack(pady=10)

        self.label_score = tk.Label(root, text="Score: 0", font=("Arial", 12), bg=bg_color, fg=fg_color)
        self.label_score.pack(pady=10)
        
        self.entry = tk.Entry(root, font=("Arial", 14), bg="#555555", fg=fg_color)
        self.entry.pack(pady=10)
        
        self.submit_button = tk.Button(root, text="Submit", command=self.check_word, font=("Arial", 12), bg=btn_color, fg=fg_color)
        self.submit_button.pack(pady=10)
        
        # Timer with bold font
        self.timer_label = tk.Label(root, text=f"Time Left: {self.time_slice}s", font=("Arial", 20, "bold"), bg=bg_color, fg=fg_color)  # Bold timer
        self.timer_label.pack(pady=10)
        
        # Load heart image
        self.heart_image = ImageTk.PhotoImage(Image.open("heart.png").resize((20, 20)))

        # Lives display for the current player
        self.lives_label = tk.Label(root, text="", font=("Arial", 12), bg=bg_color, fg=fg_color)
        self.lives_label.pack(pady=10)

        self.entry.bind('<Return>', self.check_word)  # Bind the Enter key to submit the word

        self.start_new_round()

    def start_new_round(self):
        # Only start new round if game is not over
        if not self.game_over:
            self.round_number += 1
            self.label_round.config(text=f"Round: {self.round_number}")
            self.prompt = self.generate_prompt()
            self.label_prompt.config(text=f"Prompt: {self.prompt}")
            self.time_left = self.time_slice  # Reset time to 12 seconds
            self.entry.delete(0, tk.END)  # Clear previous input
            self.update_player_info()  # Update player-specific labels
            self.start_timer()  # Start the timer for the current player

    def generate_prompt(self):
        # Randomly choose between 1 or 2 letters
        prompt_length = random.choice([1, 2])
        return ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=prompt_length))

    def update_player_info(self):
        current_player = self.players[self.current_player_index]
        self.label_player.config(text=f"{current_player['name']}'s Turn")
        self.label_score.config(text=f"Score: {current_player['score']}")
        self.lives_label.config(text=f"Lives: {current_player['lives']}", image=self.heart_image, compound='right')  # Show lives with heart

    def start_timer(self):
        """Start the timer for the current player."""
        self.time_left = self.time_slice  # Reset time
        self.timer_label.config(text=f"Time Left: {self.time_left}s")  # Display reset time
        self.timer_running = True  # Indicate the timer is running
        self.update_timer()  # Begin countdown

    def update_timer(self):
        if self.timer_running:
            if self.time_left > 0:
                self.timer_label.config(text=f"Time Left: {self.time_left}s")
                self.time_left -= 1
                self.timer_id = self.root.after(1000, self.update_timer)  # Schedule the next update in 1 second
            else:
                self.lose_life()  # Time's up, lose a life

    def check_word(self, event=None):
        user_input = self.entry.get().lower()
        current_player = self.players[self.current_player_index]
        
        # Check if word is valid, contains the prompt, is in word_list, and hasn't been used
        if user_input in word_list and user_input not in current_player['used_words']:
            if self.prompt in user_input:
                current_player['score'] += 1
                current_player['used_words'].add(user_input)  # Add the word to used words
                self.entry.delete(0, tk.END)  # Clear input field
                self.label_score.config(text=f"Score: {current_player['score']}")
                self.switch_player()  # Switch to the other player's turn after scoring
            else:
                self.lose_life()  # The word did not contain the prompt
        else:
            self.lose_life()  # Invalid word

    def lose_life(self):
        current_player = self.players[self.current_player_index]
        current_player['lives'] -= 1
        
        # Check if game over
        if current_player['lives'] == 0:
            self.game_over = True
            self.end_game()  # End the game if lives are exhausted
        else:
            self.update_player_info()  # Update lives info
            self.switch_player()  # Switch to the other player's turn

    def switch_player(self):
        self.current_player_index = (self.current_player_index + 1) % 2  # Switch between players
        self.update_player_info()  # Update the player display
        self.reset_timer()  # Reset the timer for the new player

    def reset_timer(self):
        self.root.after_cancel(self.timer_id)  # Cancel the current timer
        self.start_new_round()  # Start a new round for the next player

    def end_game(self):
        winner = max(self.players, key=lambda p: p['score'])  # Determine the winner
        messagebox.showinfo("Game Over", f"{winner['name']} wins with a score of {winner['score']}!")
        self.root.quit()  # Close the game window

# Function to open the player name entry window
def open_player_name_window():
    player_name_window = tk.Toplevel()  # Use Toplevel to avoid extra Tk instance
    player_name_window.title("Enter Player Names")
    
    # Set window size
    window_width = 400
    window_height = 300
    screen_width = player_name_window.winfo_screenwidth()
    screen_height = player_name_window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Configure window size and position
    player_name_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Dark mode colors
    bg_color = "#2E2E2E"
    fg_color = "#FFFFFF"
    btn_color = "#444444"
    player_name_window.configure(bg=bg_color)

    # Create player name entry fields
    label_player1 = tk.Label(player_name_window, text="Player 1 Name:", font=("Arial", 12), bg=bg_color, fg=fg_color)
    label_player1.pack(pady=10)
    entry_player1 = tk.Entry(player_name_window, font=("Arial", 12))
    entry_player1.pack(pady=10)

    label_player2 = tk.Label(player_name_window, text="Player 2 Name:", font=("Arial", 12), bg=bg_color, fg=fg_color)
    label_player2.pack(pady=10)
    entry_player2 = tk.Entry(player_name_window, font=("Arial", 12))
    entry_player2.pack(pady=10)

    def start_game():
        player1_name = entry_player1.get()
        player2_name = entry_player2.get()

        if player1_name and player2_name:
            player_name_window.destroy()  # Close the player name window
            root.deiconify()  # Show the main game window
            BombPartyGame(root, player1_name, player2_name)  # Start the game with entered player names
        else:
            messagebox.showerror("Error", "Please enter names for both players.")

    # Bind the Enter key to start the game
    entry_player2.bind('<Return>', lambda event: start_game())

    start_button = tk.Button(player_name_window, text="Start Game", command=start_game, font=("Arial", 12), bg=btn_color, fg=fg_color)
    start_button.pack(pady=20)

# Create the main window
root = tk.Tk()
root.withdraw()  # Start the main window hidden

# Call the function to open the player name entry window
open_player_name_window()

# Start the Tkinter event loop
root.mainloop()