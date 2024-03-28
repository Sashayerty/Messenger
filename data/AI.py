import requests
from api_keys.api_gpt import API_KEY


class AI():
    def __init__(self) -> None:
        self.prompt = {
            "modelUri": "gpt://b1gpchf8l5umrbhroffm/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "2000"
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты самый обыкновенный ChatGPT, который готов помогать людям. Ты знаешь, что тебя используют в приложении SimpleChat."
                }
            ]
        }
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self. headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {API_KEY}"
        }

    def message(self, mess):  
        self.prompt["messages"].append({
            "role": "user",
            "text": mess
        })
        response = requests.post(self.url, headers=self.headers, json=self.prompt)
        result = response.json()
        self.prompt["messages"].append({
            "role": "assistant",
            "text": result["result"]["alternatives"][0]["message"]["text"]
        })
        return result["result"]["alternatives"][0]["message"]["text"]
    

    def messages(self):
        return self.prompt["messages"]
