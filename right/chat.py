#!/usr/bin/env python3
"""Interactive chat with Qwen3-8B via vLLM OpenAI API."""

from openai import OpenAI
import sys

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")
MODEL = "Qwen3-8B"

def chat():
    messages = []
    print("Qwen3-8B 交互式对话")
    print("命令: /quit 退出 | /clear 清空历史 | /think 开启思考 | /nothink 关闭思考")
    print("-" * 60)

    thinking = False  # default: no thinking

    while True:
        try:
            user_input = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input == "/quit":
            print("再见！")
            break
        if user_input == "/clear":
            messages = []
            print("[历史已清空]")
            continue
        if user_input == "/think":
            thinking = True
            print("[思考模式已开启]")
            continue
        if user_input == "/nothink":
            thinking = False
            print("[思考模式已关闭]")
            continue

        messages.append({"role": "user", "content": user_input})

        extra_body = {}
        if not thinking:
            extra_body["chat_template_kwargs"] = {"enable_thinking": False}

        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=0.8,
                stream=True,
                extra_body=extra_body if extra_body else None,
            )

            print("\nQwen: ", end="", flush=True)
            full_reply = ""
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    print(delta.content, end="", flush=True)
                    full_reply += delta.content
            print()

            messages.append({"role": "assistant", "content": full_reply})

        except Exception as e:
            print(f"\n[错误] {e}")
            messages.pop()  # remove failed user message

if __name__ == "__main__":
    chat()
