from unittest.mock import Mock, patch
from concurrent.futures import Future

from dexter.utils.common import (
    format_content,
    extract_code_from_text,
    run_extracted_code,
    generate_tools_prompt,
    generate_agents_prompt
)


class TestFormatContent:
    """Test cases for format_content function."""
    
    def test_format_content_text_only(self):
        """Test formatting content with text only."""
        # Arrange
        text = "Hello, world!"
        
        # Act
        result = format_content(text)
        
        # Assert
        expected = [{"type": "text", "text": "Hello, world!"}]
        assert result == expected
    
    def test_format_content_with_image(self):
        """Test formatting content with both text and image."""
        # Arrange
        text = "Describe this image"
        image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        # Act
        result = format_content(text, image)
        
        # Assert
        expected = [
            {"type": "image", "image": f"data:image;base64,{image}"},
            {"type": "text", "text": "Describe this image"}
        ]
        assert result == expected
    
    def test_format_content_empty_text(self):
        """Test formatting content with empty text."""
        # Arrange
        text = ""
        
        # Act
        result = format_content(text)
        
        # Assert
        expected = [{"type": "text", "text": ""}]
        assert result == expected


class TestExtractCodeFromText:
    """Test cases for extract_code_from_text function."""
    
    def test_extract_python_code_block(self):
        """Test extracting Python code from text."""
        # Arrange
        text = """Here's some code:
```python
print("Hello, world!")
x = 5 + 3
```
That was the code."""
        
        # Act
        result = extract_code_from_text(text)
        
        # Assert
        expected = 'print("Hello, world!")\nx = 5 + 3'
        assert result == expected
    
    def test_extract_py_code_block(self):
        """Test extracting code with py tag."""
        # Arrange
        text = """Code example:
```py
def hello():
    return "world"
```"""
        
        # Act
        result = extract_code_from_text(text)
        
        # Assert
        expected = 'def hello():\n    return "world"'
        assert result == expected
    
    def test_extract_tool_code_block(self):
        """Test extracting code with tool_code tag."""
        # Arrange
        text = """Tool usage:
```tool_code
some_tool(param="value")
```"""
        
        # Act
        result = extract_code_from_text(text)
        
        # Assert
        expected = 'some_tool(param="value")'
        assert result == expected
    
    def test_extract_multiple_code_blocks(self):
        """Test extracting multiple code blocks."""
        # Arrange
        text = """First block:
```python
x = 1
```
Second block:
```py
y = 2
```"""
        
        # Act
        result = extract_code_from_text(text)
        
        # Assert
        expected = "x = 1\n\ny = 2"
        assert result == expected
    
    def test_no_code_blocks(self):
        """Test when no code blocks are present."""
        # Arrange
        text = "This text has no code blocks."
        
        # Act
        result = extract_code_from_text(text)
        
        # Assert
        assert result is None
    
    def test_custom_code_block_tags(self):
        """Test with custom code block tags."""
        # Arrange
        text = "Custom code: <start>print('test')<end>"
        custom_tags = ("<start>", "<end>")
        
        # Act
        result = extract_code_from_text(text, custom_tags)
        
        # Assert
        expected = "print('test')"
        assert result == expected


class TestRunExtractedCode:
    """Test cases for run_extracted_code function."""
    
    @patch('dexter.utils.common.custom_executor')
    def test_run_code_success(self, mock_executor):
        """Test successful code execution."""
        # Arrange
        code = "print('Hello')"
        mock_executor.return_value = ["Hello"]
        
        # Act
        result = run_extracted_code(code)
        
        # Assert
        mock_executor.assert_called_once_with(code)
        assert result == "Code execution results: ['Hello']"
    
    @patch('dexter.utils.common.custom_executor')
    def test_run_code_returns_future(self, mock_executor):
        """Test code execution that returns a Future."""
        # Arrange
        code = "async_task()"
        mock_future = Mock(spec=Future)
        mock_executor.return_value = [mock_future]
        
        # Act
        result = run_extracted_code(code)
        
        # Assert
        mock_executor.assert_called_once_with(code)
        assert result == mock_future
    
    @patch('dexter.utils.common.custom_executor')
    def test_run_code_exception(self, mock_executor):
        """Test code execution that raises an exception."""
        # Arrange
        code = "invalid syntax"
        mock_executor.side_effect = Exception("Syntax error")
        
        # Act
        result = run_extracted_code(code)
        
        # Assert
        mock_executor.assert_called_once_with(code)
        assert result == "Code execution results: Syntax error"


