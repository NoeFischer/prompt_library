from openai import OpenAI
from pydantic import BaseModel


class Response(BaseModel):
    action: str
    response: str


class DatasetChatbot:
    def __init__(self):
        self.client = OpenAI()
        self.conversation_history = []
        self.dataset_specs = {
            "use_case": "",
            "columns": [],
            "volume": {},
        }
        self.steps = ["use_case", "suggest_columns"]
        self.system_prompts = {
            "follow_up": "Determine if you have enough information for this step. Additionally, provide an action to take next, which can be either 'continue' or 'next'.",
            "use_case": "Greet the user and ask about the use case of the dataset.",
            "suggest_columns": "Based on the use case '{self.dataset_specs['use_case']}', suggest appropriate columns for the dataset. Include the column name, data type, and a brief description for each. Ask the user if they want to make modifications or continue.",
        }

    def create_prompt(self, system_prompt):
        Response = self.generate_response(system_prompt)
        self.update_conversation(system_prompt, Response.response)
        return Response.response

    def generate_response(self, system_prompt):
        messages = self.conversation_history + [{"role": "system", "content": system_prompt}]
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini", messages=messages, temperature=0.7, response_format=Response
        )
        return response.choices[0].message.parsed

    def update_conversation(self, user_input, assistant_output):
        self.conversation_history.extend(
            [{"role": "user", "content": user_input}, {"role": "assistant", "content": assistant_output}]
        )

    def chat(self):
        for step in self.steps:
            response = self.create_prompt(self.system_prompts[step])
            print(f"DataDynamo: {response}")

            while True:
                user_input = input("You: ")
                follow_up = self.generate_response(self.system_prompts["follow_up"])

                if follow_up.action == "next":
                    break
                else:
                    print(f"DataDynamo: {follow_up.response}")
                    self.update_conversation(user_input, follow_up.response)

        print("DataDynamo: Thank you for using DataDynamo. Good luck with your project!")


if __name__ == "__main__":
    chatbot = DatasetChatbot()
    chatbot.chat()
