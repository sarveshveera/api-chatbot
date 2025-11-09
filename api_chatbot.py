# API-Integrated Chatbot with Multiple Services
import requests
import json
import os
from datetime import datetime
import random

class APIChatbot:
    def __init__(self):
        # API keys (in production, use environment variables)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.weather_api_key = os.getenv('WEATHER_API_KEY')
        
        # API endpoints
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        self.weather_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # Conversation history
        self.conversation_history = []
        
        # Intent patterns
        self.intent_patterns = {
            'weather': ['weather', 'temperature', 'forecast', 'rain', 'sunny', 'cloudy'],
            'time': ['time', 'date', 'what time', 'current time'],
            'ai_chat': ['tell me', 'explain', 'what do you think', 'opinion', 'advice'],
            'calculation': ['calculate', 'math', 'plus', 'minus', 'multiply', 'divide']
        }

    def detect_intent(self, user_input):
        """ Determine user intent based on keywords """
        text = user_input.lower()
        for intent, keywords in self.intent_patterns.items():
            if any(k in text for k in keywords):
                return intent
        return 'general_chat'

    def get_weather_info(self, city="London"):
        """ Get weather info (safe even if API key missing) """
        if not self.weather_api_key:
            return "Weather service unavailable. Add WEATHER_API_KEY to enable weather lookup."
        
        try:
            params = {'q': city, 'appid': self.weather_api_key, 'units': 'metric'}
            r = requests.get(self.weather_url, params=params, timeout=5)
            if r.status_code == 200:
                data = r.json()
                desc = data['weather'][0]['description']
                temp = data['main']['temp']
                return f"Weather in {city}: {desc}, {temp}°C"
            else:
                return "Could not fetch weather. Check city name."
        except Exception as e:
            return f"Weather service error: {str(e)}"

    def get_current_time(self):
        """ Return local time """
        now = datetime.now()
        return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

    def calculate_expression(self, expr):
        """ Safe math evaluation without code execution """
        try:
            allowed = "0123456789+-*/(). "
            if not all(c in allowed for c in expr):
                return "Use only basic math symbols (+ - * /)."
            
            expr = expr.lower().replace("calculate", "").strip()
            result = eval(expr)
            return f"Answer: {result}"
        except:
            return "Invalid math expression."

    def chat_with_openai(self, user_input):
        """ Call OpenAI API or provide fallback """
        if not self.openai_api_key:
            return random.choice([
                "I can answer better with an OpenAI API key.",
                "Add your OPENAI_API_KEY to unlock AI chat.",
                "AI chat unavailable without API access."
            ])
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }

            messages = [{"role": "system", "content": "You are a helpful assistant."}]
            for entry in self.conversation_history[-3:]:
                messages.append({"role": "user", "content": entry['user']})
                messages.append({"role": "assistant", "content": entry['bot']})
            messages.append({"role": "user", "content": user_input})

            data = {"model": "gpt-3.5-turbo", "messages": messages, "max_tokens": 150}
            
            r = requests.post(self.openai_url, headers=headers, json=data, timeout=10)
            if r.status_code == 200:
                return r.json()['choices'][0]['message']['content']
            return "AI service unavailable."
        except Exception as e:
            return f"OpenAI error: {str(e)}"

    def get_response(self, user_input):
        """ Main router for chatbot commands """
        intent = self.detect_intent(user_input)

        if intent == 'weather':
            words = user_input.split()
            city = "London"
            for i, w in enumerate(words):
                if w.lower() in ["in", "at", "for"] and i + 1 < len(words):
                    city = words[i + 1]
            return self.get_weather_info(city)

        if intent == 'time':
            return self.get_current_time()

        if intent == 'calculation':
            return self.calculate_expression(user_input)

        if intent == 'ai_chat':
            return self.chat_with_openai(user_input)

        # General chat
        if self.openai_api_key:
            return self.chat_with_openai(user_input)

        return random.choice([
            "Tell me more!",
            "That's interesting.",
            "Hmm, continue…",
            "I like where this is going."
        ])

    def chat(self):
        """ Main run loop """
        print("🌐 API Chatbot ready!")
        print("Type 'quit' to exit.")
        print("-" * 70)

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ["quit", "exit"]:
                print("Goodbye!")
                break
            if user_input == "":
                continue

            response = self.get_response(user_input)
            print("Bot:", response)

            self.conversation_history.append({
                "user": user_input,
                "bot": response,
                "timestamp": datetime.now()
            })


if __name__ == "__main__":
    print("✅ API Chatbot booting…")
    print("Set `OPENAI_API_KEY` and `WEATHER_API_KEY` for full features.")
    print()
    APIChatbot().chat()