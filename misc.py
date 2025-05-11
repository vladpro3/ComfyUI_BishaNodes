import random
import torch
import os
import comfy.model_management
import secrets
import time


def generate_seed():
    return time.time_ns() ^ secrets.randbits(64)


def read_file(file_path):
    lines = []

    if file_path != "":
        file_path = os.path.expandvars(file_path)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file at path '{file_path}' does not exist.")
        with open(file_path, 'r') as file:
            file_lines = file.readlines()

        for line in file_lines:
            line = line.replace("\r", "")
            line = line.strip()
            if line != "":
                lines.append(line)

    return lines


def get_file_line(self, lines, next_line, line_count):
    text = ""

    if line_count > 0:
        if next_line == "random":
            self.random.seed(generate_seed())
            self.current_line = self.random.randint(0, line_count - 1)

        self.current_line = self.current_line % line_count
        text = text + lines[self.current_line]

        if next_line == "increment":
            self.current_line = self.current_line + 1
        elif next_line == "decrement":
            self.current_line = self.current_line - 1
            if self.current_line < 0:
                self.current_line = line_count - 1

    text = text.replace("\r", "").replace("\n", " ").replace("<", " <")

    return text


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


class CreatePromptsWithTextFromFile:
    def __init__(self):
        self.current_line = 0
        self.random = random.Random()

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"default": "", "multiline": False}),
                "next_line": (["increment", "decrement", "random", "fixed"], {"default": "fixed"}),
                "start_line": ("INT", {"default": 0, "min": 0, "step": 1}),
                "results": ("INT", {"default": 1, "min": 1, "step": 1}),
            },
            "optional": {
                "prepend_text": ("STRING", {"multiline": True, "default": ""}),
                "append_text": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompts",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "execute"
    CATEGORY = "BishaNodes"

    def execute(self, file_path="", next_line="fixed", start_line=0, results=1, prepend_text="", append_text=""):
        lines = read_file(file_path)
        line_count = len(lines)

        if start_line > line_count:
            self.current_line = line_count
        else:
            self.current_line = start_line

        result = []

        if next_line in ["increment", "decrement"] and results > line_count:
            results = line_count

        for i in range(results):
            text = get_file_line(self, lines, next_line, line_count)

            if prepend_text != "":
                text = prepend_text + ", " + text
            if append_text != "":
                text = text + ", " + append_text

            if i < results - 1:
                result.append(text + "\n")
            else:
                result.append(text)

        return (result,)


MISC_CLASS_MAPPINGS = {
    "SimpleSizePicker": SimpleSizePicker,
    "EmptyLatentSizePicker": EmptyLatentSizePicker,
    "CreatePromptsWithTextFromFile": CreatePromptsWithTextFromFile,
}

MISC_NAME_MAPPINGS = {
    "SimpleSizePicker": "Simple Size Picker",
    "EmptyLatentSizePicker": "Empty Latent Size Picker",
    "CreatePromptsWithTextFromFile": "Create Prompts With Text From File",
}
