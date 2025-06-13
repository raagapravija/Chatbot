from llm_utils import load_llm

def generate_response(prompt, history):
    """
    Generates AI response using Groq via LangChain
    Args:
        prompt (str): Current user message
        history (list): Conversation history in format [{"role": "user|assistant", "content": str}]
    """
    llm = load_llm()
    
    # Format messages for LangChain
    messages = [
        {"role": msg["role"], "content": msg["content"]} 
        for msg in history[-5:]  # Use last 5 messages for context
    ]
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = llm.invoke(messages).content
        return response.strip()
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"