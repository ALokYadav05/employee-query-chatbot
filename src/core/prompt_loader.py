import os
from src.core import config

class PromptLoader:
    """
    Utility class to load system prompts from Markdown file.
    """
    def __init__(self):
        self.file_path = f"{config.BASE_DIR}/src/prompts/system_prompt.md"

    def load_prompt(self) -> str:
        """
        Loads system prompt from Markdown file.
        Return: system prompt as string
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Prompt file not found : {self.file_path}")

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                prompt = file.read()
                return prompt
        except Exception as e:
            print(f"Error while loading system prompt : {e}")

prompt_loader = PromptLoader()
