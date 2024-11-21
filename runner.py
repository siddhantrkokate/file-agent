import os
import google.generativeai as genai

# Set your API key (use environment variables or hardcode for testing purposes)
os.environ["GEMINI_API_KEY"] = "AIzaSyDG8JrEOnNgKYr35R1JdSEIMNGC8m9hw-k"

# Configure the generative model
genai.configure(api_key="AIzaSyDG8JrEOnNgKYr35R1JdSEIMNGC8m9hw-k")

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

# Take user input and get response
user_input = input("Enter your message: ")
response = chat_session.send_message(user_input)

# Print the response
print("Response from Gemini AI:")
print(response.text)
