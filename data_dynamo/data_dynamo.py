from openai import OpenAI
from pydantic import BaseModel


class Response(BaseModel):
    action: str
    response: str


class DatasetChatbot:
    def __init__(self):
        self.client = OpenAI()
        self.conversation_history = []
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
            ## Role
            You are an AI assistant specializing in generating sample datasets. Your role is to interact with users professionally and concisely, guiding them through the conversation one question at a time and creating customized datasets using Python. 

            You answer in the following format:
            - action: modify/next
            - response: Your response to the user's input.
            
            ## Step 1: Use Case
            Greet the user and ask about the use case of the dataset.
            """,
            "columns": """
            ## Step 2: Columns
            Based on the use case, suggest appropriate columns for the dataset. Include the column name, data type, and a brief description for each. Ask the user if they want to make modifications or continue.
            """,
            "ranges_distributions": """
            ## Step 3: Ranges and Distributions
            Provide realistic ranges and distributions for float and integer columns. Ask the user if they want to make modifications or continue.
            """,
            "categories": """
            ## Step 4: Categories
            Suggest categories for categorical columns. Ask the user if they want to make modifications or continue.
            """,
            "constraints": """
            ## Step 5: Constraints
            Suggest constraints considering the specific use case. Ask the user if they want to make modifications or continue.
            """,
            "edge_cases": """
            ## Step 6: Edge Cases
            Suggest edge cases for the dataset. Ask the user if they want to make modifications or continue.
            """,
            "data_volume": """
            ## Step 7: Data Volume
            Ask the user about the desired data volume for the dataset.
            """,
            "delivery": """
            ## Step 8: Delivery
            Provide the full Python code to generate the dataset. Ask the user if they need any further assistance.
            """,
            "follow_up": """ 
            ## Follow-Up
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

    def run_step(self, step):
        prompt = self.prompts[step]
        Response = self.generate_response(prompt)
        self.update_conversation("system", prompt)
        self.update_conversation("assistant", Response.response)
        return Response.response

    def generate_response(self, prompt):
        messages = self.conversation_history + [{"role": "system", "content": prompt}]
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            response_format=Response,
        )
        return response.choices[0].message.parsed

    def chat(self):
        for step in self.steps:
            response = self.run_step(step)
            print(f"DataDynamo: {response}")

            while True:
                user_input = input("You: ")
                self.update_conversation("user", user_input)
                follow_up = self.generate_response(self.prompts["follow_up"])
                if follow_up.action == "next":
                    break
                elif follow_up.action == "modify":
                    self.update_conversation("assistant", follow_up.response)
                    print(f"DataDynamo: {follow_up.response}")
                else:
                    print("DataDynamo: I'm sorry, I didn't understand that.")
                    continue


if __name__ == "__main__":
    chatbot = DatasetChatbot()
    chatbot.chat()
