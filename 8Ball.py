import tkinter as tk
from PIL import Image, ImageTk
import random
import os
import sys

# --- PYINSTALLER PATH BUNDLING FIX ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- CONSTANTS & CONFIG ---
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
IMAGE_PATH = resource_path("8ball.png")

# Official 20 Magic 8 Ball Responses
RESPONSES = [
    "It is certain", "It is decidedly so", "Without a doubt", "Yes definitely",
    "You may rely on it", "As I see it, yes", "Most likely", "Outlook good",
    "Yes", "Signs point to yes", "Reply hazy, try again", "Ask again later",
    "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
    "Don't count on it", "My reply is no", "My sources say no", 
    "Outlook not so good", "Very doubtful"
]

# Hex codes transitioning from dark background indigo to bright white floating font
FADE_STEPS = ["#12163b", "#222a6b", "#3c489b", "#5e6cc4", "#8ba0e8", "#c2cff7", "#ffffff"]

# --- ANIMATION FUNCTIONS ---

def shake_effect(count=0):
    """Displaces the background image rapidly to simulate a real physical shake."""
    if count < 10:  # Shakes back and forth 10 times
        # Alternate displacement values (-8 pixels to +8 pixels)
        dx = 8 if count % 2 == 0 else -8
        dy = 4 if count % 4 == 0 else -4
        
        # Move the background image asset on the canvas
        canvas.move(ball_image_id, dx, dy)
        
        # Schedule the next shake frame in 40 milliseconds
        root.after(40, lambda: shake_effect(count + 1))
    else:
        # Reset the image precisely back to the center of the 600x600 canvas
        canvas.coords(ball_image_id, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        # Choose a random answer and start floating it up
        reveal_text(random.choice(RESPONSES))

def reveal_text(answer, step_index=0):
    """Gradually changes the text color to simulate the die floating up to the viewport surface."""
    if step_index == 0:
        # Format long answers into two lines so they fit nicely inside the triangle
        if len(answer) > 15 and " " in answer:
            mid = len(answer) // 2
            split_idx = answer.find(" ", mid)
            if split_idx == -1: split_idx = answer.rfind(" ", 0, mid)
            answer = answer[:split_idx] + "\n" + answer[split_idx+1:]
        
        canvas.itemconfig(response_text_id, text=answer, fill=FADE_STEPS[0])
        root.after(150, lambda: reveal_text(answer, step_index + 1))
    elif step_index < len(FADE_STEPS):
        # Apply the next brightest color hex code
        canvas.itemconfig(response_text_id, fill=FADE_STEPS[step_index])
        root.after(100, lambda: reveal_text(answer, step_index + 1))
    else:
        # Animation complete, re-enable the button for the next turn
        shake_button.config(state=tk.NORMAL)

def trigger_shake():
    """Handles button interaction, locking inputs while animating."""
    shake_button.config(state=tk.DISABLED)  # Prevent double-clicking during animation
    canvas.itemconfig(response_text_id, text="")  # Clear previous answer instantly
    shake_effect()  # Kick off step 1 of the sequence

# --- GUI INITIALIZATION ---
root = tk.Tk()
root.title("Magic 8 Ball")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.configure(bg="#1a1a1a")
root.resizable(False, False)

# 1. Full-Window Canvas
canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="#1a1a1a", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Load background graphic
try:
    img = Image.open(IMAGE_PATH)
    img = img.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(img)
    canvas.image = bg_image 
    ball_image_id = canvas.create_image(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, image=bg_image)
except Exception as e:
    print(f"Error loading image: {e}")
    ball_image_id = canvas.create_oval(50, 50, 550, 550, fill="black")

# 2. Top Prompt Label Overlay
prompt_text_id = canvas.create_text(
    WINDOW_WIDTH // 2, 40,
    text="Concentrate on your question...",
    font=("Helvetica", 16, "italic"),
    fill="#ffffff"
)

# 3. Floating Response Text Overlay
# Currently targeting the perfect dead center (300, 300)
response_text_id = canvas.create_text(
    (WINDOW_WIDTH // 2),
    (WINDOW_HEIGHT // 2) - 10,
    text="",
    font=("Helvetica", 14, "bold"),
    fill="#ffffff",
    justify=tk.CENTER,
    width=120
)

# 4. Action Layer ("Shake!" Button Overlay)
shake_button = tk.Button(
    root, 
    text="SHAKE!", 
    font=("Helvetica", 12, "bold"),
    bg="#333333", 
    fg="#ffffff", 
    activebackground="#555555",
    activeforeground="#ffffff",
    padx=20, 
    pady=10,
    command=trigger_shake
)

button_window = canvas.create_window(
    WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60,
    window=shake_button
)

# Run the program
root.mainloop()