class TestGenerateToolsPrompt:
    """Test cases for generate_tools_prompt function."""
    
    def test_generate_tools_prompt_single_tool(self):
        """Test generating prompt for a single tool."""
        # Arrange
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "A test tool"
        mock_tool.inputs = {
            "param1": {"type": str, "description": "First parameter"},
            "param2": {"type": int, "description": "Second parameter"}
        }
        mock_tool.output_type = str
        
        # Act
        result = generate_tools_prompt([mock_tool])
        
        # Assert
        assert "def test_tool(param1: str, param2: int) -> str:" in result
        assert "A test tool" in result
        assert "param1: First parameter" in result
        assert "param2: Second parameter" in result
        assert "You have several tools available" in result
    
    def test_generate_tools_prompt_multiple_tools(self):
        """Test generating prompt for multiple tools."""
        # Arrange
        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "First tool"
        tool1.inputs = {"arg": {"type": str, "description": "Argument"}}
        tool1.output_type = str
        
        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Second tool"
        tool2.inputs = {"num": {"type": int, "description": "Number"}}
        tool2.output_type = int
        
        # Act
        result = generate_tools_prompt([tool1, tool2])
        
        # Assert
        assert "def tool1(arg: str) -> str:" in result
        assert "def tool2(num: int) -> int:" in result
        assert "First tool" in result
        assert "Second tool" in result
    
    def test_generate_tools_prompt_no_inputs(self):
        """Test generating prompt for tool with no inputs."""
        # Arrange
        mock_tool = Mock()
        mock_tool.name = "simple_tool"
        mock_tool.description = "Simple tool with no inputs"
        mock_tool.inputs = {}
        mock_tool.output_type = str
        
        # Act
        result = generate_tools_prompt([mock_tool])
        
        # Assert
        assert "def simple_tool() -> str:" in result
        assert "Simple tool with no inputs" in result


class TestGenerateAgentsPrompt:
    """Test cases for generate_agents_prompt function."""
    
    def test_generate_agents_prompt_single_agent(self):
        """Test generating prompt for a single agent."""
        # Arrange
        mock_agent = Mock()
        mock_agent.name = "Test Agent"
        mock_agent.description = "A test agent for testing"
        
        # Act
        result = generate_agents_prompt([mock_agent])
        
        # Assert
        assert "def test_agent(task: str, additional_args: dict[str, Any]) -> str:" in result
        assert "A test agent for testing" in result
        assert "You can also give tasks to agents" in result
        assert "task: Long detailed description" in result
        assert "additional_args: Dictionary of extra inputs" in result
    
    def test_generate_agents_prompt_multiple_agents(self):
        """Test generating prompt for multiple agents."""
        # Arrange
        agent1 = Mock()
        agent1.name = "First Agent"
        agent1.description = "First test agent"
        
        agent2 = Mock()
        agent2.name = "Second Agent"
        agent2.description = "Second test agent"
        
        # Act
        result = generate_agents_prompt([agent1, agent2])
        
        # Assert
        assert "def first_agent(task: str, additional_args: dict[str, Any]) -> str:" in result
        assert "def second_agent(task: str, additional_args: dict[str, Any]) -> str:" in result
        assert "First test agent" in result
        assert "Second test agent" in result
    
    def test_generate_agents_prompt_agent_name_with_spaces(self):
        """Test agent name conversion with spaces and special characters."""
        # Arrange
        mock_agent = Mock()
        mock_agent.name = "Complex Agent Name"
        mock_agent.description = "An agent with complex name"
        
        # Act
        result = generate_agents_prompt([mock_agent])
        
        # Assert
        assert "def complex_agent_name(task: str, additional_args: dict[str, Any]) -> str:" in result