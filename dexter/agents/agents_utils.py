from helium import *
from smolagents import ActionStep
from PIL import Image
from io import BytesIO
from time import sleep

def save_screenshot(memory_step: ActionStep, agent) -> None:
    """Set up screenshot callback for web automation agents."""
    sleep(1.0)  # Let JavaScript animations happen before taking the screenshot
    driver = helium.get_driver()
    current_step = memory_step.step_number
    if driver is not None:
        for previous_memory_step in agent.memory.steps:  # Remove previous screenshots for lean processing
            if isinstance(previous_memory_step, ActionStep) and previous_memory_step.step_number <= current_step - 2:
                previous_memory_step.observations_images = None
        png_bytes = driver.get_screenshot_as_png()
        image = Image.open(BytesIO(png_bytes))
        print(f"Captured a browser screenshot: {image.size} pixels")
        memory_step.observations_images = [image.copy()]  # Create a copy to ensure it persists

        # Get all clickable buttons
        buttons = find_all(Button())
        aria_labels = [b.web_element.get_attribute("aria-label") for b in buttons]
        aria_labels = [label for label in aria_labels if label is not None]
        buttons_text = "\nClickable buttons:\n" + str(aria_labels)

        # Update observations with current URL and buttons
        url_info = f"Current url: {driver.current_url}"
        memory_step.observations = (
            f"{url_info}\n{buttons_text}" if memory_step.observations is None 
            else f"{memory_step.observations}\n{url_info}\n{buttons_text}"
        )
