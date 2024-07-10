import pytest
from unittest.mock import AsyncMock

import pytest_asyncio

from app.ai import OpenAIModel, AnthropicModel, categorize_ticket, prioritize_ticket, generate_response


@pytest_asyncio.fixture(params=[OpenAIModel(), AnthropicModel()])
async def ai_model(request):
    return request.param


@pytest.mark.asyncio
async def test_categorize_ticket(ai_model):
    ai_model.get_completion = AsyncMock(return_value='{"category": "Technical Problem", "confidence": 0.95}')
    category, confidence = await categorize_ticket(ai_model, "Subject", "Body")
    assert category.value == "technical_problem"
    assert confidence == 0.95


@pytest.mark.asyncio
async def test_prioritize_ticket(ai_model):
    ai_model.get_completion = AsyncMock(return_value='{"priority": "High", "confidence": 0.90}')
    priority, confidence = await prioritize_ticket(ai_model, "Subject", "Body")
    assert priority.value == "high"
    assert confidence == 0.90


@pytest.mark.asyncio
async def test_generate_response(ai_model):
    ai_model.get_completion = AsyncMock(return_value="This is a response.")
    response = await generate_response(ai_model, "Subject", "Body")
    assert response == "This is a response."
