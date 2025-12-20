"""
AI Cleanup and Summarization Service

This service handles AI-powered text summarization and cleanup using OpenAI GPT API.

Responsibilities:
- Format transcripts for AI processing
- Send requests to OpenAI API
- Parse and format AI responses
- Handle API rate limits and errors
- Manage API key configuration

Prompt Templates:
- Summary: "Provide a concise summary of the following transcript..."
- Cleanup: "Clean up this transcript by removing filler words..."
- Key Points: "Extract the main points from this transcript..."

Dependencies:
- openai (Python SDK)
"""

import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI
from openai import OpenAIError, RateLimitError, APIError

logger = logging.getLogger(__name__)


class AICleanupService:
    """
    Service for AI-powered text summarization and cleanup.
    
    This service integrates with OpenAI's GPT API to provide intelligent
    summarization and cleanup of transcribed text.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview"
    ) -> None:
        """
        Initialize the AI cleanup service.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4-turbo-preview)
        """
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"AI cleanup service initialized with model: {model}")
    
    def _call_api(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """
        Internal method to call OpenAI API.
        
        Args:
            system_prompt: System prompt for the AI
            user_message: User message/content
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            API response text
            
        Raises:
            Exception: If API call fails
        """
        try:
            logger.info(f"Calling OpenAI API with model: {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            result = response.choices[0].message.content.strip()
            logger.info(f"API call successful, response length: {len(result)} characters")
            return result
            
        except RateLimitError as e:
            error_msg = "OpenAI API rate limit exceeded. Please try again later."
            logger.error(f"{error_msg}: {str(e)}")
            raise Exception(error_msg)
            
        except APIError as e:
            error_msg = f"OpenAI API error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except OpenAIError as e:
            error_msg = f"OpenAI service error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error calling OpenAI API: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def summarize_text(
        self,
        text: str,
        max_length: Optional[int] = None,
        style: str = "concise"
    ) -> str:
        """
        Generate a summary of the provided text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary (optional)
            style: Summary style ('concise', 'detailed', 'bullet')
            
        Returns:
            Summarized text
            
        Raises:
            Exception: If API call fails
        """
        if not text or not text.strip():
            raise ValueError("Text to summarize cannot be empty")
        
        logger.info(f"Generating {style} summary for text of length {len(text)}")
        
        # Build system prompt based on style
        style_instructions = {
            'concise': "Provide a concise, well-structured summary that captures the main ideas.",
            'detailed': "Provide a detailed, comprehensive summary that covers all important points.",
            'bullet': "Provide a summary in bullet point format, highlighting key information."
        }
        
        instruction = style_instructions.get(style, style_instructions['concise'])
        
        system_prompt = f"""You are an expert at summarizing transcripts and extracting key information.
{instruction}
Focus on the most important information and maintain clarity."""
        
        user_message = f"Please summarize the following transcript:\n\n{text}"
        
        if max_length:
            user_message += f"\n\nKeep the summary under {max_length} words."
        
        return self._call_api(
            system_prompt=system_prompt,
            user_message=user_message,
            max_tokens=2000,
            temperature=0.7
        )
    
    def clean_transcript(self, text: str) -> str:
        """
        Clean up transcript by removing filler words and improving readability.
        
        Args:
            text: Transcript text to clean
            
        Returns:
            Cleaned transcript text
            
        Raises:
            Exception: If API call fails
        """
        if not text or not text.strip():
            raise ValueError("Text to clean cannot be empty")
        
        logger.info(f"Cleaning transcript of length {len(text)}")
        
        system_prompt = """You are an expert at cleaning up transcripts.
Remove filler words (um, uh, like, you know, etc.), fix grammar, and improve readability.
Maintain the original meaning and tone. Keep the content natural and conversational."""
        
        user_message = f"Please clean up this transcript:\n\n{text}"
        
        return self._call_api(
            system_prompt=system_prompt,
            user_message=user_message,
            max_tokens=3000,
            temperature=0.5
        )
    
    def generate_key_points(self, text: str) -> List[str]:
        """
        Extract key points from the transcript.
        
        Args:
            text: Transcript text to analyze
            
        Returns:
            List of key points
            
        Raises:
            Exception: If API call fails
        """
        if not text or not text.strip():
            raise ValueError("Text to analyze cannot be empty")
        
        logger.info(f"Extracting key points from text of length {len(text)}")
        
        system_prompt = """You are an expert at extracting key points from transcripts.
Identify the most important takeaways and present them as a clear, numbered list.
Each point should be concise but complete. Aim for 3-7 key points."""
        
        user_message = f"Please extract the key points from this transcript:\n\n{text}"
        
        response = self._call_api(
            system_prompt=system_prompt,
            user_message=user_message,
            max_tokens=1000,
            temperature=0.7
        )
        
        # Parse the response into a list
        # Split by newlines and filter out empty lines
        key_points = [
            line.strip().lstrip('0123456789.-) ').strip()
            for line in response.split('\n')
            if line.strip() and not line.strip().startswith('#')
        ]
        
        # Filter out very short lines (likely formatting artifacts)
        key_points = [point for point in key_points if len(point) > 10]
        
        logger.info(f"Extracted {len(key_points)} key points")
        return key_points
    
    def custom_prompt(self, text: str, prompt: str) -> str:
        """
        Process text with a custom prompt.
        
        Args:
            text: Text to process
            prompt: Custom prompt for processing
            
        Returns:
            Processed text based on custom prompt
            
        Raises:
            Exception: If API call fails
        """
        if not text or not text.strip():
            raise ValueError("Text to process cannot be empty")
        
        if not prompt or not prompt.strip():
            raise ValueError("Custom prompt cannot be empty")
        
        logger.info(f"Processing text with custom prompt: {prompt[:50]}...")
        
        system_prompt = "You are a helpful AI assistant that processes transcripts according to user instructions."
        
        user_message = f"{prompt}\n\nTranscript:\n{text}"
        
        return self._call_api(
            system_prompt=system_prompt,
            user_message=user_message,
            max_tokens=2000,
            temperature=0.7
        )