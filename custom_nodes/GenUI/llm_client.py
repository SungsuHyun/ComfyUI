import os
import google.generativeai as genai
from openai import OpenAI
import mimetypes
import time

class LLMClient:
    def __init__(self):
        pass

    @staticmethod
    def get_gemini_response(api_key, model_name, system_instruction, user_prompt, temperature, max_tokens, files=None):
        try:
            genai.configure(api_key=api_key)
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                system_instruction=system_instruction if system_instruction else None
            )

            contents = []
            uploaded_files = []
            
            if files:
                for file_path in files:
                    if os.path.exists(file_path):
                        mime_type, _ = mimetypes.guess_type(file_path)
                        if not mime_type:
                            mime_type = "image/png" # Default fallback for temp images
                        
                        # Gemini File API 업로드
                        uploaded_file = genai.upload_file(file_path, mime_type=mime_type)
                        
                        # 처리 대기 (ACTIVE 상태 확인)
                        while uploaded_file.state.name == "PROCESSING":
                            time.sleep(1)
                            uploaded_file = genai.get_file(uploaded_file.name)
                            
                        uploaded_files.append(uploaded_file)
                        contents.append(uploaded_file)

            contents.append(user_prompt)

            response = model.generate_content(contents)
            
            # 업로드한 임시 파일 정리 (선택 사항: Gemini 파일 스토리지는 한도 있음)
            # for f in uploaded_files:
            #     genai.delete_file(f.name)
                
            return response.text
        except Exception as e:
            return f"Gemini Error: {str(e)}"

    @staticmethod
    def get_gpt_response(api_key, model_name, system_instruction, user_prompt, temperature, max_tokens, files=None):
        try:
            client = OpenAI(api_key=api_key)
            
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            
            user_content = [{"type": "text", "text": user_prompt}]
            
            if files:
                import base64
                for file_path in files:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as image_file:
                            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                            
                            mime_type, _ = mimetypes.guess_type(file_path)
                            if not mime_type: mime_type = "image/png"

                            user_content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            })

            messages.append({"role": "user", "content": user_content})

            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"GPT Error: {str(e)}"
