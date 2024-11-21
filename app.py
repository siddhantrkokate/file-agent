import os
import google.generativeai as genai
import re
from flask import Flask, render_template, request, jsonify

import fileinput

def modify_line(file_path, line_number, new_data):
    # The fileinput.input() function allows you to modify files in-place
    with fileinput.input(file_path, inplace=True) as file:
        for current_line_number, line in enumerate(file, start=1):
            if current_line_number == line_number:
                print(new_data)  # print replaces the current line with the new data
            else:
                print(line, end='')  # print keeps the other lines unchanged

# Set your API key in environment variables for better security
os.environ["GEMINI_API_KEY"] = "AIzaSyDG8JrEOnNgKYr35R1JdSEIMNGC8m9hw-k"  # Make sure to replace with your actual API key

# Configure the generative model using the environment variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-8b",  # Adjust to the model you are using
    generation_config=generation_config,
)

# Initialize Flask application
app = Flask(__name__)

# Common path for file operations
MAIN_PATH = "C:/"

# Helper function to generate AI responses
def generate_response(modify):
    # Start a chat session with an empty history
    chat_session = model.start_chat(history=[])
    
    # Send the modify input to the model
    response = chat_session.send_message(modify)
    
    # Store the response text in a variable
    response_text = response.text
    
    return response_text

