import os
import tkinter as tk
import google.generativeai as genai

# Set your API key (use environment variables or hardcode for testing purposes)
os.environ["GEMINI_API_KEY"] = "AIzaSyDG8JrEOnNgKYr35R1JdSEIMNGC8m9hw-k"

# Configure the generative model
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-8b",
    generation_config=generation_config,
)

# Start chat session
chat_session = model.start_chat(history=[])

# Function to send message and display it in the chat window
def send_message():
    user_message = message_entry.get()  # Get the message from the entry field
    if user_message != "":  # Only proceed if there's some text
        chat_box.config(state=tk.NORMAL)  # Enable the chat box for editing
        chat_box.insert(tk.END, f":User    {user_message}\n")  # Insert user message
        
        # Get response from Gemini AI API
        response = chat_session.send_message(user_message)
        bot_response = response.text  # Get the text response from Gemini AI
        
        # Display the bot's response in the chat
        chat_box.insert(tk.END, f"Bot: {bot_response}\n")  # Insert bot response
        chat_box.config(state=tk.DISABLED)  # Disable editing of the chat box
        message_entry.delete(0, tk.END)  # Clear the message entry field

# Setting up the main window
root = tk.Tk()
root.title("Chatbot UI")
root.geometry("400x500")
root.config(bg="black")

# Create a Chat window (Text widget) for displaying the conversation
chat_box = tk.Text(root, bg="black", fg="white", font=("Arial", 12), width=40, height=15, state=tk.DISABLED)
chat_box.pack(pady=10)

# Create a frame for the entry field with a grey border
entry_frame = tk.Frame(root, bg="black")
entry_frame.pack(pady=20, padx=20, fill=tk.X)  # Add padding and fill the width

# Create a frame for the border effect
border_frame = tk.Frame(entry_frame, bg="grey", bd=1)  # Grey border with 1 pixel thickness
border_frame.pack(padx=5, pady=5, fill=tk.X)  # Padding around the border

# Create an entry field for the user to type their message
message_entry = tk.Entry(border_frame, bg="black", fg="white", font=("Arial", 14), 
                          borderwidth=0)  # Set font size to 14 px and no border
message_entry.pack(pady=5, padx=5, fill=tk.X)  # Add padding and fill the width

# Create a send button to trigger the message
send_button = tk.Button(root, text="Send", font=("Arial", 12), bg="green", fg="white", command=send_message)
send_button.pack(pady=5)

# Run the Tkinter event loop
root.mainloop()
