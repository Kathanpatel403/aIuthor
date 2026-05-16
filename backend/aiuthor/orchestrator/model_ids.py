"""Default OpenAI chat model ids (no client imports — avoids cycles with observability).

Override via Settings: `openai_chat_model`, `openai_chat_model_mini`.
"""

# Defaults aligned with `aiuthor.config.settings.Settings`
OPENAI_CHAT_MODEL_PRIMARY = "gpt-4o"
OPENAI_CHAT_MODEL_FAST = "gpt-4o-mini"
