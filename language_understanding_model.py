from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta, date, timezone
from dateutil.parser import parse as is_date
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

def main():
    try:
        # Load environment variables
        load_dotenv()

        # Retrieve configuration settings
        ls_prediction_endpoint = os.getenv('LS_CONVERSATIONS_ENDPOINT')
        ls_prediction_key = os.getenv('LS_CONVERSATIONS_KEY')

        # Validate environment variables
        if not ls_prediction_endpoint or not ls_prediction_key:
            raise ValueError("Missing required environment variables.")

        # User input loop
        while True:
            user_text = input('\nEnter some text ("quit" to stop): ').strip()
            if user_text.lower() == 'quit':
                print("Exiting...")
                break

            # Create a client for the Azure Language Service
            client = ConversationAnalysisClient(
                ls_prediction_endpoint, AzureKeyCredential(ls_prediction_key)
            )

            cls_project = 'Clock'
            deployment_slot = 'production'

            with client:
                query = user_text
                result = client.analyze_conversation(
                    task={
                        "kind": "Conversation",
                        "analysisInput": {
                            "conversationItem": {
                                "participantId": "1",
                                "id": "1",
                                "modality": "text",
                                "language": "en",
                                "text": query
                            },
                            "isLoggingEnabled": False
                        },
                        "parameters": {
                            "projectName": cls_project,
                            "deploymentName": deployment_slot,
                            "verbose": True
                        }
                    }
                )

            # Extract top intent and entities
            prediction = result["result"]["prediction"]
            top_intent = prediction["topIntent"]
            entities = prediction.get("entities", [])

            print("\nTop Intent:", top_intent)
            print("Confidence Score:", prediction["intents"][0]["confidenceScore"])

            if entities:
                print("\nEntities Found:")
                for entity in entities:
                    print(f"  - {entity['category']}: {entity['text']} (Confidence: {entity['confidenceScore']})")

            # Process the intent
            if top_intent == 'GetTime':
                location = next((e["text"] for e in entities if e["category"] == "Location"), "local")
                print("Time:", GetTime(location))

            elif top_intent == 'GetDay':
                date_string = next((e["text"] for e in entities if e["category"] == "Date"), date.today().strftime("%m/%d/%Y"))
                print("Day:", GetDay(date_string))

            elif top_intent == 'GetDate':
                day = next((e["text"] for e in entities if e["category"] == "Weekday"), "today")
                print("Date:", GetDate(day))

            else:
                print("Try asking for the time, day, or date.")

    except Exception as ex:
        print("Error:", ex)

def GetTime(location):
    """Returns the current time in the specified location."""
    timezone_offsets = {
        "local": 0,
        "london": 0,
        "sydney": 11,
        "new york": -5,
        "nairobi": 3,
        "tokyo": 9,
        "delhi": 5.5
    }
    offset = timezone_offsets.get(location.lower(), None)

    if offset is not None:
        time = datetime.now(timezone.utc) + timedelta(hours=offset)
        return f"{time.hour}:{time.minute:02d}"
    
    return f"I don't know the time in {location}."

def GetDate(day):
    """Returns the date for a specified weekday in the current week."""
    weekdays = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, 
                "friday": 4, "saturday": 5, "sunday": 6}

    today = date.today()
    day_lower = day.lower()

    if day_lower == 'today':
        return today.strftime("%m/%d/%Y")
    elif day_lower in weekdays:
        offset = weekdays[day_lower] - today.weekday()
        return (today + timedelta(days=offset)).strftime("%m/%d/%Y")

    return "I can only determine dates for today or named days of the week."

def GetDay(date_string):
    """Returns the day of the week for a given date."""
    try:
        date_object = datetime.strptime(date_string, "%m/%d/%Y")
        return date_object.strftime("%A")
    except ValueError:
        return "Enter a valid date in MM/DD/YYYY format."

if __name__ == "__main__":
    main()
