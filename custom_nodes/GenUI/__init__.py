from .ui_render import UIRender
from .nodes_gemini import Gemini
from .nodes_gpt import GPT
from .nodes_text_input import UserTextInput
from .nodes_text_output import TextOutput
from .nodes_agent import OrchestratorAgentNode
from .nodes_tools import APITool, ToolCollection, ReadTextFileTool

NODE_CLASS_MAPPINGS = {
    "UIRender": UIRender,
    "Gemini": Gemini,
    "GPT": GPT,
    "UserTextInput": UserTextInput,
    "TextOutput": TextOutput,
    "OrchestratorAgentNode": OrchestratorAgentNode,
    "APITool": APITool,
    "ToolCollection": ToolCollection,
    "ReadTextFileTool": ReadTextFileTool,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UIRender": "UI Render (GenUI)",
    "Gemini": "Gemini (GenUI)",
    "GPT": "GPT (GenUI)",
    "UserTextInput": "User Text Input (GenUI)",
    "TextOutput": "Text Output (GenUI)",
    "OrchestratorAgentNode": "Orchestrator Agent (GenUI)",
    "APITool": "API Tool (GenUI)",
    "ToolCollection": "Tool Collection (GenUI)",
    "ReadTextFileTool": "Read Text File Tool (GenUI)",
}

WEB_DIRECTORY = "./js"
