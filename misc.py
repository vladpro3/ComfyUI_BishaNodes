import torch
import comfy.model_management


def load_strings_from_files(file_paths, max_lines):
    all_lines = []

    for file_path in file_paths:
        if len(all_lines) >= max_lines:
            break

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]
                all_lines.extend(lines)
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='cp1251') as file:
                    lines = [line.strip() for line in file.readlines() if line.strip()]
                    all_lines.extend(lines)
            except Exception as e:
                print(f"Не удалось прочитать файл {file_path}: {str(e)}")
        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {str(e)}")

    return all_lines[:max_lines]


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
        maxFileCount = 15
        maxValuesCount = 1000

        inputs = {
            "required": {
                "files_count": ("INT", {"default": 3, "min": 1, "max": maxFileCount, "step": 1}),
                "values_limit": ("INT", {"default": 50, "min": 1, "max": maxValuesCount, "step": 1}),
            },
        }

        for i in range(0, maxFileCount):
            inputs["required"][f"file_{i+1}"] = ("STRING", {"default": "", "multiline": False})
            inputs["required"][f"enabled_{i+1}"] = ("BOOLEAN", {"default": False })

        return inputs


    RETURN_TYPES = ("STRING","STRING","INT",)
    RETURN_NAMES = ("values list","values","count")
    OUTPUT_IS_LIST = (True,False,False)
    FUNCTION = "execute"
    CATEGORY = "BishaNodes"

    def execute(self, files_count, values_limit, **kwargs):
        files = []

        for i in range(files_count):
            text_key = f"file_{i+1}"
            enable_key = f"enabled_{i+1}"

            text_value = kwargs.get(text_key, "")
            is_enabled = kwargs.get(enable_key, False)

            if is_enabled and text_value.strip():
                files.append(text_value)

        lines_list = load_strings_from_files(files, values_limit)
        line_count = len(lines_list)
        lines = ", ".join(lines_list)

        return (lines_list,lines,line_count,)


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
