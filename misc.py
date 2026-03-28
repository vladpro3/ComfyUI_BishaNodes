import os
import torch
import comfy.model_management


class _AnyType(str):
    """Always equal in != comparisons — allows ComfyUI to accept any input type."""
    def __ne__(self, other): return False

_any_type = _AnyType("*")


class _FlexibleOptionalInputType(dict):
    """Makes INPUT_TYPES accept dynamic unknown keys (e.g. file_1, file_2, ...)."""
    def __init__(self, type):
        self.type = type
    def __getitem__(self, key):
        return (self.type,)
    def __contains__(self, key):
        return True


def load_strings_from_files(file_paths):
    all_lines = []

    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"[BishaNodes] Файл не найден: {file_path}")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                all_lines.extend(line.strip() for line in f if line.strip())
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='cp1251') as f:
                    all_lines.extend(line.strip() for line in f if line.strip())
            except Exception as e:
                print(f"[BishaNodes] Не удалось прочитать файл {file_path}: {e}")
        except Exception as e:
            print(f"[BishaNodes] Ошибка при обработке файла {file_path}: {e}")

    return all_lines


square_resolutions = [
    "512 x 512 (1:1)",
    "768 x 768 (1:1)",
    "1024 x 1024 (1:1)",
    "1536 x 1536 (1:1)",
    "2048 x 2048 (1:1)"
]
portrait_resolutions = [
    "512 x 768 (2:3)",
    "768 x 1152 (2:3)",
    "1024 x 1536 (2:3)",
    "1152 x 1728 (2:3)",
    "832 x 1216 (≈3:4)",
    "1024 x 1360 (≈3:4)",
    "1080 x 1920 (9:16)"
]
landscape_resolutions = [
    "768 x 512 (3:2)",
    "1152 x 768 (3:2)",
    "1536 x 1024 (3:2)",
    "1216 x 832 (≈4:3)",
    "1360 x 1024 (≈4:3)",
    "1920 x 1080 (16:9)",
    "2048 x 1152 (16:9)",
    "2560 x 1440 (16:9)",
    "3840 x 2160 (16:9)"
]
widescreen_resolutions = [
    "1344 x 768 (16:9)",
    "1792 x 1024 (16:9)",
    "2048 x 1080 (≈17:9, DCI 2K)"
]
ultrawide_resolutions = [
    "2560 x 1080 (64:27 ≈ 21:9)",
    "3440 x 1440 (43:18 ≈ 21.5:9)",
    "3840 x 1600 (12:5 = 21.6:9)",
    "5120 x 2160 (64:27 ≈ 21:9, 5K UW)"
]
super_ultrawide_resolutions = [
    "3840 x 1080 (32:9, Dual Full HD)",
    "5120 x 1440 (32:9, Dual QHD)",
    "7680 x 2160 (32:9, 8K Ultra Wide)"
]
panoramic_resolutions = [
    "5760 x 1080 (48:9 = 16:3, Triple Full HD)",
    "7680 x 1440 (48:9 = 16:3, Triple QHD)",
    "9600 x 1200 (8:1, Custom Ultra Panoramic)"
]
resolutions = (
        square_resolutions +
        portrait_resolutions +
        landscape_resolutions +
        widescreen_resolutions +
        ultrawide_resolutions +
        super_ultrawide_resolutions +
        panoramic_resolutions
)


class SimpleSizePicker:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "resolution": (resolutions, {"default": square_resolutions[0]}),
            }
        }

    RETURN_TYPES = ("INT", "INT",)
    RETURN_NAMES = ("width", "height",)
    FUNCTION = "execute"
    CATEGORY = "BishaNodes"

    def execute(self, resolution):
        width, height = map(int, resolution.split(" (")[0].split(" x "))

        return (width, height,)


class EmptyLatentSizePicker:
    def __init__(self):
        self.device = comfy.model_management.intermediate_device()

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "resolution": (resolutions, {"default": "1024x1024 (1.0)"}),
            "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096}),
        }}

    RETURN_TYPES = ("LATENT", "INT", "INT",)
    RETURN_NAMES = ("LATENT", "width", "height",)
    FUNCTION = "execute"
    CATEGORY = "BishaNodes"

    def execute(self, resolution, batch_size):
        width, height = map(int, resolution.split(" (")[0].split(" x "))

        latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)

        return ({"samples": latent}, width, height,)


class LoadDataFromFiles:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": _FlexibleOptionalInputType(_any_type),
        }

    RETURN_TYPES = ("STRING", "STRING", "INT",)
    RETURN_NAMES = ("values list", "values", "count")
    OUTPUT_IS_LIST = (True, False, False)
    FUNCTION = "execute"
    CATEGORY = "BishaNodes"

    def execute(self, **kwargs):
        # Collect all active file paths from dynamic widgets: {"on": bool, "file": str}
        files = [
            v["file"]
            for k, v in kwargs.items()
            if k.startswith("file_") and isinstance(v, dict)
            and v.get("on") and v.get("file", "").strip()
        ]

        lines_list = load_strings_from_files(files)
        line_count = len(lines_list)
        lines = ", ".join(lines_list)

        return (lines_list, lines, line_count,)


MISC_CLASS_MAPPINGS = {
    "SimpleSizePicker": SimpleSizePicker,
    "EmptyLatentSizePicker": EmptyLatentSizePicker,
    "LoadDataFromFiles": LoadDataFromFiles,
}

MISC_NAME_MAPPINGS = {
    "SimpleSizePicker": "Simple Size Picker",
    "EmptyLatentSizePicker": "Empty Latent Size Picker",
    "LoadDataFromFiles": "Load Data From Files",
}
