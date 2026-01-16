from .ui_render import UIRender
from .nodes_gemini import Gemini
from .nodes_gpt import GPT
from .nodes_text_input import UserTextInput

NODE_CLASS_MAPPINGS = {
    "UIRender": UIRender,
    "Gemini": Gemini,
    "GPT": GPT,
    "UserTextInput": UserTextInput,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UIRender": "UI Render (GenUI)",
    "Gemini": "Gemini (GenUI)",
    "GPT": "GPT (GenUI)",
    "UserTextInput": "User Text Input (GenUI)",
}

WEB_DIRECTORY = "./js"
