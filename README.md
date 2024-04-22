
# Streamlit Chat UI with Unify Models

This Streamlit application provides a user interface for interacting with Unify models through chat. It allows users to select models and providers, input text, and view the conversation history with AI assistants.

## Setup

1. Clone this repository:

    ```bash
    git clone https://github.com/samthakur587/LLM_playground
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the Streamlit app:

    ```bash
    streamlit run stream.py
    ```

## Used the Unify streaming API
```python
  from unify import AsyncUnify
  import os
  import asyncio
  async_unify = AsyncUnify(
     # This is the default and optional to include.
     api_key=os.environ.get("UNIFY_KEY"),
     endpoint="llama-2-13b-chat@anyscale"
  )
```
async def main():
   responses = await async_unify.generate(user_prompt="Hello Llama! Who was Isaac Newton?")

asyncio.run(main())

## Usage

1. Input Unify API Key: Enter your Unify API key in the provided text input box on the sidebar.

2. Select Model and Provider: Choose the models and providers from the sidebar dropdown menus.

3. Start Chatting: Type your message in the chat input box and press "Enter" or click the "Send" button.

4. View Conversation History: The conversation history with the AI assistant for each model is displayed in separate containers.

5. Clear History: You can clear the conversation history by clicking the "Clear History" button.

## Features

- **Chat UI**: Interactive chat interface to communicate with AI assistants.
- **Model and Provider Selection**: Choose from a variety of models and providers.
- **Conversation History**: View and track the conversation history with each model.
- **Clear History**: Option to clear the conversation history for a fresh start.

## Dependencies

- Streamlit
- Pandas
- Unify (Custom library for interacting with Unify models)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
