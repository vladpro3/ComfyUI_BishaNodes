import random
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


def get_line(self, lines, next_line, line_count, start_line = 0):
    text = ""

    if line_count > 0:
        if next_line == "random":
            self.random.seed(generate_seed())
            self.current_line = self.random.randint(start_line, line_count - 1)

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


def replace_wildcard(prompt, wildcard, replacements, value_separator):
    if wildcard and wildcard in prompt:
        if isinstance(replacements, list):
            replacement_str = value_separator.join(replacements)
        else:
            replacement_str = str(replacements)

        output_text = prompt.replace(wildcard, replacement_str)
        return output_text
    else:
        return prompt


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
    CATEGORY = "BishaNodes/prompt"

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
            text = get_line(self, lines, next_line, line_count, start_line)

            if prepend_text != "":
                text = prepend_text + ", " + text
            if append_text != "":
                text = text + ", " + append_text

            result.append(text)

        return (result,)


class WildcardReplace:
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
                "prompts": ("STRING", {"forceInput": True}),
                "values": ("STRING", {"forceInput": True}),
                "wildcard": ("STRING", {"multiline": False, "default": ""}),
                "next_line": (["increment", "decrement", "random", "fixed"], {"default": "fixed"}),
                "start_line": ("INT", {"default": 0, "min": 0, "step": 1}),
                "values_count": ("INT", {"default": 1, "min": 1, "step": 1}),
                "value_separator": ("STRING", {"multiline": False, "default": ","}),
            },
            "optional": {
                "prepend_text": ("STRING", {"multiline": True, "default": ""}),
                "append_text": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompts",)
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "execute"
    CATEGORY = "BishaNodes/prompt"

    def execute(self, prompts, values, wildcard, next_line, start_line, values_count, value_separator, prepend_text, append_text):
        line_count = len(values)
        next_line = next_line[0]
        start_line = start_line[0]
        values_count = values_count[0]
        prepend_text = prepend_text[0]
        append_text = append_text[0]

        if start_line > line_count:
            self.current_line = line_count
        else:
            self.current_line = start_line

        result_values = []
        result_prompt = []

        if next_line in ["increment", "decrement"] and values_count > line_count:
            values_count = line_count

        for i in range(values_count):
            result_values.append(get_line(self, values, next_line, line_count, start_line))

        for prompt in prompts:
            replaced_text = replace_wildcard(prompt, wildcard[0], result_values, value_separator[0])

            if prepend_text != "":
                replaced_text = prepend_text + value_separator + replaced_text
            if append_text != "":
                replaced_text = replaced_text + value_separator + append_text

            result_prompt.append(replaced_text)

        return (result_prompt,)


class WildcardReplaceFromFile:
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
                "prompt": ("STRING", {"forceInput": True}),
                "wildcard": ("STRING", {"multiline": False, "default": ""}),
                "file_path": ("STRING", {"multiline": False, "default": ""}),
                "next_line": (["increment", "decrement", "random", "fixed"], {"default": "fixed"}),
                "start_line": ("INT", {"default": 0, "min": 0, "step": 1}),
                "values_count": ("INT", {"default": 1, "min": 1, "step": 1}),
                "value_separator": ("STRING", {"multiline": False, "default": ","}),
            },
            "optional": {
                "prepend_text": ("STRING", {"multiline": True, "default": ""}),
                "append_text": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompts",)
    OUTPUT_IS_LIST = (False,)
    FUNCTION = "execute"
    CATEGORY = "BishaNodes/prompt"

    def execute(self, prompt, wildcard, file_path, next_line, start_line, values_count, value_separator, prepend_text, append_text):
        lines = read_file(file_path)
        line_count = len(lines)

        if start_line > line_count:
            self.current_line = line_count
        else:
            self.current_line = start_line

        result_values = []

        if next_line in ["increment", "decrement"] and values_count > line_count:
            values_count = line_count

        for i in range(values_count):
            result_values.append(get_line(self, lines, next_line, line_count, start_line))

        replaced_text = replace_wildcard(prompt, wildcard, result_values, value_separator)

        if prepend_text != "":
            replaced_text = prepend_text + value_separator + replaced_text
        if append_text != "":
            replaced_text = replaced_text + value_separator + append_text

        return (replaced_text,)


PROMPTS_CLASS_MAPPINGS = {
    "CreatePromptsWithTextFromFile": CreatePromptsWithTextFromFile,
    "WildcardReplaceFromFile": WildcardReplaceFromFile,
    "WildcardReplace": WildcardReplace,
}

PROMPTS_NAME_MAPPINGS = {
    "CreatePromptsWithTextFromFile": "Create Prompts With Text From File",
    "WildcardReplaceFromFile": "Wildcard Replace (with values from File)",
    "WildcardReplace": "Wildcard Replace",
}
