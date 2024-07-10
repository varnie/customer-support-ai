import json
from abc import ABC, abstractmethod

import anthropic
import openai
from openai import AsyncOpenAI

from app.config import Config
from app.decorators import log
from app.schemas import TicketCategory, TicketPriority


class AIModel(ABC):
    @abstractmethod
    async def get_completion(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        pass


class OpenAIModel(AIModel):
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.api_key = Config.OPENAI_API_KEY
        self.client = AsyncOpenAI()

        if not self.api_key:
            raise ValueError("OpenAI API key is missing")
        openai.api_key = self.api_key
        self.model = model

    @log
    async def get_completion(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens
        )
        return completion.choices[0].message.content


class AnthropicModel(AIModel):
    def __init__(self, model: str = "claude-3-5-sonnet-20240620"):
        self.api_key = Config.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("Anthropic API key is missing")
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        self.model = model

    @log
    async def get_completion(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        messages = [
            {"role": "user", "content": user_prompt}
        ]
        response = await self.client.messages.create(
            model=self.model,
            messages=messages,
            system=system_prompt,
            max_tokens=max_tokens
        )
        return response.content[0].text


openai_model = OpenAIModel()
anthropic_model = AnthropicModel()


async def categorize_ticket(model: AIModel, subject: str, body: str) -> (TicketCategory, float):
    """
    Use the provided AI model to categorize the support ticket based on its content.
    """
    system_prompt = "You are an assistant that categorizes support tickets into predefined categories and returns a JSON object with the category and a confidence score."
    user_prompt = f"Subject: {subject}\n\nBody: {body}\n\nCategories: [Account Access, Payment Issue, Feature Request, Technical Problem, Other]\n\nRespond with a JSON object like this: {{'category': 'Category Name', 'confidence': 0.95}}"

    response = await model.get_completion(system_prompt, user_prompt, max_tokens=50)

    # Parse the JSON response
    try:
        response_json = json.loads(response)
        category = response_json.get('category')
        category_confidence = response_json.get('confidence')
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format received: {response}")

    # Validate category
    try:
        category_enum = TicketCategory[category.replace(" ", "_").lower()]
    except KeyError:
        raise ValueError(f"Invalid category received: {category}")

    return category_enum, category_confidence


async def prioritize_ticket(model: AIModel, subject: str, body: str) -> (TicketPriority, float):
    """
    Use the provided AI model to prioritize the support ticket based on its content.
    """
    system_prompt = "You are an assistant that prioritizes support tickets based on urgency and returns a JSON object with the priority and a confidence score."
    user_prompt = f"Subject: {subject}\n\nBody: {body}\n\nPriorities: [Low, Medium, High, Critical]\n\nRespond with a JSON object like this: {{'priority': 'Priority Level', 'confidence': 0.90}}"

    response = await model.get_completion(system_prompt, user_prompt, max_tokens=50)

    # Parse the JSON response
    try:
        response_json = json.loads(response)
        priority = response_json.get('priority')
        priority_confidence = response_json.get('confidence')
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format received: {response}")

    # Validate priority
    try:
        priority_enum = TicketPriority[priority.lower()]
    except KeyError:
        raise ValueError(f"Invalid priority received: {priority}")

    return priority_enum, priority_confidence


async def generate_response(model: AIModel, subject: str, body: str) -> str:
    """
    Use the provided AI model to generate an initial response for the support ticket based on its content.
    """
    system_prompt = (
        "You are an assistant that generates initial responses for support tickets. "
        "Respond in a professional, courteous, and empathetic manner. "
        "Ensure the response addresses the customer's concerns directly and provides clear steps or information. "
        "If additional information or action is needed from the customer, clearly state what is required. "
        "The response should be formatted in plain text, without JSON or code blocks."
    )
    user_prompt = f"Subject: {subject}\n\nBody: {body}\n\nGenerate an initial response to the provided ticket."

    response = await model.get_completion(system_prompt, user_prompt, max_tokens=4096)

    return response
