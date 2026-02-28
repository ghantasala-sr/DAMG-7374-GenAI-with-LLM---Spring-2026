"""
Parallel Analyst Executor - Concurrent Agent Execution.

Manages parallel execution of multiple analyst agents using asyncio,
with progress tracking, error handling, and result aggregation.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from analysts.base_analyst import BaseAnalyst, AnalystResult


class ExecutionStatus(Enum):
    """Status of analyst execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AnalystExecution:
    """Tracks execution state of a single analyst."""
    analyst_name: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Optional[AnalystResult] = None
    error: Optional[str] = None
    
    @property
    def execution_time_ms(self) -> float:
        """Calculate execution time in milliseconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "analyst_name": self.analyst_name,
            "status": self.status.value,
            "execution_time_ms": self.execution_time_ms,
            "result": self.result.to_dict() if self.result else None,
            "error": self.error
        }


@dataclass
class ParallelExecutionResult:
    """Results from parallel analyst execution."""
    executions: Dict[str, AnalystExecution] = field(default_factory=dict)
    total_time_ms: float = 0.0
    start_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def successful_results(self) -> Dict[str, AnalystResult]:
        """Get only successful analyst results."""
        return {
            name: exec.result
            for name, exec in self.executions.items()
            if exec.status == ExecutionStatus.COMPLETED and exec.result
        }
    
    @property
    def failed_analysts(self) -> List[str]:
        """Get list of failed analysts."""
        return [
            name for name, exec in self.executions.items()
            if exec.status == ExecutionStatus.FAILED
        ]
    
    @property
    def all_completed(self) -> bool:
        """Check if all analysts completed successfully."""
        return all(
            exec.status == ExecutionStatus.COMPLETED
            for exec in self.executions.values()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "executions": {k: v.to_dict() for k, v in self.executions.items()},
            "total_time_ms": self.total_time_ms,
            "start_timestamp": self.start_timestamp,
            "successful_count": len(self.successful_results),
            "failed_count": len(self.failed_analysts)
        }


class ParallelAnalystExecutor:
    """
    Executes multiple analyst agents in parallel using asyncio.
    
    Features:
    - True parallel execution using asyncio.gather
    - Progress tracking with callbacks
    - Error isolation (one failure doesn't stop others)
    - Timeout handling
    - Result aggregation
    """
    
    def __init__(
        self,
        timeout_seconds: float = 60.0,
        on_analyst_start: Optional[Callable[[str], None]] = None,
        on_analyst_complete: Optional[Callable[[str, AnalystResult], None]] = None,
        on_analyst_error: Optional[Callable[[str, str], None]] = None
    ):
        """
        Initialize the parallel executor.
        
        Args:
            timeout_seconds: Maximum time for each analyst
            on_analyst_start: Callback when analyst starts
            on_analyst_complete: Callback when analyst completes
            on_analyst_error: Callback when analyst fails
        """
        self.timeout_seconds = timeout_seconds
        self.on_analyst_start = on_analyst_start
        self.on_analyst_complete = on_analyst_complete
        self.on_analyst_error = on_analyst_error
    
    async def _execute_single_analyst(
        self,
        analyst: BaseAnalyst,
        query: str,
        execution: AnalystExecution
    ) -> AnalystExecution:
        """
        Execute a single analyst with error handling.
        
        Args:
            analyst: The analyst instance to execute
            query: The query to analyze
            execution: Execution tracking object
            
        Returns:
            Updated AnalystExecution with results
        """
        execution.status = ExecutionStatus.RUNNING
        execution.start_time = time.time()
        
        if self.on_analyst_start:
            self.on_analyst_start(analyst.name)
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                analyst.analyze_async(query),
                timeout=self.timeout_seconds
            )
            
            execution.end_time = time.time()
            execution.status = ExecutionStatus.COMPLETED
            execution.result = result
            
            if self.on_analyst_complete:
                self.on_analyst_complete(analyst.name, result)
                
        except asyncio.TimeoutError:
            execution.end_time = time.time()
            execution.status = ExecutionStatus.FAILED
            execution.error = f"Timeout after {self.timeout_seconds}s"
            
            if self.on_analyst_error:
                self.on_analyst_error(analyst.name, execution.error)
                
        except Exception as e:
            execution.end_time = time.time()
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            
            if self.on_analyst_error:
                self.on_analyst_error(analyst.name, execution.error)
        
        return execution
    
    async def execute_parallel(
        self,
        analysts: Dict[str, BaseAnalyst],
        queries: Dict[str, str]
    ) -> ParallelExecutionResult:
        """
        Execute multiple analysts in parallel.
        
        Args:
            analysts: Dictionary mapping analyst names to instances
            queries: Dictionary mapping analyst names to their queries
            
        Returns:
            ParallelExecutionResult: Aggregated results from all analysts
        """
        result = ParallelExecutionResult()
        start_time = time.time()
        
        # Initialize execution tracking for each analyst
        for name in analysts.keys():
            result.executions[name] = AnalystExecution(analyst_name=name)
        
        # Create tasks for parallel execution
        tasks = [
            self._execute_single_analyst(
                analyst=analysts[name],
                query=queries.get(name, ""),
                execution=result.executions[name]
            )
            for name in analysts.keys()
        ]
        
        # Execute all analysts in parallel
        await asyncio.gather(*tasks, return_exceptions=True)
        
        result.total_time_ms = (time.time() - start_time) * 1000
        
        return result
    
    def execute_parallel_sync(
        self,
        analysts: Dict[str, BaseAnalyst],
        queries: Dict[str, str]
    ) -> ParallelExecutionResult:
        """
        Synchronous wrapper for parallel execution.
        
        Useful when calling from synchronous code (e.g., Streamlit).
        
        Args:
            analysts: Dictionary mapping analyst names to instances
            queries: Dictionary mapping analyst names to their queries
            
        Returns:
            ParallelExecutionResult: Aggregated results from all analysts
        """
        return asyncio.run(self.execute_parallel(analysts, queries))


def create_progress_callbacks(status_container=None):
    """
    Create callback functions for progress tracking.
    
    Args:
        status_container: Optional Streamlit container for status updates
        
    Returns:
        Tuple of callback functions (on_start, on_complete, on_error)
    """
    def on_start(analyst_name: str):
        if status_container:
            status_container.write(f"🔄 Starting {analyst_name}...")
        else:
            print(f"🔄 Starting {analyst_name}...")
    
    def on_complete(analyst_name: str, result: AnalystResult):
        time_ms = result.execution_time_ms
        if status_container:
            status_container.write(f"✅ {analyst_name} completed ({time_ms:.0f}ms)")
        else:
            print(f"✅ {analyst_name} completed ({time_ms:.0f}ms)")
    
    def on_error(analyst_name: str, error: str):
        if status_container:
            status_container.write(f"❌ {analyst_name} failed: {error}")
        else:
            print(f"❌ {analyst_name} failed: {error}")
    
    return on_start, on_complete, on_error
