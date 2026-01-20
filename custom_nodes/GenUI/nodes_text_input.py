class UserTextInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "dynamicPrompts": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "return_text"
    CATEGORY = "GenUI"
    DESCRIPTION = "사용자로부터 텍스트 입력을 받아 출력하는 간단한 노드입니다."

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def return_text(self, text):
        return (text,)
