import os
import google.generativeai as genai
from openai import OpenAI
import mimetypes
import time
import json

class LLMClient:
    def __init__(self):
        pass

    @staticmethod
    def get_gemini_response(api_key, model_name, system_instruction, messages, tools=None, temperature=0.7, max_tokens=8192):
        # Gemini는 현재 복잡한 Tool Loop를 이 Client 내에서 처리하기보다,
        # Agent Node에서 호출할 수 있도록 기본 생성 기능에 집중합니다.
        # 참고: Gemini API의 Tool 사용은 설정이 다르므로 여기서는 텍스트 생성 위주로 처리하되
        # 추후 확장을 위해 인터페이스를 맞춰둡니다.
        try:
            genai.configure(api_key=api_key)
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            # Gemini Tools 변환 (간략화)
            gemini_tools = None
            if tools:
                # Gemini용 tool 변환 로직이 필요하나, 복잡성을 줄이기 위해 
                # 현재는 System Prompt에 도구 설명을 추가하는 방식으로 우회하거나
                # 추후 전용 변환 로직 구현 권장.
                pass

            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                system_instruction=system_instruction if system_instruction else None,
                tools=gemini_tools
            )

            # Messages 변환 (OpenAI format -> Gemini format)
            gemini_contents = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                parts = []
                if isinstance(msg["content"], list):
                    for part in msg["content"]:
                        if part["type"] == "text":
                            parts.append(part["text"])
                        elif part["type"] == "image_url":
                            # 이미지 처리 로직 (파일 경로가 있다고 가정)
                            pass 
                else:
                    parts.append(msg["content"])
                
                gemini_contents.append({"role": role, "parts": parts})

            response = model.generate_content(gemini_contents)
            
            # OpenAI 호환 응답 객체 생성
            class ResponseWrapper:
                def __init__(self, content, role="assistant", tool_calls=None):
                    self.content = content
                    self.role = role
                    self.tool_calls = tool_calls

            return ResponseWrapper(response.text)
        except Exception as e:
            print(f"Gemini Error: {str(e)}")
            return None

    @staticmethod
    def get_gpt_response(api_key, model_name, system_instruction, messages, tools=None, temperature=0.7, max_tokens=8192):
        try:
            client = OpenAI(api_key=api_key)
            
            full_messages = []
            if system_instruction:
                full_messages.append({"role": "system", "content": system_instruction})
            
            # 이전 대화 기록 추가
            full_messages.extend(messages)

            # Tools 포맷팅
            api_tools = []
            if tools:
                for t in tools:
                    if "schema" in t:
                        api_tools.append(t["schema"])
            
            params = {
                "model": model_name,
                "messages": full_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            if api_tools:
                params["tools"] = api_tools
                params["tool_choice"] = "auto"

            response = client.chat.completions.create(**params)
            return response.choices[0].message
        except Exception as e:
            # 에러 발생 시 문자열로 반환하지 않고 예외를 던지거나 에러 객체 반환
            # Agent 로직 처리를 위해 Message 객체 구조를 흉내낸 dict 반환
            print(f"GPT Error: {str(e)}")
            return None
