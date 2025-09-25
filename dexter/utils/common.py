import logging
import re
from concurrent.futures import Future

from smolagents.local_python_executor import LocalPythonExecutor
from dexter.core.prompts import TOOLS_PROMPT_TEMPLATE, AGENTS_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

custom_executor = LocalPythonExecutor(
    ["numpy", "dexter.agents.tools", "dexter.agents.agents_executors"]
)
custom_executor(
    "from dexter.agents.tools import *"
)  # Import all tools for local persistent executor
custom_executor(
    "from dexter.agents.agents_executors import test_agent, youtube_agent, auchan_agent, report_agent"
)  # Import functions to run agents


def format_content(text: str, image: str | None = None) -> list[dict[str, str]]:
    """
    Format the given image and text into content structure.

    Args:
        image (str, optional): The base64 encoded image string. Defaults to None.
        text (str): The text string.

    Returns:
        dict: The formatted content.
    """
    content = [
        {
            "type": "text",
            "text": text,
        }
    ]

    if image:
        content.insert(
            0,
            {
                "type": "image",
                "image": f"data:image;base64,{image}",
            },
        )

    return content


def extract_code_from_text(
    text: str, code_block_tags: tuple[str, str] = ("```(?:python|py|tool_code|tool_call)", "```")
) -> str | None:
    """Extract code from the LLM's output."""
    pattern = rf"{code_block_tags[0]}(.*?){code_block_tags[1]}"
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        logger.info(f"Extracted code: {matches}")
        return "\n\n".join(match.strip() for match in matches)
    return None


def run_extracted_code(code: str):
    """
    Extract and run code from text using custom executor.

    Args:
        code (str): Code to execute

    Returns:
        concurrent.futures.Future or str: Returns Future if code creates one, otherwise returns result string
    """
    try:
        logger.info("Executing extracted code")
        result = custom_executor(code)
        # If result is a Future, return it directly (it's an agent working in background)
        if isinstance(result.output, Future):
            logger.info("Code execution returned Future - agent task running in background")
            return result.output

        logger.info("Code execution completed successfully")
        return f"Code execution results: {result.output}"
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        return f"Code execution results: {str(e)}"


def generate_tools_prompt(tools_list: list) -> str:
    """Generate function signatures for a list of tools."""
    signatures = []

    for tool in tools_list:
        # Extract argument information - tool.inputs is a dict with type info
        args = ", ".join(
            f"{arg_name}: {arg_info['type'].__name__ if hasattr(arg_info['type'], '__name__') else str(arg_info['type'])}"
            for arg_name, arg_info in tool.inputs.items()
        )

        # Extract argument descriptions
        doc_args = "\n".join(
            f"        {arg_name}: {arg_info['description']}"
            for arg_name, arg_info in tool.inputs.items()
        )

        # Get return type
        return_type = (
            tool.output_type.__name__
            if hasattr(tool.output_type, "__name__")
            else str(tool.output_type)
        )

        # Generate the function signature string
        func_signature = f"""def {tool.name}({args}) -> {return_type}:
    \"\"\"{tool.description}

    Args:
{doc_args}
    \"\"\""""

        signatures.append(func_signature)

    return TOOLS_PROMPT_TEMPLATE + "\n\n".join(signatures)


def generate_agents_prompt(agent_objects: list) -> str:
    """Get the function signatures of all agent objects as a formatted string."""
    signatures = []

    for agent_obj in agent_objects:
        agent_name = agent_obj.name.replace(" ", "_").lower()
        signature = f'''def {agent_name}(task: str, additional_args: dict[str, Any]) -> str:
    """{agent_obj.description}

    Args:
        task: Long detailed description of the task.
        additional_args: Dictionary of extra inputs to pass to the managed agent, e.g. images, dataframes, or any other contextual data it may need.
    """'''
        signatures.append(signature)

    return AGENTS_PROMPT_TEMPLATE + "\n\n" + "\n\n".join(signatures) + "\n```"
