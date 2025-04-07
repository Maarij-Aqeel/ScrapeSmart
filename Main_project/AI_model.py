"""This module provides a Model class for processing content using various generative AI models, with support for models like Gemini and DeepSeek. It enables extracting structured information from text content with options for chunked or non-chunked processing strategies."""

import google.generativeai as genai
import streamlit as st
from openai import OpenAI


class Model:
    def __init__(self, model, api_key):
        self.model = model
        self.api_key = api_key

    def process_with_chunking(self, chunks, description, history=None):
        """
        Processes content by breaking it into chunks and sending each chunk separately to the AI model.

        Args:
            chunks (list): List of text content chunks to process.
            description (str): Description of what information to extract from the content.
            history (list, optional): Conversation history for context continuation. Defaults to None.
        """
        if "gemini" in self.model:
            self.chunk_with_gemini(self, chunks, description, history)
        elif "deepseek" in self.model:
            self.chunk_with_deepseek(self, chunks, description, history)

    def process_with_nochunking(self, chunks, description, history=None):
        """
        Processes content by combining all chunks and sending to the model as a single request.

        Args:
            chunks (list): List of text content chunks to process.
            description (str): Description of what information to extract from the content.
            history (list, optional): Conversation history for context continuation. Defaults to None.

        Returns:

            tuple: (str, list) Containing the response content and updated conversation history."""
        if "gemini" in self.model:
            return self.nochunk_with_gemini(chunks, description, history)
        elif "deepseek" in self.model:
            return self.nochunk_with_deepseek(chunks, description, history)

    def construct_prompt(self, description):
        """
        Construct the system prompt for data extraction.

        Args:
            description: Description of what to extract

        Returns:
            Formatted system prompt
        """
        return (
            "You are a precision data extraction assistant. Your sole purpose is to process web content according to specific criteria. "
            "Follow these directives precisely:\n\n"
            f"1. **Information Extraction:** Extract ONLY data matching: {description}.\n"
            "2. **Zero Commentary:** Never explain, justify, or add commentary to your output.\n"
            "3. **Structured Format:** Present extracted data using Markdown formatting when appropriate (tables, lists).\n"
            "4. **Empty Results:** Return an empty string ('') if no matching information exists.\n"
            "5. **Conversational Mode:** Only when NO content is provided for extraction, respond conversationally to user queries.\n"
            "6. **Content Focus:** Focus exclusively on the content provided, not on external knowledge.\n"
            "7. **Data Consolidation:** When processing multiple content chunks, merge related information into a single coherent output.\n"
            "8. **Pattern Recognition:** Identify and extract recurring patterns in the data that match the description criteria."
        )

    def chunk_with_gemini(self, chunks, description, history=None):
        """Handles information extraction using Google's Gemini models with a chunking approach.

        Parameters:
            chunks (list): List of text content chunks to process individually.
            description (str): Description of what information to extract from the content.
            history (list, optional): Conversation history for context continuation. Defaults to None.

        Returns:
            tuple: (str, list) Containing the final combined result and updated conversation history."""

        if history is None:
            history = []
        system_prompt = self.construct_prompt(description)

        model = genai.GenerativeModel(self.model, system_instruction=system_prompt)
        try:
            response_placeholder = st.empty()
            all_responses = []  # collect responses first

            for chunk in chunks:
                full_input = f"Text content: {chunk}\n\nDescription: {description}"
                full_response = ""

                history.append({"role": "user", "parts": [{"text": full_input}]})

                for response_chunk in model.generate_content(history, stream=True):
                    if hasattr(response_chunk, "text"):
                        full_response += response_chunk.text

                if full_response.strip():
                    all_responses.append(full_response.strip())
                    history.append(
                        {"role": "model", "parts": [{"text": full_response.strip()}]}
                    )
                final_result = "\n".join(all_responses)
                response_placeholder.markdown(final_result)

            return final_result, history
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return "", history

    def chunk_with_deepseek(self, chunks, description, history=None):
        """Handles information extraction using DeepSeek models with a chunking approach via OpenRouter.

        Parameters:
            chunks (list): List of text content chunks to process individually.
            description (str): Description of what information to extract from the content.
            history (list, optional): Conversation history for context continuation. Defaults to None.

        Returns:
            tuple: (str, list) Containing the final combined result and updated conversation history."""
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1", api_key=self.api_key
            )

            if history is None:
                history = []

            system_prompt = self.construct_prompt(description)

            response_placeholder = st.empty()
            all_responses = []

            for chunk in chunks:
                full_input = f"Text content: {chunk}\n\nDescription: {description}"
                full_response = ""

                # Create messages for this request
                current_messages = [system_prompt]

                for msg in history:
                    current_messages.append(msg)
                # Add current user message
                current_messages.append({"role": "user", "content": full_input})

                # Stream the response
                response_stream = client.chat.completions.create(
                    model=self.model, messages=current_messages, stream=True
                )

                for response_chunk in response_stream:
                    if (
                        hasattr(response_chunk.choices[0].delta, "content")
                        and response_chunk.choices[0].delta.content is not None
                    ):
                        content = response_chunk.choices[0].delta.content
                        full_response += content
                        response_placeholder.markdown(full_response)

                if full_response.strip():
                    all_responses.append(full_response.strip())
                    # Add to history after complete response
                    history.append({"role": "user", "content": full_input})
                    history.append(
                        {"role": "assistant", "content": full_response.strip()}
                    )

            final_result = "\n".join(all_responses)
            response_placeholder.markdown(final_result)

            return final_result, history
        except Exception as e:
            st.error(f"Error occurred: {e}")
            return "", history

    def nochunk_with_gemini(self, chunks, description, history=None):
        """Handles information extraction using Google's Gemini models without chunking.

        Parameters:
            chunks (list): List of text content chunks to combine and process as one.
            description (str): Description of what information to extract from the content.
            history (list, optional): Conversation history for context continuation. Defaults to None.
        Returns:
            tuple: (str, list) Containing the response content and updated conversation history."""

        if history is None:
            history = []

        if not chunks:
            model = genai.GenerativeModel(
                self.model,
                system_instruction=(
                    "You are tasked with extracting specific information from the given text content. "
                    "If the user asks anything about web scraping, remind them to provide a link above. "
                    "From now on, please refer to yourself as ScrapeSmart."
                ),
            )
            response = model.generate_content(description)
            return response.text, history

        system_prompt = self.construct_prompt(description)
        model = genai.GenerativeModel(self.model, system_instruction=system_prompt)

        try:
            # Combine all chunks into a single input
            full_input = "\n\n".join(chunks) + f"\n\nDescription: {description}"

            # Append user input to history
            history.append({"role": "user", "parts": [{"text": full_input}]})

            response_placeholder = st.empty()
            full_response = ""

            for response_chunk in model.generate_content(history, stream=True):
                if hasattr(response_chunk, "text"):
                    full_response += response_chunk.text
                    response_placeholder.markdown(full_response)

            if full_response.strip():
                history.append(
                    {"role": "model", "parts": [{"text": full_response.strip()}]}
                )

            return full_response.strip(), history
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return "", history

    def nochunk_with_deepseek(self, chunks, description, history=None):
        """Handles information extraction using DeepSeek models without chunking via OpenRouter.

        Parameters:
            chunks (list): List of text content chunks to combine and process as one.
            description (str): Description of what information to extract from the content.
            history (list, optional): Conversation history for context continuation. Defaults to None.

        Returns:
            tuple: (str, list) Containing the response content and updated conversation history."""

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

        try:
            if history is None:
                history = []

            if not chunks:
                system_message = {
                    "role": "system",
                    "content": (
                        "You are tasked with extracting specific information from the given text content. "
                        "If the user asks anything about web scraping, remind them to provide a link above. "
                        "From now on, please refer to yourself as ScrapeSmart."
                    ),
                }

                messages = [system_message, {"role": "user", "content": description}]
                response = client.chat.completions.create(
                    model=self.model, messages=messages
                )

                return response.choices[0].message.content, history

            system_prompt = self.construct_prompt(description)

            full_input = "\n\n".join(chunks) + f"\n\nDescription: {description}"
            response_placeholder = st.empty()
            messages = [system_prompt]
            # Add history messages
            for msg in history:
                messages.append(msg)
            # Add current user message
            messages.append({"role": "user", "content": full_input})

            response_placeholder = st.empty()
            full_response = ""

            response_stream = client.chat.completions.create(
                model=self.model, messages=messages, stream=True
            )

            for response_chunk in response_stream:
                if (
                    hasattr(response_chunk.choices[0].delta, "content")
                    and response_chunk.choices[0].delta.content is not None
                ):
                    content = response_chunk.choices[0].delta.content
                    full_response += content
                    response_placeholder.markdown(full_response)

            if full_response.strip():
                # Store model response
                history.append({"role": "user", "content": full_input})
                history.append({"role": "assistant", "content": full_response.strip()})

            return full_response.strip(), history
        except Exception as e:
            st.error(f"Error occurred: {e}")
            return "", history
