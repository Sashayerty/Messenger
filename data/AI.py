import requests
from dotenv import load_dotenv
import os

load_dotenv()


class AI():
    def __init__(self) -> None:
        self.msgs = []
        self.prompt = {
            "modelUri": "gpt://b1gpchf8l5umrbhroffm/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "5000"
            },
            "messages": self.msgs
        }
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self. headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {os.getenv("API_KEY")}"
        }

    def message(self, mess): 
        self.msgs.append({
            "role": "user",
            "text": mess
        }) 
        self.prompt["messages"] = self.msgs
        response = requests.post(self.url, headers=self.headers, json=self.prompt)
        result = response.json()
        self.prompt["messages"].append({
            "role": "assistant",
            "text": result["result"]["alternatives"][0]["message"]["text"]
        })
    

    def get_messages(self):
        return self.prompt["messages"]
    
    def set_messages(self, messags):
        self.msgs = messags
 