import sys
from typing import Any
from types import SimpleNamespace

from app import ask


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(
        text="回答",
        usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=8),
    )

    class FakeModels:
        def generate_content(self, *, model, contents):
            return response

    class FakeClient:
        def __init__(self, *, api_key):
            self.models = FakeModels()

    monkeypatch.setattr(ask.genai, "Client", FakeClient)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")

    assert ask.ask("質問") == "回答"
    assert capsys.readouterr().out == "[tokens] input=12 output=8\n"


def test_ask_reuses_chat_session_for_follow_up_questions(capsys):
    class FakeChat:
        def __init__(self):
            self.questions: list[str] = []

        def send_message(self, message: str) -> Any:
            self.questions.append(message)
            return SimpleNamespace(
                text=f"{message}への回答",
                usage_metadata=SimpleNamespace(
                    prompt_token_count=12, candidates_token_count=8
                ),
            )

    chat = FakeChat()

    assert ask.ask("最初の質問", chat) == "最初の質問への回答"
    assert ask.ask("続きの質問", chat) == "続きの質問への回答"
    assert chat.questions == ["最初の質問", "続きの質問"]
    assert capsys.readouterr().out.count("[tokens] input=12 output=8") == 2


def test_ask_reports_when_token_usage_is_missing(capsys):
    class FakeChat:
        def send_message(self, message: str) -> Any:
            return SimpleNamespace(text="回答", usage_metadata=None)

    assert ask.ask("質問", FakeChat()) == "回答"
    assert capsys.readouterr().out == "[tokens] トークン使用量はAPI応答に含まれていません\n"


def test_run_interactive_sends_each_question_to_same_chat(monkeypatch, capsys):
    questions = iter(["最初の質問", "続きの質問", "終了"])
    monkeypatch.setattr("builtins.input", lambda _: next(questions))

    class FakeChat:
        def __init__(self):
            self.questions: list[str] = []

        def send_message(self, message: str) -> Any:
            self.questions.append(message)
            return SimpleNamespace(text=f"{message}への回答", usage_metadata=None)

    chat = FakeChat()
    ask.run_interactive(chat)

    assert chat.questions == ["最初の質問", "続きの質問"]
    assert "続きの質問への回答" in capsys.readouterr().out


def test_main_starts_interactive_chat_without_flag(monkeypatch):
    chat = object()
    created = []
    started = []

    class FakeChats:
        def create(self, *, model):
            created.append(model)
            return chat

    class FakeClient:
        def __init__(self, *, api_key):
            self.chats = FakeChats()

    monkeypatch.setattr(sys, "argv", ["app.ask"])
    monkeypatch.setattr(ask.genai, "Client", FakeClient)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(
        ask, "run_interactive", lambda session, first_question=None: started.append(
            (session, first_question)
        )
    )

    ask.main()

    assert created == [ask.MODEL]
    assert started == [(chat, None)]