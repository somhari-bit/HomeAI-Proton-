from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Variables to store current values
current_fan_speed = "medium"
current_ac_temp = 24

@app.route('/')
def index():
    return render_template('control.html', fan_speed=current_fan_speed, ac_temp=current_ac_temp)

@app.route('/update', methods=['POST'])
def update():
    global current_fan_speed, current_ac_temp
    data = request.json
    current_fan_speed = data.get('fan_speed', current_fan_speed)
    current_ac_temp = data.get('ac_temperature', current_ac_temp)
    return jsonify({"status": "success", "fan_speed": current_fan_speed, "ac_temperature": current_ac_temp})

@app.route('/get_values', methods=['GET'])
def get_values():
    return jsonify({"fan_speed": current_fan_speed, "ac_temperature": current_ac_temp})


class ChatBot:
    started = False

    @staticmethod
    def start():
        # Initialize or start the ChatBot
        ChatBot.started = True
        print("ChatBot has started.")

    @staticmethod
    def isUserInput():
        # Method to check if there is user input
        # Replace with actual implementation
        return False

    @staticmethod
    def popUserInput():
        # Method to retrieve user input
        # Replace with actual implementation
        return ""

    @staticmethod
    def addAppMsg(msg):
        # Method to add a message to the application
        print(f"App Message: {msg}")

    @staticmethod
    def close():
        # Method to properly close or shut down the ChatBot
        print("ChatBot has been closed.")


# Example of setting the ChatBot as started
ChatBot.started = True

# If you need to have user profiles or settings, you can include that here
user_profiles = {
    "user1": {"fan_speed": "medium", "ac_temperature": 24},
    "user2": {"fan_speed": "high", "ac_temperature": 20},
    # Add more profiles as needed
}


def get_user_profile(user_name):
    # Retrieve the profile for a given user name
    return user_profiles.get(user_name, {})


def update_user_profile(user_name, profile_data):
    # Update the profile for a given user name
    user_profiles[user_name] = profile_data
    print(f"Updated profile for {user_name}: {profile_data}")


def main():
    # Example main function to test the ChatBot
    chatbot = ChatBot()
    chatbot.start()

    if chatbot.isUserInput():
        user_input = chatbot.popUserInput()
        print(f"User Input: {user_input}")
        chatbot.addAppMsg(f"Received user input: {user_input}")

    chatbot.close()


if __name__ == '__main__':
    main()

