import os
from .llm_client import LLMClient

class GPT:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"multiline": False, "default": ""}),
                "model_name": (["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"], {"default": "gpt-4o"}),
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
    DESCRIPTION = "OpenAI GPT 모델을 호출하여 텍스트에 대한 응답을 생성합니다."

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # LLM은 매번 새로운 결과를 생성해야 하므로 항상 변경된 것으로 처리
        return float("NaN")

    def generate(self, api_key, model_name, system_instruction, user_prompt, temperature, max_tokens):
        # API 키 확인 (환경변수 fallback)
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("[GPT] Error: API Key is missing.")
            return ("Error: API Key is missing.",)

        print(f"[GPT] Generating response with model: {model_name}")

        # 단일 user_prompt를 messages 리스트 포맷으로 변환
        messages = [{"role": "user", "content": user_prompt}]

        response_msg = LLMClient.get_gpt_response(
            api_key=api_key,
            model_name=model_name,
            system_instruction=system_instruction,
            messages=messages,
            tools=None,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # get_gpt_response는 이제 Message 객체를 반환하므로 content만 추출
        response_text = response_msg.content if response_msg else "Error: Failed to get response."
        print(f"[GPT] Response: {response_text}")
        return (response_text,)