# Function to convert placeholders (like ***) into HTML tags
def convert_to_html(response_text):
    # Convert # Heading 1 into <h1>
    response_text = re.sub(r'^# (.*)', r'<h1>\1</h1>', response_text, flags=re.MULTILINE)
    # Convert ## Heading 2 into <h2>
    response_text = re.sub(r'^## (.*)', r'<h2>\1</h2>', response_text, flags=re.MULTILINE)
    # Convert ### Heading 3 into <h3>
    response_text = re.sub(r'^### (.*)', r'<h3>\1</h3>', response_text, flags=re.MULTILINE)
    # Convert **bold text** into <b> tags
    response_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response_text)
    # Convert *italic text* into <i> tags
    response_text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', response_text)
    # Convert line breaks into <br> tags
    response_text = response_text.replace('\n', '<br>')
    # Wrap the response in a div for styling
    return f'<div class="response-container">{response_text}</div>'

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST' and request.is_json:
        user_input = request.json.get('user_input')
        if not user_input:
            return jsonify({'error': 'No user input provided'}), 400

        # Open the file in read mode
        with open("response-history.txt", 'r') as file:
            # Read the entire content of the file and store it in a variable
            file_response_history = file.read()

        print(file_response_history)


        # Identify intent using the AI model
        intent_prompt = """
You are a smart assistant designed to identify the user's intent from a predefined list of intents.

Use the following predefined list of intents:
1. "create file" or any related phrases indicating the creation of a file.
2. "create folder" or any related phrases indicating the creation of a folder.
3. "delete file" or any related phrases indicating the deletion of a file.

Rules:
1. Match the user's input to the closest intent from the list.
2. If no match is found, return "Y".
3. Output should be the index number of the matched intent (e.g., 1, 2, 3) or "Y" if no match is found.
4. When identifying intent, use both the user’s current input and any previous history provided to improve accuracy.

Now, based on the user's input below, identify the intent:
User input: """ + user_input + """
Use the following history to help identify the intent (if relevant):
""" + file_response_history + """
"""

    
        intent_response = generate_response(intent_prompt)
        print(intent_response)

        # store user's intent
        intent = open("intent.txt","w")
        intent_reader = open("intent.txt","r")
        storePre = intent_reader.read()

        if storePre != intent_response:
            intent.write(intent_response[0])
            historyPage = open("history.txt","w")
            historyPage.write("")
            historyPage.close()
            storeHistory = open("response-history.txt","w+")
            storeHistory.write("")
            storeHistory.close()

        intent.close()
        intent_reader.close()

        if str(intent_response[0]) == "1":  # Create file

            # common instructions
            common_instructions = f"""
           You are a smart assistant tasked with identifying and extracting file names and folder names from the given input. Your responses should be casual and intuitive.

            *Output Rules:
            If only a file name is found with valid (and no folder name):
                intension: Create file and file name: [File Name]. Ask for the folder name.
            If only a folder name is found (and no file name):
                intension: Create file, folder name: [Folder Name]. Ask for the file name. *if file name is not valid ask for valid one*
            If file name and folder name both not found:
                intension: create file. Ask for file and folder name. *If file name is not valid ask for valid one.*
            If both file name and folder name are found:
                intension: Create file and file name: [File Name] and folder name: [Folder Name].
            
            Now use this User Input and give me output: "{user_input}". and use this previous responses also {file_response_history}

            """
            response_create_file = generate_response(common_instructions)
            
            # print(response_create_file)
            response_create_file_good = generate_response(
                f"""
                you are the sentence structurer now in this project.

                Task: 
                1. give you the user input = {response_create_file},
                2. understand the input.
                3. Input is the summary of found and not found things so use it and create a output which is like a message to send user.
                3. create a meaningful sentnse which should have everything that sentence want to say.

                Rules:
                1. only craete a sentence not anything else.

                """
            )

            file_folder_finder = generate_response(f"""
            You are the true or false stater. You will be given a input and from that input just find the file name and folder name.
            If file name and folder name (both) got then only show output 1.
            And if file name and folder name not got then only show output 0.

            Now give me output for this: {response_create_file_good}
            """).strip()

            print("Here"+file_folder_finder)


            if str(file_folder_finder) == "1":

                # find file name and store it in data file.abs
                file_name_finder = generate_response(f"""
                "Given the following input, extract and return only the filename (including its extension) from the text. The filename can be anywhere within the input text. If no filename is found, return 'No file name found'."
Just give me response an an output an name of file.
Input: {response_create_file_good}

                """)

                folder_name_finder = generate_response(f"""
                You have given following input and from that return only the name of folder from the text. folder name can be anywhere within input text.
                Just give me response as an output an name of folder.
                Input:{response_create_file_good}
                """)

                historyPage = open("history.txt","w+")
                historyPage.write(file_name_finder)
                historyPage.write(folder_name_finder)
                historyPage.close()

                gen_pos_res = generate_response("Generate response of gthered all deails for creating file working on it.")
                html_response = convert_to_html(gen_pos_res)

                with open("response-history.txt", "r") as res_his_store:
                    existing_data = res_his_store.readlines()  # Read all lines into a list

                with open("response-history.txt", "a") as res_his_store:
                    res_his_store.write(existing_data + "\n")
                    res_his_store.write("User Inputed: " + user_input + "\n")
                    res_his_store.write("Response Shown To User: " + gen_pos_res + "\n")
                return jsonify({'html_response':html_response})
            else:
                html_response = convert_to_html(response_create_file_good)

                with open("response-history.txt", "r") as res_his_store:
                    existing_data = res_his_store.readlines()  # Read all lines into a list

                with open("response-history.txt", "a") as res_his_store:
                    res_his_store.write(existing_data + "\n")
                    res_his_store.write("User Inputed: " + user_input + "\n")
                    res_his_store.write("Response Shown To User: " + response_create_file_good + "\n")
                return jsonify({'html_response':html_response})

            
            

            file_name_1 = generate_response("In this given input what is the name of file tell me as itis with its extension? And return false if file name is not found! given input = "+response_create_file_good).strip()
            folder_name_1 = generate_response("In this given input what is the name of folder? And if folder name not idetified then return false! given input = "+response_create_file_good).strip()
            # identify the file and folder name and store
            # storer = f"from this - {response_create_file_good} find file name and folder name. and create an list add pass each values [filename,foldername] only."
            # playerr = generate_response(storer)
            # print(playerr)

            


        

            

        elif intent_response == "2":  # Create Folder
            folder_name_prompt = f"From this input: '{user_input}', extract only the folder name."
            folder_name = generate_response(folder_name_prompt)

            success_message = f"Okay, creating folder '{folder_name}'."
            html_response = convert_to_html(success_message)
            return jsonify({'html_response': html_response})

        elif intent_response == "3":  # Delete File
            file_name_prompt = f"Extract only the file name from the following user input: '{user_input}'. If no file name is found, return 'error'."
            file_name = generate_response(file_name_prompt)

            if file_name == "error":
                problem_message = "Error: File name not found. Please provide a valid file name for deletion."
                html_response = convert_to_html(problem_message)
                return jsonify({'html_response': html_response})
            else:
                success_message = f"Okay, deleting file '{file_name}'."
                html_response = convert_to_html(success_message)
                return jsonify({'html_response': html_response})

        else:  # Intent not identified
            error_message = generate_response(
                f"""
                You are a smart assistant. You will need to response on given input as an human.
                Given Input:{user_input}
                """
            )
            html_response = convert_to_html(error_message)
            return jsonify({'html_response': html_response})
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
