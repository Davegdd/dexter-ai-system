from datetime import datetime
from litellm import completion
from ..utils.common import extract_code_from_text, format_content, generate_tools_prompt, run_extracted_code, generate_agents_prompt
from .prompts import build_system_prompt
from ..config.settings import settings
import logging
import time
from smolagents import WebSearchTool, VisitWebpageTool
from dexter.agents.agents import test_agent, youtube_agent, auchan_agent, report_agent
from concurrent.futures import Future
from tenacity import retry, stop_after_attempt, wait_exponential
from dexter.service.history_manager import HistoryManager
from typing import Any

logger = logging.getLogger(__name__)

class LLM:
    _instance: 'LLM' = None
    model: str
    tools: str
    agents: str
    system_prompt: str
    complete_response: str | None
    speech_text: str | None
    new_history: bool
    history_manager: HistoryManager
    history: list[dict[str, Any]] | None
    timestamp_mode: bool
    pending_tasks: list[Future]
    session_tag: str | None

    def __new__(cls, *args, **kwargs) -> 'LLM':
        if cls._instance is None:
            cls._instance = super(LLM, cls).__new__(cls)
            cls._instance.model = settings.DEFAULT_MODEL
            cls._instance.tools = generate_tools_prompt([WebSearchTool, VisitWebpageTool])
            cls._instance.agents = generate_agents_prompt([test_agent, youtube_agent, auchan_agent, report_agent])
            cls._instance.system_prompt = build_system_prompt(
                memories=[],
                tools=cls._instance.tools,
                agents=cls._instance.agents
            )
            cls._instance.complete_response = None
            cls._instance.speech_text = None
            cls._instance.new_history = False
            cls._instance.history_manager = HistoryManager()
            cls._instance.history = None
            cls._instance.timestamp_mode = True
            cls._instance.pending_tasks = []
            cls._instance.session_tag = None

        return cls._instance

    def _check_completed_tasks(self) -> None:
        """Check for completed tasks from agents and process their results."""
        completed_tasks: list[tuple[int, Any]] = []
        for i, task in enumerate(self.pending_tasks):
            if task.done():
                try:
                    result = task.result()
                    logger.info(f"Agent task completed with result: {result}")
                    completed_tasks.append((i, result))
                except Exception as e:
                    logger.error(f"Agent task completed with error: {e}")
                    completed_tasks.append((i, f"Task error: {str(e)}"))
        
        if completed_tasks:
            combined_results = "\n".join([f"Result from agent task to convey to user: {str(result)}" for i, result in completed_tasks])
            for i, _ in reversed(completed_tasks):
                self.pending_tasks.pop(i)
            self.llm_input(format_content(combined_results))

    def _prepare_input_file_content(self, base64_data: str, file_type: str) -> dict[str, Any]:
        """Prepare file content with appropriate MIME type for multimodal messages."""
        if file_type == "video":
            mime_type = "data:video/mp4;base64,"
        elif file_type == "image":
            mime_type = "data:image/jpeg;base64,"
        else:
            mime_type = "data:image/jpeg;base64,"
        
        return {
            "type": "file",
            "file": {
                "file_data": mime_type + base64_data
            },
        }

    def _prepare_user_message(self, user_text: str, base64_data: str | None = None, file_type: str | None = None) -> dict[str, Any]:
        """Prepare user message with optional file content for multimodal messages."""
        if base64_data:
            return {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    self._prepare_input_file_content(base64_data, file_type),
                ],
            }
        else:
            return {"role": "user", "content": user_text}

    @retry(
        stop=stop_after_attempt(settings.MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=settings.RETRY_MIN_WAIT, max=settings.RETRY_MAX_WAIT),
        before_sleep=lambda retry_state: logger.warning(f"API call failed (attempt {retry_state.attempt_number}/{settings.MAX_RETRY_ATTEMPTS}). Error: {retry_state.outcome.exception()}. Retrying in {retry_state.next_action.sleep} seconds...")
    )
    def _send_message_with_retry(self, messages: list[dict[str, Any]]) -> Any:
        """Send message with tenacity retry logic for any API errors."""
        return completion(
            model=self.model,
            messages=messages,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            top_p=settings.TOP_P,
            tools=[],
            tool_choice="auto"
        )

    def _add_timestamp_if_enabled(self, text: str) -> str:
        """
        Add timestamp prefix to user text if timestamp_mode is enabled.
        """
        if self.timestamp_mode:
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            return f"[{timestamp}] {text}"
        return text

    def _extract_speech_text(self, response_text: str, extracted_code: str) -> str:
        """Extract speech-friendly text by removing code blocks."""
        speech_text = response_text
        for code_block in ["```py", "```tool_code"]:
            if code_block in speech_text:
                speech_text = speech_text.replace(f"{code_block}\n{extracted_code}\n```", "")
        return speech_text

    def llm_input(self, question_type_dict: list[dict[str, str]], base64_data: str | None = None, file_type: str | None = None) -> None:
        """Interact with the model using a pure-text conversation approach."""
        self.complete_response = None
        self.speech_text = None

        if self.new_history:
            logger.info("Starting new conversation history")
            self.history_manager.get_history_file(new_history=True)
            self.history = [{}]
            self.new_history = False
        elif self.history is None:
            logger.info("Loading existing conversation history")
            self.history_manager.get_history_file(new_history=False)
            self.history = self.history_manager.load_history()
        
        user_text = question_type_dict[0]['text']
        user_text = self._add_timestamp_if_enabled(user_text)

        self.history[0] = {"role": "system", "content": self.system_prompt}

        messages = self.history.copy()

        user_message = self._prepare_user_message(user_text, base64_data, file_type)
        messages.append(user_message)

        start_time = time.time()
        response = self._send_message_with_retry(messages)
        end_time = time.time()
        time_taken = end_time - start_time
        logger.info(f"Time taken for response generation: {time_taken} seconds")
        
        self.complete_response = response.choices[0].message.content
        logger.info("Dexter: " + self.complete_response)
        extracted_code = extract_code_from_text(self.complete_response)
        
        if extracted_code:
            self.speech_text = self._extract_speech_text(self.complete_response, extracted_code)
            
            user_msg = {"role": "user", "content": user_text}
            assistant_msg = {"role": "assistant", "content": self.complete_response}
            
            self.history.append(user_msg)
            self.history.append(assistant_msg)
            self.history_manager.save_history(self.history)
            
            # Save to session if session_tag is set
            if self.session_tag:
                self.history_manager.save_to_session(self.session_tag, user_msg, assistant_msg, self.system_prompt)

            execution_results = run_extracted_code(extracted_code)
            
            if isinstance(execution_results, Future):
                logger.info("Adding Future task to pending tasks list")
                self.pending_tasks.append(execution_results)
            else:
                self.llm_input(format_content(execution_results))
            return
        
        logger.info("Adding assistant response to history")
        
        user_msg = {"role": "user", "content": user_text}
        assistant_msg = {"role": "assistant", "content": self.complete_response}
        
        self.history.append(user_msg)
        self.history.append(assistant_msg)
        self.history_manager.save_history(self.history)
        
        if self.session_tag:
            self.history_manager.save_to_session(self.session_tag, user_msg, assistant_msg, self.system_prompt)

        logger.info("Saved updated history to file")

        # Check for completed tasks at the end of interaction
        self._check_completed_tasks()
        return