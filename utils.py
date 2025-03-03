import re

def structure_message(role, content):
    return {"role": role, "content": content}


def escape_markdown_v2(text):
    """Escapes special characters in MarkdownV2 to prevent parsing issues."""
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)