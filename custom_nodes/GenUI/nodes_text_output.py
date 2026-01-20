class TextOutput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True, "multiline": True}),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "display_text"
    CATEGORY = "GenUI"
    DESCRIPTION = "입력받은 텍스트를 보여주는 읽기 전용 노드입니다."
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def display_text(self, text):
        return {"ui": {"text": [text]}}

