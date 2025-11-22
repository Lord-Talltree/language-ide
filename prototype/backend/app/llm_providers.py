from abc import ABC, abstractmethod
import subprocess
import json
from typing import Dict, Any, Optional

class LLMProvider(ABC):
    @abstractmethod
    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """Generates JSON output from the LLM based on the prompt."""
        pass

class CodexCLIProvider(LLMProvider):
    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """Uses the local 'codex' CLI command to generate JSON."""
        try:
            # Construct the full prompt to force JSON
            full_prompt = f"{prompt}\nReturn ONLY valid JSON."
            
            # Run the command
            # We use a timeout to prevent hanging
            process = subprocess.Popen(
                ["codex"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=full_prompt, timeout=30)
            
            if process.returncode != 0:
                print(f"Codex Error: {stderr}")
                return {}

            # Attempt to parse JSON from stdout
            # It might contain other text, so we look for the first { and last }
            output = stdout.strip()
            start = output.find('{')
            end = output.rfind('}') + 1
            
            if start != -1 and end != -1:
                json_str = output[start:end]
                return json.loads(json_str)
            else:
                print(f"Could not find JSON in Codex output: {output}")
                return {}
                
        except subprocess.TimeoutExpired:
            process.kill()
            print("Codex command timed out.")
            return {}
        except Exception as e:
            print(f"Error calling Codex: {e}")
            return {}

class MockProvider(LLMProvider):
    def generate_json(self, prompt: str) -> Dict[str, Any]:
        # Return the static mock data
        import os
        mock_path = os.path.join(os.path.dirname(__file__), "../llm_output.json")
        try:
            with open(mock_path, 'r') as f:
                return json.load(f)
        except:
            return {}
