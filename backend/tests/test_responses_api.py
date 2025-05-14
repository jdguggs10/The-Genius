import os
from openai import OpenAI

# 1. Set your API key (ensure OPENAI_API_KEY is in your env)
api_key = os.getenv("OPENAI_API_KEY")

# 2. Initialize the OpenAI client
client = OpenAI(api_key=api_key)

# 3. Make a dummy Responses API call
response = client.responses.create(
    model="gpt-4.1",              # Using the gpt-4.1 model
    instructions="You are a helpful assistant.",
    input="Ping"
)

# 4. Print out the model's reply
print(response.output_text) 