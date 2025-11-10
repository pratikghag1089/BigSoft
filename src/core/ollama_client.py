"""Ollama LLM client for interacting with local models."""

import json
import logging
from typing import Optional, Dict, Any, List
import requests
from .config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama LLM."""

    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        self.host = host or settings.ollama_host
        self.model = model or settings.ollama_model
        self.base_url = f"{self.host}/api"

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to set context
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Response dictionary with 'response' key
        """
        url = f"{self.base_url}/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()

            if stream:
                return self._handle_stream(response)
            else:
                result = response.json()
                return {
                    "response": result.get("response", ""),
                    "model": result.get("model", self.model),
                    "done": result.get("done", True),
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            return {
                "response": f"Error: {str(e)}",
                "error": True,
            }

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Chat completion with conversation history.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response dictionary
        """
        url = f"{self.base_url}/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()

            return {
                "response": result.get("message", {}).get("content", ""),
                "model": result.get("model", self.model),
                "done": result.get("done", True),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama chat API: {e}")
            return {
                "response": f"Error: {str(e)}",
                "error": True,
            }

    def _handle_stream(self, response):
        """Handle streaming response."""
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    if "response" in chunk:
                        full_response += chunk["response"]
                    if chunk.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue

        return {
            "response": full_response,
            "model": self.model,
            "done": True,
        }

    def check_connection(self) -> bool:
        """Check if Ollama is accessible."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error listing models: {e}")
            return []


# Global client instance
ollama_client = OllamaClient()
