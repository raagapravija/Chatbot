def generate_response(llm, prompt, history):
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-5:]])
    
    instruction = f"""You are a knowledgable and helpful AI assistant. Provide clear, confident answers to technical questions and general questions.
If a question is unclear, ask for clarification once. Otherwise, answer directly. Do not ask follow-up questions unless specifically requested.
    
Current conversation:
{context}
User: {prompt}
Assistant:"""
    
    try:
        response = llm.invoke(instruction)
        return response.strip()
    except Exception as e:
        return f"I encountered an error. Could you please repeat your question?"