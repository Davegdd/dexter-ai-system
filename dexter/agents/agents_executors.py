from concurrent.futures import ThreadPoolExecutor, Future
from typing import Any, Dict
import logging
from datetime import datetime
from selenium import webdriver

from dexter.agents.agents import test_agent as _test_agent_obj, youtube_agent as _youtube_agent_obj, auchan_agent as _auchan_agent_obj, report_agent as _report_agent_obj
from dexter.core.prompts import YOUTUBE_AGENT_INSTRUCTIONS, HELIUM_AGENT_INSTRUCTIONS, REPORT_AGENT_INSTRUCTIONS

logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=4)

current_date = datetime.now().strftime("%Y-%m-%d")

def test_agent(task: str, additional_args: Dict[str, Any] = None) -> Future:
    """
    Execute test_agent in a separate thread and return a Future.
    
    Args:
        task: String description of the task
        additional_args: Optional dictionary of additional arguments
    
    Returns:
        concurrent.futures.Future object
    """
    logger.info(f"Launching test_agent with task: '{task}'")
    if additional_args:
        logger.info(f"Additional arguments provided: {additional_args}")
    
    if additional_args is None:
        future = executor.submit(_test_agent_obj.run, task)
    else:
        future = executor.submit(_test_agent_obj.run, task, additional_args)
    
    logger.info(f"Agent launched successfully, Future ID: {id(future)}")
    return future

def youtube_agent(task: str, additional_args: Dict[str, Any] = None) -> Future:
    """
    Execute youtube_agent in a separate thread and return a Future.
    Pre-pends YouTube-specific instructions to the task.
    
    Args:
        task: String description of the task
        additional_args: Optional dictionary of additional arguments
    
    Returns:
        concurrent.futures.Future object
    """
    logger.info(f"Launching youtube_agent with task: '{task}'")
    if additional_args:
        logger.info(f"Additional arguments provided: {additional_args}")
    
    full_task = YOUTUBE_AGENT_INSTRUCTIONS.format(current_date=current_date) + "\n\n" + task
    
    if additional_args is None:
        future = executor.submit(_youtube_agent_obj.run, full_task)
    else:
        future = executor.submit(_youtube_agent_obj.run, full_task, additional_args)
    
    logger.info(f"Agent launched successfully, Future ID: {id(future)}")
    return future

def auchan_agent(task: str, additional_args: Dict[str, Any] = None) -> Future:
    """
    Execute auchan_agent in a separate thread and return a Future.
    Pre-pends helium-specific instructions to the task.
    
    Args:
        task: String description of the task
        additional_args: Optional dictionary of additional arguments
    
    Returns:
        concurrent.futures.Future object
    """
    logger.info(f"Launching auchan_agent with task: '{task}'")
    if additional_args:
        logger.info(f"Additional arguments provided: {additional_args}")
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--force-device-scale-factor=1")
    chrome_options.add_argument("--window-size=1000,1350")
    chrome_options.add_argument("--disable-pdf-viewer")
    chrome_options.add_argument("--window-position=0,0")

    import helium
    driver = helium.start_chrome(headless=False, options=chrome_options)
    
    _auchan_agent_obj.python_executor("from helium import *")
    _auchan_agent_obj.python_executor("from pypdf import *")
    
    full_task = HELIUM_AGENT_INSTRUCTIONS + "\n\n" + task
    
    if additional_args is None:
        future = executor.submit(_auchan_agent_obj.run, full_task)
    else:
        future = executor.submit(_auchan_agent_obj.run, full_task, additional_args)
    
    logger.info(f"Agent launched successfully, Future ID: {id(future)}")
    return future


def report_agent(task: str, additional_args: Dict[str, Any] = None) -> Future:
    """
    Execute report_agent in a separate thread and return a Future.
    Pre-pends import instructions to the task.
    
    Args:
        task: String description of the task
        additional_args: Optional dictionary of additional arguments
    
    Returns:
        concurrent.futures.Future object
    """

    logger.info(f"Launching report_agent with task: '{task}'")
    if additional_args:
        logger.info(f"Additional arguments provided: {additional_args}")
    
    full_task = REPORT_AGENT_INSTRUCTIONS + "\n\n" + task
    
    if additional_args is None:
        future = executor.submit(_report_agent_obj.run, full_task)
    else:
        future = executor.submit(_report_agent_obj.run, full_task, additional_args)
    
    logger.info(f"Agent launched successfully, Future ID: {id(future)}")
    return future


AGENTS = {
    "test": test_agent,
    "youtube": youtube_agent, 
    "auchan": auchan_agent,
    "report": report_agent
}

