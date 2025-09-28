"""
Task Queue System for Parallel Processing
Handles concurrent request processing and resource management
"""
import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
import uuid

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    @property
    def execution_time(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

@dataclass
class Task:
    task_id: str
    func: Callable
    args: tuple
    kwargs: dict
    priority: int = 1
    max_retries: int = 3
    retry_count: int = 0
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

class TaskQueue:
    """
    Asynchronous task queue system for parallel processing
    """
    
    def __init__(self, max_workers: int = 10, max_queue_size: int = 100):
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.queue = asyncio.PriorityQueue(maxsize=max_queue_size)
        self.workers: List[asyncio.Task] = []
        self.results: Dict[str, TaskResult] = {}
        self.running_tasks: Dict[str, Task] = {}
        self.is_running = False
        
        # Semaphore for limiting concurrent workers
        self.semaphore = asyncio.Semaphore(max_workers)
        
        logger.info(f"TaskQueue initialized with {max_workers} workers and queue size {max_queue_size}")

    async def start(self):
        """Start the task queue workers"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
            
        logger.info(f"Started {len(self.workers)} workers")

    async def stop(self):
        """Stop the task queue workers"""
        if not self.is_running:
            return
            
        self.is_running = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        logger.info("Task queue stopped")

    async def add_task(
        self, 
        func: Callable, 
        *args, 
        priority: int = 1, 
        task_id: str = None,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """
        Add a task to the queue
        
        Args:
            func: Async function to execute
            *args: Function arguments
            priority: Task priority (lower numbers = higher priority)
            task_id: Optional custom task ID
            max_retries: Maximum retry attempts
            **kwargs: Function keyword arguments
            
        Returns:
            str: Task ID
        """
        if task_id is None:
            task_id = str(uuid.uuid4())
            
        task = Task(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            max_retries=max_retries
        )
        
        try:
            # Use priority as queue priority (lower number = higher priority)
            await self.queue.put((priority, time.time(), task))
            
            # Initialize result
            self.results[task_id] = TaskResult(
                task_id=task_id,
                status=TaskStatus.PENDING
            )
            
            logger.info(f"Task {task_id} added to queue with priority {priority}")
            return task_id
            
        except asyncio.QueueFull:
            logger.error(f"Queue is full, cannot add task {task_id}")
            raise Exception("Task queue is full")

    async def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Get task result by ID"""
        return self.results.get(task_id)

    async def wait_for_result(self, task_id: str, timeout: float = None) -> TaskResult:
        """Wait for task completion and return result"""
        start_time = time.time()
        
        while True:
            result = self.results.get(task_id)
            if result and result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                return result
                
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} timed out after {timeout} seconds")
                
            await asyncio.sleep(0.1)

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        return {
            "queue_size": self.queue.qsize(),
            "max_queue_size": self.max_queue_size,
            "running_tasks": len(self.running_tasks),
            "max_workers": self.max_workers,
            "total_results": len(self.results),
            "is_running": self.is_running,
            "completed_tasks": sum(1 for r in self.results.values() if r.status == TaskStatus.COMPLETED),
            "failed_tasks": sum(1 for r in self.results.values() if r.status == TaskStatus.FAILED)
        }

    async def _worker(self, worker_name: str):
        """Worker coroutine that processes tasks from the queue"""
        logger.info(f"Worker {worker_name} started")
        
        while self.is_running:
            try:
                # Get task from queue with timeout
                priority, timestamp, task = await asyncio.wait_for(
                    self.queue.get(), 
                    timeout=1.0
                )
                
                # Process the task
                await self._process_task(task, worker_name)
                
            except asyncio.TimeoutError:
                # No tasks available, continue
                continue
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_name} cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}", exc_info=True)
                
        logger.info(f"Worker {worker_name} stopped")

    async def _process_task(self, task: Task, worker_name: str):
        """Process a single task"""
        task_id = task.task_id
        
        # Update task status
        self.running_tasks[task_id] = task
        result = self.results[task_id]
        result.status = TaskStatus.RUNNING
        result.start_time = time.time()
        
        logger.info(f"Worker {worker_name} processing task {task_id}")
        
        try:
            # Execute the task with semaphore (resource limiting)
            async with self.semaphore:
                if asyncio.iscoroutinefunction(task.func):
                    result.result = await task.func(*task.args, **task.kwargs)
                else:
                    # Run sync function in thread pool
                    result.result = await asyncio.to_thread(task.func, *task.args, **task.kwargs)
            
            # Mark as completed
            result.status = TaskStatus.COMPLETED
            result.end_time = time.time()
            
            logger.info(f"Task {task_id} completed successfully in {result.execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}", exc_info=True)
            
            # Handle retries
            task.retry_count += 1
            if task.retry_count <= task.max_retries:
                logger.info(f"Retrying task {task_id} (attempt {task.retry_count}/{task.max_retries})")
                
                # Re-add to queue with lower priority
                await self.queue.put((task.priority + 10, time.time(), task))
                
                # Reset status to pending
                result.status = TaskStatus.PENDING
                result.start_time = None
            else:
                # Max retries exceeded
                result.status = TaskStatus.FAILED
                result.error = str(e)
                result.end_time = time.time()
                
        finally:
            # Remove from running tasks
            self.running_tasks.pop(task_id, None)

# Global task queue instance
task_queue = TaskQueue()

async def start_task_queue():
    """Start the global task queue"""
    await task_queue.start()

async def stop_task_queue():
    """Stop the global task queue"""
    await task_queue.stop()

async def submit_task(func: Callable, *args, priority: int = 1, **kwargs) -> str:
    """Submit a task to the global queue"""
    return await task_queue.add_task(func, *args, priority=priority, **kwargs)

async def get_task_result(task_id: str) -> Optional[TaskResult]:
    """Get task result from the global queue"""
    return await task_queue.get_result(task_id)

async def wait_for_task(task_id: str, timeout: float = None) -> TaskResult:
    """Wait for task completion from the global queue"""
    return await task_queue.wait_for_result(task_id, timeout)
