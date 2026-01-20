import json
import os
from .llm_client import LLMClient

class OrchestratorAgentNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"multiline": False, "default": ""}),
                "model_name": (["gemini-3-flash-preview", "gemini-3-pro-preview", "gemini-2.5-flash", "gemini-2.5-pro"], {"default": "gemini-3-flash-preview"}),
                "system_instruction": ("STRING", {"multiline": True, "default": "You are a helpful assistant. Use the provided tools to fulfill the user's implicit request or process the provided data. Summarize the findings clearly."}),
                "user_prompt": ("STRING", {"multiline": True, "default": "Check the weather in Seoul."}),
            },
            "optional": {
                "tool": ("TOOL",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output",)
    FUNCTION = "execute_plan"
    CATEGORY = "GenUI/Agent"
    DESCRIPTION = "연결된 도구를 사용하여 작업을 수행하고 결과를 출력합니다."
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # 항상 재실행되도록 NaN 반환
        return float("NaN")

    def execute_plan(self, api_key, model_name, system_instruction, user_prompt, tool=None):
        # input 필드가 있으므로 이를 목표로 사용
        goal = user_prompt if user_prompt else "Please execute the available tools and provide a comprehensive report on the data or actions performed."

        # Load samsung_google_app_analysis.txt and append to system_instruction
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, "samsung_google_app_analysis.txt")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                system_instruction += f"\n\n=== Reference Data (Samsung & Google App Analysis) ===\n{file_content}\n======================================================\n"
                print(f"[Agent] Successfully loaded reference data from {file_path}")
            else:
                print(f"[Agent] Warning: Reference file not found at {file_path}")
        except Exception as e:
            print(f"[Agent] Error loading reference file: {str(e)}")

        if not api_key:
            if "gemini" in model_name.lower():
                api_key = os.environ.get("GEMINI_API_KEY")
            else:
                api_key = os.environ.get("OPENAI_API_KEY")
                
        if not api_key:
            return ("Error: API Key is missing.",)

        available_tools = []
        if tool:
            if isinstance(tool, list):
                available_tools.extend(tool)
            else:
                available_tools.append(tool)
        
        unique_tools = {}
        for t in available_tools:
            if t and isinstance(t, dict) and "name" in t:
                unique_tools[t["name"]] = t
        available_tools = list(unique_tools.values())
        tool_map = {t["name"]: t["func"] for t in available_tools}
        
        # 사용자 입력 목표로 시작
        messages = [{"role": "user", "content": goal}]
        current_turn = 0
        max_turns = 10
        final_response = ""

        print(f"[Agent] Starting orchestration with available tools: {list(tool_map.keys())}")

        while current_turn < max_turns:
            current_turn += 1
            
            if "gemini" in model_name.lower():
                response_msg = LLMClient.get_gemini_response(
                    api_key, model_name, system_instruction, messages, available_tools
                )
            else:
                response_msg = LLMClient.get_gpt_response(
                    api_key, model_name, system_instruction, messages, available_tools
                )

            if not response_msg:
                final_response = "Error during LLM call."
                break

            response_dict = {"role": response_msg.role, "content": response_msg.content}
            
            if response_msg.tool_calls:
                messages.append(response_msg)
                for tool_call in response_msg.tool_calls:
                    func_name = tool_call.function.name
                    func_args_str = tool_call.function.arguments
                    call_id = tool_call.id
                    
                    if func_name in tool_map:
                        try:
                            func_args = json.loads(func_args_str)
                            tool_result = tool_map[func_name](**func_args)
                        except Exception as e:
                            tool_result = f"Error executing {func_name}: {str(e)}"
                    else:
                        tool_result = f"Error: Tool {func_name} not found."

                    messages.append({
                        "role": "tool",
                        "tool_call_id": call_id,
                        "name": func_name,
                        "content": str(tool_result)
                    })
                continue
            else:
                final_response = response_msg.content
                break

        return (final_response,)
