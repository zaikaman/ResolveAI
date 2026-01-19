"""
Opik tracing initialization and configuration
Official Opik SDK: https://www.comet.com/docs/opik/
"""
import os
from typing import Any, Callable
from functools import wraps

try:
    import opik
    from opik import track
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    track = None  # type: ignore[assignment]
    print("Warning: opik package not installed. Tracing will be disabled.")


class OpikTracing:
    """Opik tracing wrapper for LLM calls and agent execution"""
    
    def __init__(
        self,
        project: str = "",
        workspace: str = "",
        api_key: str = ""
    ) -> None:
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
    
    def trace_agent(self, agent_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to trace agent execution"""
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            if not self.enabled or track is None:
                return func
            
            # Use Opik's @track decorator
            tracked: Callable[..., Any] = track(
                name=agent_name,
                project_name=self.project,
            )(func)
            return tracked
        
        return decorator
    
    def trace_llm(self, model: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to trace LLM calls"""
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            if not self.enabled or track is None:
                return func
            
            # Use Opik's @track decorator with tags
            tracked: Callable[..., Any] = track(
                name=f"llm_call_{model}",
                project_name=self.project,
                tags=["llm", model],
            )(func)
            return tracked
        
        return decorator


# Initialize global Opik instance
opik_tracing = OpikTracing(
    project=os.getenv("OPIK_PROJECT", "resolveai-debt-coach"),
    workspace=os.getenv("OPIK_WORKSPACE", ""),
    api_key=os.getenv("OPIK_API_KEY", "")
)
