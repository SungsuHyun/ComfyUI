import json
import requests
import os
import folder_paths

class BaseTool:
    """
    모든 Tool 노드의 기본 클래스입니다.
    """
    CATEGORY = "GenUI/Agent"
    RETURN_TYPES = ("TOOL",)
    RETURN_NAMES = ("tool",)
    FUNCTION = "create_tool"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def create_tool(self, **kwargs):
        raise NotImplementedError

    def get_tool_definition(self, name, description, func, schema=None):
        if schema is None:
            schema = {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": True 
                    }
                }
            }
            
        tool_def = {
            "name": name,
            "description": description,
            "func": func,
            "schema": schema
        }
        return (tool_def,)

class APITool(BaseTool):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "name": ("STRING", {"multiline": False, "default": "get_weather"}),
                "description": ("STRING", {"multiline": True, "default": "Get current weather for a location. Params: location (str)"}),
                "url": ("STRING", {"multiline": False, "default": "https://api.example.com/weather"}),
                "method": (["GET", "POST", "PUT", "DELETE"], {"default": "GET"}),
                "headers": ("STRING", {"multiline": True, "default": "{}"}),
            }
        }

    DESCRIPTION = "REST API를 호출하는 도구를 생성합니다."

    def create_tool(self, name, description, url, method, headers):
        def api_wrapper(**kwargs):
            try:
                header_dict = json.loads(headers) if headers else {}
                if method == "GET":
                    response = requests.request(method, url, headers=header_dict, params=kwargs)
                else:
                    response = requests.request(method, url, headers=header_dict, json=kwargs)
                return response.text
            except Exception as e:
                return f"Error executing tool {name}: {str(e)}"

        return self.get_tool_definition(name, description, api_wrapper)

class ReadTextFileTool(BaseTool):
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        extensions = ['.txt', '.json', '.csv', '.log', '.md']
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and any(f.endswith(ext) for ext in extensions)]
        return {
            "required": {
                "file": (sorted(files), {"file_upload": True}),
            }
        }

    DESCRIPTION = "선택한 텍스트 파일을 읽어오는 도구를 생성합니다."

    def create_tool(self, file):
        file_path = os.path.join(folder_paths.get_input_directory(), file)
        
        # 이름과 설명을 고정하여 사용자가 입력할 필요 없게 함
        name = "read_text_file"
        description = f"Reads the content of the selected file: {file}"
        
        def read_file_wrapper(**kwargs):
            try:
                if not os.path.exists(file_path):
                    return f"Error: File not found at {file_path}"
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content
            except Exception as e:
                return f"Error reading file: {str(e)}"

        return self.get_tool_definition(name, description, read_file_wrapper)

class ToolCollection:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "tool_1": ("TOOL",),
                "tool_2": ("TOOL",),
                "tool_3": ("TOOL",),
                "tool_4": ("TOOL",),
                "tool_5": ("TOOL",),
            }
        }

    RETURN_TYPES = ("TOOL",)
    RETURN_NAMES = ("tool_collection",)
    FUNCTION = "collect_tools"
    CATEGORY = "GenUI/Agent"
    DESCRIPTION = "여러 개의 도구를 하나로 묶어 Agent에 전달합니다."

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def collect_tools(self, **kwargs):
        final_collection = []
        for k, v in kwargs.items():
            if v:
                if isinstance(v, list):
                    final_collection.extend(v)
                else:
                    final_collection.append(v)
        return (final_collection,)
