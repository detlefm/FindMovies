from pathlib import Path
import time
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def count_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def get_response_time_and_tokens(prompt, model="gpt-4o"):
    token_count = count_tokens(prompt, model)

    start_time = time.time()
    completion = client.chat.completions.create(
            model=model,
            messages=[ {"role": "user", "content": prompt}], # type: ignore
        )

    end_time = time.time()
    duration = end_time - start_time

    #response_text = response['choices'][0]['message']['content']
    response_text =str(completion.choices[0].message.content if completion.choices else '')
    response_tokens = count_tokens(response_text, model)
    total_tokens = token_count + response_tokens

    print(f"Prompt Tokens: {token_count}")
    print(f"Response Tokens: {response_tokens}")
    print(f"Total Tokens: {total_tokens}")
    print(f"Time Taken: {duration:.2f} seconds")
    print(f"Tokens per Second: {total_tokens / duration:.2f}")
    print(f"Response: {response_text}")


# Beispiel verwenden

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        txt = sys.argv[1]
        if txt.startswith('@'):
            txt = Path(txt[1:]).read_text(encoding='utf-8')
        get_response_time_and_tokens(txt)
    else:
        print('Prompt text needed')


