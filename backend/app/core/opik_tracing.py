"""
Opik tracing initialization and configuration
Official Opik SDK: https://www.comet.com/docs/opik/
"""
import os
from typing import Any, Callable
from functools import wraps

try:
    import opik
    from opik.decorator import track
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    print("Warning: opik package not installed. Tracing will be disabled.")


class OpikTracing:
    """Opik tracing wrapper for LLM calls and agent execution"""
    
    def __init__(self, project: str, workspace: str, api_key: str):
        self.project = project
        self.workspace = workspace
        self.api_key = api_key
        self.enabled = bool(api_key) and OPIK_AVAILABLE
        
        if self.enabled:
            # Configure Opik
            opik.configure(
                api_key=api_key,
                workspace=workspace,
            )
    
    def trace_agent(self, agent_name: str):
        """Decorator to trace agent execution"""
        def decorator(func: Callable) -> Callable:
            if not self.enabled:
                return func
            
            # Use Opik's @track decorator
            return track(
                name=agent_name,
                project_name=self.project,
            )(func)
        
        return decorator
    
    def trace_llm(self, model: str):
        """Decorator to trace LLM calls"""
        def decorator(func: Callable) -> Callable:
            if not self.enabled:
                return func
            
            # Use Opik's @track decorator with tags
            return track(
                name=f"llm_call_{model}",
                project_name=self.project,
                tags=["llm", model],
            )(func)
        
        return decorator


# Initialize global Opik instance
opik_tracing = OpikTracing(
    project=os.getenv("OPIK_PROJECT", "resolveai-debt-coach"),
    workspace=os.getenv("OPIK_WORKSPACE", ""),
    api_key=os.getenv("OPIK_API_KEY", "")
)
