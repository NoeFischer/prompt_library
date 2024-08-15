import json

from openai import OpenAI
from pydantic import BaseModel


class StepResponse(BaseModel):
    action: str
    response: str


class DatasetChatbot:
    def __init__(self):
        self.client = OpenAI()
        self.conversation_history = []
        self.current_step = 0
        self.steps = [
            "use_case",
            "columns",
            "ranges_distributions",
            "categories",
            "constraints",
            "edge_cases",
            "data_volume",
            "delivery",
        ]
        self.prompts = {
            "use_case": """
            You are an AI assistant specializing in generating sample datasets. Your role is to interact with users professionally and efficiently, guiding them through the conversation one question at a time and creating customized datasets. You refuse to answer any questions that are not related to the use case of the dataset. Greet the user and ask about the use case of the dataset.
            """,
            "columns": "Suggest appropriate columns for the dataset based on the use case.",
            "ranges_distributions": "Provide realistic ranges and distributions for float and integer columns.",
            "categories": "Suggest categories for categorical columns.",
            "constraints": "Suggest constraints considering the specific use case.",
            "edge_cases": "Suggest edge cases for the dataset.",
            "data_volume": "Ask about the desired data volume for the dataset.",
            "delivery": "Provide the full Python code to generate the dataset.",
            "follow_up": """
            Analyze the user's response and determine if you can move to the next step or need to take a different action:
            1. If the user requests changes:
                - Set the action to "modify".
                - Provide specific suggestions for modifications based on their feedback.
            2. If the user expresses agreement or satisfaction:
                - Set the action to "next".
                - Prepare to move to the next step in the process.

            Always include reasoning for your choice of action.
            """,
        }

    def update_conversation(self, input_type, input_content):
        self.conversation_history.append({"role": input_type, "content": input_content})

    def generate_response(self, step, user_input=None):
        if user_input:
            self.update_conversation("user", user_input)
        # Update the conversation history with the system prompt
        self.update_conversation("system", self.prompts[step])
        # Generate the response
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            temperature=0.7,
            messages=self.conversation_history,
            response_format=StepResponse,
        )
        assistant_response = json.loads(response.choices[0].message.content)
        # Update the conversation history with the assistant's response
        self.update_conversation("assistant", assistant_response["response"])
        return assistant_response

    def conversation_flow(self, user_input=None):
        while self.current_step < len(self.steps):
            current_step = self.steps[self.current_step]
            if user_input is None:
                return self.generate_response(current_step)["response"]

            while True:
                follow_up = self.generate_response("follow_up", user_input)

                if follow_up["action"] == "next":
                    self.current_step += 1
                    break
                else:
                    return follow_up["response"]

            user_input = None

        return (
            "Thank you for using DataDynamo. Your dataset creation process is complete."
        )
