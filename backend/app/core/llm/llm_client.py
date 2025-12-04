"""
LLM Client - Real integration with OpenAI and Anthropic.
Replaces placeholder implementations with actual LLM calls.
"""

import logging
import os
from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.core.config import settings
from app.core.utils.rate_limiter import get_rate_limiter
from app.core.utils.caching import cached_async
from app.core.utils.monitoring import get_performance_monitor

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMClient:
    """
    Unified LLM client supporting multiple providers.
    
    Features:
    - OpenAI (GPT-4, GPT-3.5-turbo)
    - Anthropic (Claude 3)
    - Rate limiting
    - Caching
    - Performance monitoring
    - Error handling with retries
    """
    
    def __init__(
        self,
        provider: LLMProvider = LLMProvider.OPENAI,
        model: Optional[str] = None
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider to use
            model: Specific model (uses default if None)
        """
        self.provider = provider
        
        # Initialize clients
        if provider == LLMProvider.OPENAI:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = model or "gpt-4-turbo-preview"
        elif provider == LLMProvider.ANTHROPIC:
            self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = model or "claude-3-opus-20240229"
        
        logger.info(f"Initialized LLM client: {provider.value} / {self.model}")
    
    @cached_async(cache_type="api", ttl=3600)
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Generate text completion.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (context)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text
        """
        # Rate limiting
        rate_limiter = get_rate_limiter()
        await rate_limiter.wait_for_external_api(self.provider.value)
        
        # Performance monitoring
        monitor = get_performance_monitor()
        import time
        start_time = time.time()
        
        try:
            if self.provider == LLMProvider.OPENAI:
                response = await self._generate_openai(
                    prompt, system_prompt, temperature, max_tokens, **kwargs
                )
            elif self.provider == LLMProvider.ANTHROPIC:
                response = await self._generate_anthropic(
                    prompt, system_prompt, temperature, max_tokens, **kwargs
                )
            
            # Track success
            duration = time.time() - start_time
            monitor.track_external_api_call(self.provider.value, duration, True)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            monitor.track_external_api_call(self.provider.value, duration, False)
            logger.error(f"LLM generation failed: {e}", exc_info=True)
            raise
    
    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate using OpenAI."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    async def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate using Anthropic."""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[
                {"role": "user", "content": prompt}
            ],
            **kwargs
        )
        
        return response.content[0].text
    
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured output (JSON).
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            response_format: Expected response format
            **kwargs: Additional parameters
            
        Returns:
            Parsed JSON response
        """
        import json
        
        # Add JSON instruction to prompt
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        
        if response_format:
            json_prompt += f"\n\nExpected format:\n{json.dumps(response_format, indent=2)}"
        
        response = await self.generate(
            json_prompt,
            system_prompt,
            temperature=0.3,  # Lower temperature for structured output
            **kwargs
        )
        
        # Parse JSON
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
    
    async def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """
        Generate with automatic retries on failure.
        
        Args:
            prompt: User prompt
            max_retries: Maximum number of retries
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await self.generate(prompt, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"LLM generation attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)
        
        raise last_error


class LLMClientFactory:
    """Factory for creating LLM clients."""
    
    _clients: Dict[str, LLMClient] = {}
    
    @classmethod
    def get_client(
        cls,
        provider: LLMProvider = LLMProvider.OPENAI,
        model: Optional[str] = None
    ) -> LLMClient:
        """
        Get or create LLM client.
        
        Args:
            provider: LLM provider
            model: Specific model
            
        Returns:
            LLM client instance
        """
        key = f"{provider.value}:{model or 'default'}"
        
        if key not in cls._clients:
            cls._clients[key] = LLMClient(provider, model)
        
        return cls._clients[key]


# Convenience functions
async def generate_text(
    prompt: str,
    system_prompt: Optional[str] = None,
    provider: LLMProvider = LLMProvider.OPENAI,
    **kwargs
) -> str:
    """
    Generate text using default client.
    
    Args:
        prompt: User prompt
        system_prompt: System prompt
        provider: LLM provider
        **kwargs: Additional parameters
        
    Returns:
        Generated text
    """
    client = LLMClientFactory.get_client(provider)
    return await client.generate(prompt, system_prompt, **kwargs)


async def generate_json(
    prompt: str,
    system_prompt: Optional[str] = None,
    response_format: Optional[Dict[str, Any]] = None,
    provider: LLMProvider = LLMProvider.OPENAI,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate structured JSON output.
    
    Args:
        prompt: User prompt
        system_prompt: System prompt
        response_format: Expected format
        provider: LLM provider
        **kwargs: Additional parameters
        
    Returns:
        Parsed JSON
    """
    client = LLMClientFactory.get_client(provider)
    return await client.generate_structured(prompt, system_prompt, response_format, **kwargs)


if __name__ == "__main__":
    # Test LLM client
    async def test():
        client = LLMClient(provider=LLMProvider.OPENAI)
        
        response = await client.generate(
            "What is the capital of France?",
            system_prompt="You are a helpful assistant."
        )
        
        print(f"Response: {response}")
        
        # Test structured output
        json_response = await client.generate_structured(
            "Analyze Apple Inc. and provide investment recommendation.",
            response_format={
                "company": "string",
                "recommendation": "BUY/HOLD/SELL",
                "confidence": "float 0-1",
                "reasoning": "string"
            }
        )
        
        print(f"JSON Response: {json_response}")
    
    asyncio.run(test())
