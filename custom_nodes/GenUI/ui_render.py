import os
import urllib.parse
import folder_paths
import time
import random

class UIRender:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "code": ("STRING", {"multiline": True, "default": "<style>.ui-card { padding: 16px; background:#111; color:#fff; }</style><div class='ui-card'>Hello ComfyUI</div>"}),
                "filename_prefix": ("STRING", {"default": "ComfyUI_UI"}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_ui"
    OUTPUT_NODE = True
    CATEGORY = "GenUI"
    DESCRIPTION = "HTML/CSS UI 코드를 저장하고 /view 미리보기 링크를 제공합니다."

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # 항상 재실행되도록 현재 시간 + 난수 반환
        return float("NaN")

    @staticmethod
    def _wrap_html(code: str) -> str:
        # code 안에 html, css가 모두 포함되어 있다고 가정
        # 단순 래핑만 수행
        lower_code = code.lower()
        if "<html" not in lower_code:
            return (
                "<!DOCTYPE html>"
                "<html><head><meta charset=\"utf-8\">"
                "</head><body>"
                f"{code}"
                "</body></html>"
            )
        return code

    def save_ui(self, code, filename_prefix="ComfyUI_UI", prompt=None, extra_pnginfo=None):
        base_output = folder_paths.get_output_directory()
        ui_root = os.path.join(base_output, "ui_previews")
        os.makedirs(ui_root, exist_ok=True)

        safe_prefix = filename_prefix.strip() or "ComfyUI_UI"
        clean_prefix = safe_prefix.replace("\\", "/")
        if ".." in clean_prefix.split("/"):
            raise Exception("Invalid filename_prefix")

        full_output_folder, filename, counter, subfolder, _ = folder_paths.get_save_image_path(clean_prefix, ui_root, 1, 1)
        filename_with_batch = filename.replace("%batch_num%", "0")
        html_filename = f"{filename_with_batch}_{counter:05}_.html"
        html_path = os.path.join(full_output_folder, html_filename)

        html_content = self._wrap_html(code)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        relative_folder = os.path.relpath(full_output_folder, base_output)
        preview_params = {
            "filename": html_filename,
            "subfolder": relative_folder,
            "type": "output",
            "allow_html": "1",
            "t": str(time.time()) # URL 캐시 방지용 파라미터 추가
        }
        preview_query = "&".join(f"{k}={urllib.parse.quote(v)}" for k, v in preview_params.items() if v)
        preview_url = f"/view?{preview_query}"
        
        rel_path = os.path.relpath(html_path, base_output)
        info_text = f"Saved UI HTML: {rel_path}\nPreview: {preview_url}"

        return {
            "ui": {
                "text": (info_text,),
                # 프런트 확장용 key 변경: save_ui_preview -> ui_render_url
                "ui_render_url": (preview_url,),
            }
        }
