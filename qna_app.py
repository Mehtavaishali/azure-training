from dotenv import load_dotenv
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

def main():
    try:
        # Load environment variables
        load_dotenv()

        # Retrieve configuration settings
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')
        ai_project_name = os.getenv('QA_PROJECT_NAME')
        ai_deployment_name = os.getenv('QA_DEPLOYMENT_NAME')

        # Validate environment variables
        if not all([ai_endpoint, ai_key, ai_project_name, ai_deployment_name]):
            raise ValueError("One or more required environment variables are missing.")

        # Create client using endpoint and key
        credential = AzureKeyCredential(ai_key)
        ai_client = QuestionAnsweringClient(endpoint=ai_endpoint, credential=credential)

        print("Azure AI Question Answering Chatbot (Type 'quit' to exit)")

        # Loop to handle user questions
        while True:
            user_question = input("\nQuestion: ").strip()

            if user_question.lower() == 'quit':
                print("Exiting...")
                break

            # Submit a question and display the answer
            response = ai_client.get_answers(
                question=user_question,
                project_name=ai_project_name,
                deployment_name=ai_deployment_name
            )

            if response.answers:
                for candidate in response.answers:
                    print("\nAnswer:", candidate.answer)
                    print("Confidence:", candidate.confidence)
                    print("Source:", candidate.source)
            else:
                print("No answer found.")

    except Exception as ex:
        print("Error:", ex)

if __name__ == "__main__":
    main()
