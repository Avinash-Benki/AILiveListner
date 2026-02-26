import requests
EDEN_AI_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNTk0NTQxYzgtMGVhZS00M2VlLWE4YzgtZTlkZjQ4N2NjNTYwIiwidHlwZSI6ImFwaV90b2tlbiJ9.jgt7OtrYpfamyQ9PeluVHbQoejo9vNaOJi-Ts8xlsOE"
url = "https://api.edenai.run/v3/llm/chat/completions"
headers = {
    "Authorization": f"Bearer {EDEN_AI_API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "model": "anthropic/claude-haiku-4-5",
    "messages": [
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ]
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()
print(data)