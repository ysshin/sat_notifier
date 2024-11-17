import requests
import time
import subprocess
from datetime import datetime, timedelta

# URL for SAT June test availability
JUNE_TEST_URL = "https://aru-test-center-search.collegeboard.org/prod/test-centers?date=2025-06-07&zip=95124&country=US"

# Recipients' phone numbers (iMessage contacts)
RECIPIENTS = ["phone_number1_to_be_added", "phone_number2_to_be_added"]

# Store previous result for change detection
previous_june = None

# Track the next allowed message time
next_message_time = datetime.now()
is_first_message = True  # Flag to indicate whether this is the first message

def fetch_and_check_availability(url):
    try:
        # Fetch the data
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Find the closest school with available seats
        available_schools = [
            school for school in data if school.get("seatAvailability")
        ]
        if available_schools:
            closest_school = min(available_schools, key=lambda s: s["distance"])
            # Format the message to show name, city, and distance (one decimal place)
            return f"{closest_school['name']}\n    {closest_school['city']} ({closest_school['distance']:.1f} miles)"
        else:
            return "None available"
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return "Error checking availability"

def check_schools():
    global previous_june, next_message_time, is_first_message

    # Check for June test
    june_closest = fetch_and_check_availability(JUNE_TEST_URL)

    # Detect changes (skip for the first message)
    if not is_first_message:
        june_change_note = "[changed!]" if june_closest != previous_june else "[no change]"
    else:
        june_change_note = ""

    # Update previous result
    previous_june = june_closest

    # Prepare the message
    message = (
        f"SAT Availability (closest):\n"
        f"- June {june_change_note}:\n    {june_closest}\n"
        f"Next message will be in 6 hours"
    )

    # Send the message immediately if it's the first run or if there's a change
    if is_first_message or june_change_note == "[changed!]":
        send_message_to_all_recipients(message)
        next_message_time = datetime.now() + timedelta(hours=6)
        is_first_message = False
    # Otherwise, send the message only if 6 hours have passed
    elif datetime.now() >= next_message_time:
        send_message_to_all_recipients(message)
        next_message_time = datetime.now() + timedelta(hours=6)

def send_message_to_all_recipients(message):
    for recipient in RECIPIENTS:
        send_imessage(recipient, message)

def send_imessage(recipient, message):
    try:
        # Use AppleScript to send the message via iMessage
        applescript = f"""
        tell application "Messages"
            set targetService to 1st service whose service type = iMessage
            set targetBuddy to buddy "{recipient}" of targetService
            send "{message}" to targetBuddy
        end tell
        """
        subprocess.run(["osascript", "-e", applescript], check=True)
        print(f"Message sent to {recipient}: {message}")
    except subprocess.CalledProcessError as e:
        print(f"Error sending iMessage to {recipient}: {e}")

print("Script started. Checking SAT availability every minute...")

# Continuously check availability every minute
while True:
    check_schools()
    time.sleep(60)  # Wait 1 minute before checking again