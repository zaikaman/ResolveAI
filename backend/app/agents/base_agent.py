"""
Base agent class with Opik tracing integration.

All agents inherit from this class to get automatic tracing and monitoring.
"""

from typing import Any, Dict, Optional, Callable, TypeVar
from functools import wraps
import traceback
from app.core.opik_tracing import opik_tracing
from app.core.errors import SystemError, ExternalError

F = TypeVar('F', bound=Callable[..., Any])


class BaseAgent:
    """
    Base class for all AI agents with built-in Opik tracing.
    
    Features:
    - Automatic Opik tracing for agent execution
    - Error handling and recovery
    - Input/output logging
    - Performance monitoring
    
    Usage:
        class MyAgent(BaseAgent):
            def __init__(self):
                super().__init__(agent_name="MyAgent")
            
            async def execute(self, input_data: dict) -> dict:
                return await self.trace_execution(
                    self._process,
                    input_data=input_data
                )
            
            async def _process(self, input_data: dict) -> dict:
                # Agent logic here
                return {"result": "success"}
    """
    
    def __init__(self, agent_name: str, description: Optional[str] = None) -> None:
        """
        Initialize base agent.
        
        Args:
            agent_name: Name of the agent for tracing
            description: Optional description of agent purpose
        """
        self.agent_name = agent_name
        self.description = description or f"{agent_name} agent"
        self.tracer = opik_tracing
    
    async def trace_execution(
        self,
        func: Callable[..., Any],
        **kwargs: Any
    ) -> Any:
        """
        Execute a function with Opik tracing.
        
        Args:
            func: Function to execute
            **kwargs: Arguments to pass to function
        
        Returns:
            Function result
        
        Raises:
            SystemError: If execution fails
        """
        try:
            # If tracing is enabled, wrap the function with the tracer
            if self.tracer.enabled:
                traced_func = self.tracer.trace_agent(self.agent_name)(func)
                result = await traced_func(**kwargs)
            else:
                result = await func(**kwargs)
            
            return result
        
        except SystemError:
            # Re-raise SystemError as-is
            raise
        
        except Exception as e:
            error_trace = traceback.format_exc()
            
            # Log error (just to console since we don't have a separate log_error method)
            print(f"Agent {self.agent_name} error: {e}\n{error_trace}")
            
            # Serialize kwargs for JSON output - convert Pydantic models to dicts
            serializable_input = {}
            for key, value in kwargs.items():
                if hasattr(value, 'model_dump'):
                    # Pydantic v2 model
                    serializable_input[key] = value.model_dump(mode='json')
                elif hasattr(value, 'dict'):
                    # Pydantic v1 model
                    serializable_input[key] = value.dict()
                elif isinstance(value, list):
                    # List of potential Pydantic models
                    serializable_input[key] = [
                        item.model_dump(mode='json') if hasattr(item, 'model_dump') 
                        else item.dict() if hasattr(item, 'dict')
                        else item
                        for item in value
                    ]
                else:
                    serializable_input[key] = value
            
            raise SystemError(
                message=f"{self.agent_name} execution failed",
                error_code="AGENT_EXECUTION_ERROR",
                details={
                    "agent": self.agent_name,
                    "error": str(e),
                    "input": serializable_input
                }
            )
    
    def validate_input(self, required_fields: list[str], input_data: Dict[str, Any]) -> None:
        """
        Validate that required input fields are present.
        
        Args:
            required_fields: List of required field names
            input_data: Input data dictionary
        
        Raises:
            SystemError: If required fields are missing
        """
        missing_fields = [field for field in required_fields if field not in input_data]
        
        if missing_fields:
            raise SystemError(
                message=f"{self.agent_name}: Missing required input fields",
                error_code="INVALID_AGENT_INPUT",
                details={
                    "agent": self.agent_name,
                    "missing_fields": missing_fields,
                    "required_fields": required_fields
                }
            )
    
    async def execute(self, **kwargs: Any) -> Any:
        """
        Execute agent logic. Must be implemented by subclasses.
        
        Args:
            **kwargs: Agent-specific input parameters
        
        Returns:
            Agent output
        
        Raises:
            NotImplementedError: If not overridden by subclass
        """
        raise NotImplementedError(f"{self.agent_name}.execute() must be implemented")


def track_agent_execution(agent_name: str) -> Callable[[F], F]:
    """
    Decorator for automatic agent execution tracking.
    
    Usage:
        @track_agent_execution("MyAgent")
        async def process_data(data: dict) -> dict:
            # Agent logic
            return result
    
    Args:
        agent_name: Name of the agent for tracking
    
    Returns:
        Decorated function with Opik tracing
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                # Use the global tracer's decorator
                if opik_tracing.enabled:
                    traced_func = opik_tracing.trace_agent(agent_name)(func)
                    return await traced_func(*args, **kwargs)
                else:
                    return await func(*args, **kwargs)
            
            except Exception as e:
                # Log error but don't block execution
                print(f"Agent {agent_name} error: {e}\n{traceback.format_exc()}")
                raise
        
        return wrapper  # type: ignore
    return decorator
