from gradio_client import Client

client = Client("ayscript/health_atlas")
result = client.predict(
		message="Do you understand yoruba?",
		system_message="You are a friendly Chatbot.",
		max_tokens=512,
		temperature=0.7,
		top_p=0.95,
		api_name="/chat"
)

print("generating.....\n")
print(result)