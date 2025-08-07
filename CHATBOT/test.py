import openai

openai.api_key = "sk-abcdijkl1234uvwxabcdijkl1234uvwxabcdijkl"  # paste your new key here

response = openai.ChatCompletion.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "user", "content": "Hello, who are you?"}
    ]
)

print(response['choices'][0]['message']['content'])
