import os
import google.generativeai as genai
import re
from flask import Flask, render_template, request, jsonify
from datetime import datetime
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

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-8b",
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

        # Step 1
        # Reading the Existing Data from the memory.txt file
        with open("memory.txt", 'r') as file:
            memory_file = file.read()

        # step 2
        import os
        # checking memory file is empty or not
        # if yes then store Nothing. And else then do nothing
        file_path = "memory.txt"

        if os.path.exists(file_path) and os.path.getsize(file_path) == 0:
            with open("memory.txt","w") as write_nothing:
                write_nothing.write("Not available history")

        # Step 3
        # Identify intent using the AI model
        identify_an_intent = generate_response(
            f"""
            From given input text Where compiler asked somthing and user input somthing use this text {user_input} and use this history also of memory for better accuracy {memory_file} and find the intent from this list: 1. create new file. 2.create new folder. As an output return only the index of matched element of list e.g., 1,2.... And if any element not matches then return "Y".
            """
        )

        # Step 4
        # Read the data from intent file: Which is used to store the intent of user in it's index
        intent_reader = open("intent.txt","r")
        sotore_intent_loaded_from_file = intent_reader.read()
        intent_reader.close()

        # Step 5
        # if user intent not matches with data of intent file then
        if str(sotore_intent_loaded_from_file.strip()) != str(identify_an_intent[0].strip()):

            # store new intent index
            with open("intent.txt", "w") as intent:
                intent.write(identify_an_intent[0])

            # empty history
            with open("history.txt", "w") as historyPage:
                historyPage.write("")

            # empty the memory file for new
            with open("memory.txt", "w") as response_history:
                response_history.write("")


        # Step 6 = match the intent

        if str(identify_an_intent[0]) == "1":  # Create file

            # step A.1
            # use a gen prompt to store the history
            with open("memory.txt","r") as fileRead:
                use_memory_file_to_read_create_file_history = fileRead.read()

            # generating good prompt to store in memory
            draft_history_sentence = generate_response(
                f"""
                Use this current Text as current input from user and compiler asked questions {user_input} and working on file creation privous converstations user's history related to this task {use_memory_file_to_read_create_file_history} from this given data understand the texts and create new history as an normal enlish text which can use used in future to understand the data user provided and asked by compiler. As an output just give the history text. Not any explanation or any extra data.
                """
            )

            # stroing draft_history_sentence in memory
            with open("memory.txt","w") as fileRead:
                update_memory = fileRead.write(draft_history_sentence)

            # finding file name and folder name and returning index's
            find_file_folder_name_return_index = f"""
            You are given a text as input. Analyze it to determine which of the following conditions match. Your output should be the index of the matching condition (e.g., 1, 2, 3, etc.). Follow these rules:

Conditions:
The text contains only a file name.
The text contains only a folder name (default folder can be used if instructed).
The text contains both a file name and a folder name (default folder can be used if instructed).
The text contains neither a file name nor a folder name (default folder can be used if instructed).

Now the Given input is : "{draft_history_sentence}".
            """
            file_folder_response_gen = generate_response(find_file_folder_name_return_index)


            # checking the file name is found but why not folder
            if str(file_folder_response_gen.strip()) == "1":
                ask_folder_name = generate_response("Write a message to ask user: a folder name to create a file inside or ask can we use default folder to create? as an response just provide message.")
                html_response = convert_to_html(ask_folder_name)
                return jsonify({'html_response': html_response})
            elif str(file_folder_response_gen.strip()) == "2":
                # asking for folder ame
                ask_folder_name = generate_response("Write a message to ask user: a file name to create a file with valid extension? as an response just provide message.")
                html_response = convert_to_html(ask_folder_name)
                return jsonify({'html_response': html_response})
            elif str(file_folder_response_gen.strip()) == "4":
                # asking for folder and file name both
                ask_folder_name = generate_response("Write a message to ask user: a file name to create a file with valid extension and ask for folder name to create a file inside and give option to user he or she can use default folder to create a file? as an response just provide question. e.g., Okay! i can create a file for you but tell me the name of file with valid extension you want to create. And if you have any specific folder in your mind then please provide the name of it or type 'default' to create in default one. ")
                html_response = convert_to_html(ask_folder_name)
                return jsonify({'html_response': html_response})

            # find folder name and file name and store it in required_data.txt file
            find_file_folder_name = generate_response(f"You have given the text and from it you have to find the file name with its extension and folder name and store the data in this sequence filename.extension, foldename and as an out return only the data in sequence. Given Text : {draft_history_sentence}")
            
            list_file_folder_name = find_file_folder_name.split(",")
            file_name = str(list_file_folder_name[0]).strip()
            folder_name = str(list_file_folder_name[1]).strip()
            print("File name : " + file_name)
            print("Folder name : "+ folder_name)

            import os

            def find_folder(folder_name, start_dir="/"):
                """
                Searches for a folder in the system starting from a given directory.
                
                :param folder_name: Name of the folder to find.
                :param start_dir: Directory to start the search from (default is root "/").
                :return: List of paths where the folder is found.
                """
                result = []
                for root, dirs, _ in os.walk(start_dir):
                    if folder_name in dirs:
                        result.append(os.path.join(root, folder_name))
                return result

            # User input for the folder name
            search_folder = folder_name
            start_directory = "C:/"

            # Search for the folder
            found_paths = find_folder(search_folder, start_directory)

            # Display the results
            if found_paths:
                print(f"Folder '{search_folder}' found at:")
                for path in found_paths:
                    print(path)
                path_creator_file = path + "/" + file_name
                if os.path.exists(path_creator_file):
                    html_response = convert_to_html(generate_response("Write a message and return as an output to say: file already existed"))
                    with open("memory.txt","w") as make_black:
                        make_black.write("Not available history.")
                    return jsonify({'html_response': html_response})
                elif open(path_creator_file,"w"):
                    html_response = convert_to_html(generate_response("Write a message and return as an output to say: file created successfully"))
                    try:
                        os.startfile(path)
                    except Exception as e:
                        html_response = convert_to_html("Facing Problem From Server Side Please Report at siddhantrkokate@gmail.com")
                        with open("memory.txt","w") as make_black:
                            make_black.write("Not available history.")
                        return jsonify({'html_response': html_response})
                    return jsonify({'html_response': html_response})
                else:
                    html_response = convert_to_html(generate_response("Write a message and return as an ouput to say: Facing problem with screent shot contact siddhantrkokate@gmail.com"))
                    return jsonify({'html_response': html_response})
            else:
                html_response = convert_to_html(f"Folder '{search_folder}' not found.")
                return jsonify({'html_response': html_response})


            html_response = convert_to_html(file_name)
            return jsonify({'html_response': html_response})
            

        elif str(identify_an_intent[0]) == "2":  # Create Folder
            
            # Using memory file to read the data
            with open("memory.txt", "r") as memory:
                memory_data = memory.read()

            # Prompt to store the data about task in memory.
            draft_memory_for_creating_folder_based_on_data = generate_response(
                f"""
                You have given a text of compiler asked and on that asked what the user has inputed {user_input} and the history of the same task but stored for you to understand the context or past data or conversation for better accuracy {memory_data} from this compiler asked and user input and history create a valid statment which says same and as an output return that statment.
                """
            )

            # update the existing memory
            with open("memory.txt", "w") as memory:
                memory.write(draft_memory_for_creating_folder_based_on_data)
            
            # conditions
            conditions_folder_creation = generate_response(
                f"""
                Analyze the given statement to determine if it specifies a folder name, a folder location, both, or neither, based on the following conditions:
1. If only the new folder name is provided, return 1.
2. If only the folder name is not provided, return 2.
As output, return only the corresponding number (1, 2).

Given statement: {draft_memory_for_creating_folder_based_on_data}
                """
            ).strip()

            print(conditions_folder_creation)

            if str(conditions_folder_creation) == "1":
                # folder name
                folder_name = str(generate_response(f"You have given text: {draft_memory_for_creating_folder_based_on_data}. from it find the folder name and as an output return that folder name only.").strip())
                try:

                    path = "C:/" + folder_name

                    # Check if the folder already exists
                    if os.path.exists(path):
                        html_response = convert_to_html(generate_response("Write a message to say folder existed and as an output return that message only"))
                        with open("memory.txt","w") as updater:
                            updater.write("")
                        return jsonify({'html_response': html_response})
                    # Create the folder
                    os.makedirs(path, exist_ok=True)
                    with open("memory.txt","w") as updater:
                        updater.write("")
                    html_response = convert_to_html(generate_response("Write a message to say new folder created and as an output return that message only."))
                    return jsonify({'html_response': html_response})
                except Exception as e:
                    html_response = convert_to_html(generate_response("Write a message to say having a prblem in software ask to refer siddhantrkokate@gmail.com to help."))
                    return jsonify({'html_response': html_response})

            elif str(conditions_folder_creation) == "2":
                message1 = generate_response("Write a message to ask user: what name new folder wants to create? as an response just provide message.")
                html_response = convert_to_html(message1)
                return jsonify({'html_response': html_response})


            html_response = convert_to_html("Unkown error: 20X : <a href='mail:siddhantrkokate@gmail.com'>Contact siddhantrkokate@gmail.com</a>.")
            with open("memory.txt","w") as updater:
                updater.write("")
            return jsonify({'html_response': html_response})

        else:  # Intent not identified

            # load memory
            with open("memory.txt", "r") as memory:
                memory_data = memory.read()

            # genarte memory
            memory_gen = generate_response(
                f"""
                You have given a text of compiler asked and on that asked what the user has inputed {user_input} and the history of the same task but stored for you to understand the context or past data or conversation for better accuracy {memory_data} from this compiler asked and user input and history create a valid statment which says same and as an output return that statment.
                """
            )

            # update memory
            with open("memory.txt", "w") as updater:
                updater.write(memory_gen)

            # generate response = You have given data of users current chat history with you in a summary so now you have to respond on the user input: {Hello how are you}. and as an output return the respond on that question or input only. History: {used asked to help}
            response_to_user = generate_response(
                f"""You have given data of users current chat history with you in a summary so now you have to respond on the user input: {user_input}. and as an output return the respond on that question or input only. History: {memory_gen}"""
            )

            html_response = convert_to_html(response_to_user)
            return jsonify({'html_response': html_response})
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
