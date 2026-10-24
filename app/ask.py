"""第1回: 素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask
    uv run python -m app.ask "LoRAとは何ですか？"  # 最初の質問を指定

起動後は会話履歴を保って続けて質問できる。ツールは使わない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse
from typing import Protocol

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 第1回の講座固有質問例。正しい答えは data/glossary.json にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"
EXIT_COMMANDS = {"exit", "quit", "終了"}


class ChatSession(Protocol):
    def send_message(self, message: str) -> genai.types.GenerateContentResponse: ...


def _print_usage(response: genai.types.GenerateContentResponse) -> None:
    usage = response.usage_metadata
    if usage is None:
        print("[tokens] トークン使用量はAPI応答に含まれていません")
        return

    print(
        f"[tokens] input={usage.prompt_token_count} "
        f"output={usage.candidates_token_count}"
    )


def ask(question: str, chat: ChatSession | None = None) -> str:
    if chat is None:
        client = genai.Client(api_key=get_api_key())
        response = client.models.generate_content(model=MODEL, contents=question)
    else:
        response = chat.send_message(question)

    _print_usage(response)
    return response.text


def run_interactive(chat: ChatSession, first_question: str | None = None) -> None:
    question = first_question
    while True:
        if question is None:
            try:
                question = input("質問> ")
            except EOFError:
                print()
                return

        if question.strip().lower() in EXIT_COMMANDS:
            return
        if question.strip():
            print(f"[質問] {question}\n")
            print(ask(question, chat))
        question = None


def main() -> None:
    parser = argparse.ArgumentParser(description="会話履歴を保ってLLMに質問する")
    parser.add_argument("question", nargs="?")
    parser.add_argument(
        "-i", "--interactive", action="store_true", help=argparse.SUPPRESS
    )
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    try:
        client = genai.Client(api_key=get_api_key())
        chat = client.chats.create(model=MODEL)
        run_interactive(chat, args.question)
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
