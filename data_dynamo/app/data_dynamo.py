from openai import OpenAI
from pydantic import BaseModel


class Response(BaseModel):
    action: str
    response: str


class DatasetChatbot:
    def __init__(self):
        self.client = OpenAI()
        self.conversation_history = []
        self.current_step_index = 0
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
            "use_case": "Ask about the use case of the dataset.",
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

    def generate_response(self, prompt):
        messages = self.conversation_history + [{"role": "system", "content": prompt}]
        response = self.client.chat.completions.create(
            model="gpt-4", messages=messages, temperature=0.7
        )
        return Response(action="next", response=response.choices[0].message.content)

    def process_input(self, user_input):
        self.update_conversation("user", user_input)

        # First, generate a follow-up response
        follow_up = self.generate_response(self.prompts["follow_up"])

        if follow_up.action == "next":
            # If we're moving to the next step, generate the response for that step
            if self.current_step_index < len(self.steps) - 1:
                self.current_step_index += 1
            current_step = self.steps[self.current_step_index]
            prompt = self.prompts[current_step]
            response = self.generate_response(prompt)
        else:
            # If we're modifying, use the follow-up response
            response = follow_up

        self.update_conversation("assistant", response.response)
        return response.response

    def start_conversation(self):
        first_step = self.steps[0]
        prompt = self.prompts[first_step]
        response = self.generate_response(prompt)
        self.update_conversation("assistant", response.response)
        return response.response
