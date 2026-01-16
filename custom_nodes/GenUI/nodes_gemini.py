import os
from .llm_client import LLMClient

class Gemini:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"multiline": False, "default": ""}),
                "model_name": (["gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-2.5-flash", "gemini-2.5-pro"], {"default": "gemini-3-flash-preview"}),
                "system_instruction": ("STRING", {"multiline": True, "default": "You are a helpful assistant."}),
                "user_prompt": ("STRING", {"multiline": True, "default": "Answer my question."}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "max_tokens": ("INT", {"default": 8192, "min": 1, "max": 8192}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response",)
    FUNCTION = "generate"
    CATEGORY = "GenUI/LLM"
    DESCRIPTION = "Gemini 모델을 호출하여 텍스트에 대한 응답을 생성합니다."

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # LLM은 매번 새로운 결과를 생성해야 하므로 항상 변경된 것으로 처리
        return float("NaN")

    def generate(self, api_key, model_name, system_instruction, user_prompt, temperature, max_tokens):
        # API 키 확인 (환경변수 fallback)
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("[Gemini] Error: API Key is missing.")
            return ("Error: API Key is missing.",)

        print(f"[Gemini] Generating response with model: {model_name}")

        # 클라이언트 호출 (이미지 없이 텍스트만)
        response = LLMClient.get_gemini_response(
            api_key, model_name, system_instruction, user_prompt, temperature, max_tokens, files=None
        )
        return (response,)
