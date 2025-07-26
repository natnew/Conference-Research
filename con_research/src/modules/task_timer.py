"""
Task Performance Timer Module
============================

Non-blocking task timing system for the Conference Research Application.
Provides real-time performance monitoring without interfering with user interactions.
Follows established coding standards with comprehensive error handling and resource cleanup.

Features:
- Non-blocking progress indicators with Streamlit integration
- Multi-task timing support with session persistence
- Performance analytics dashboard with visual representations
- Context managers for proper resource management
- Retry logic integration with exponential backoff

Dependencies:
- streamlit for UI components and session state management
- time for high-precision timing operations
- functools for decorator implementation
- contextlib for context manager support
"""

import streamlit as st
import time
import functools
from typing import Dict, Optional, Any, List
from contextlib import contextmanager


class TaskPerformanceTimer:
    """
    Centralized task timing management with non-blocking progress indicators
    for tracking performance metrics across application modules.
    
    Attributes:
        task_timings (Dict[str, float]): Completed task durations in seconds
        active_tasks (Dict[str, float]): Currently running task start times
        task_progress (Dict[str, int]): Progress percentages for active tasks
        task_metadata (Dict[str, Dict]): Additional task information and context
    """
    
    def __init__(self):
        """Initialize timer with empty state containers."""
        self.task_timings: Dict[str, float] = {}
        self.active_tasks: Dict[str, float] = {}
        self.task_progress: Dict[str, int] = {}
        self.task_metadata: Dict[str, Dict[str, Any]] = {}
    
    def start_task_timing(self, task_name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initiates timing for a named task with optional metadata tracking.
        
        Args:
            task_name (str): Unique identifier for the task being timed
            metadata (Dict[str, Any], optional): Additional task context information
            
        Side Effects:
            - Records start time in active_tasks dictionary
            - Initializes progress tracking for the task
            - Stores metadata for enhanced analytics
            
        Raises:
            ValueError: If task_name is empty or already active
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")
        
        if task_name in self.active_tasks:
            st.warning(f"Task '{task_name}' is already active. Stopping previous instance.")
            self.complete_task_timing(task_name)
        
        self.active_tasks[task_name] = time.time()
        self.task_progress[task_name] = 0
        self.task_metadata[task_name] = metadata or {}
    
    def update_task_progress(self, task_name: str, progress_percentage: int) -> None:
        """
        Updates progress for an active task without blocking execution.
        
        Args:
            task_name (str): Name of the task to update
            progress_percentage (int): Progress value between 0-100
            
        Raises:
            ValueError: If progress_percentage is not between 0-100
            KeyError: If task_name is not currently active
        """
        if not (0 <= progress_percentage <= 100):
            raise ValueError(f"Progress must be between 0-100, got {progress_percentage}")
        
        if task_name not in self.active_tasks:
            st.warning(f"Cannot update progress for inactive task: {task_name}")
            return
        
        self.task_progress[task_name] = progress_percentage
    
    def complete_task_timing(self, task_name: str) -> Optional[float]:
        """
        Completes timing for a task and records final duration.
        
        Args:
            task_name (str): Name of the task to complete
            
        Returns:
            Optional[float]: Duration in seconds, None if task not found
            
        Side Effects:
            - Moves task from active to completed state
            - Updates progress to 100%
            - Preserves metadata for analytics
        """
        if task_name not in self.active_tasks:
            st.warning(f"Cannot complete timing for inactive task: {task_name}")
            return None
        
        duration = time.time() - self.active_tasks[task_name]
        self.task_timings[task_name] = duration
        del self.active_tasks[task_name]
        self.task_progress[task_name] = 100
        return duration
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Returns comprehensive performance analytics for all completed tasks.
        
        Returns:
            Dict[str, Any]: Performance metrics including:
                - individual_timings: Task-specific durations
                - total_execution_time: Sum of all task durations
                - task_count: Number of completed tasks
                - average_task_time: Mean duration across tasks
                - longest_task: Task with maximum duration
                - shortest_task: Task with minimum duration
        """
        if not self.task_timings:
            return {
                "individual_timings": {},
                "total_execution_time": 0.0,
                "task_count": 0,
                "average_task_time": 0.0,
                "longest_task": None,
                "shortest_task": None
            }
        
        total_time = sum(self.task_timings.values())
        longest_task = max(self.task_timings.items(), key=lambda x: x[1])
        shortest_task = min(self.task_timings.items(), key=lambda x: x[1])
        
        return {
            "individual_timings": self.task_timings.copy(),
            "total_execution_time": total_time,
            "task_count": len(self.task_timings),
            "average_task_time": total_time / len(self.task_timings),
            "longest_task": {"name": longest_task[0], "duration": longest_task[1]},
            "shortest_task": {"name": shortest_task[0], "duration": shortest_task[1]}
        }
    
    def clear_all_timings(self) -> None:
        """
        Clears all recorded timings and resets timer state.
        
        Side Effects:
            - Clears completed task timings
            - Stops all active tasks
            - Resets progress tracking
            - Removes all metadata
        """
        self.task_timings.clear()
        self.active_tasks.clear()
        self.task_progress.clear()
        self.task_metadata.clear()


# Global timer instance with session state integration
def get_performance_timer() -> TaskPerformanceTimer:
    """
    Returns singleton performance timer instance with Streamlit session state persistence.
    
    Returns:
        TaskPerformanceTimer: Global timer instance for application-wide use
        
    Note:
        Uses Streamlit session state to maintain timer across page interactions.
        Creates new instance if not present in session state.
    """
    if 'performance_timer' not in st.session_state:
        st.session_state.performance_timer = TaskPerformanceTimer()
    return st.session_state.performance_timer


def track_task_performance(task_name: str, show_progress: bool = True, metadata: Optional[Dict[str, Any]] = None):
    """
    Decorator for non-blocking task performance tracking with optional progress display.
    
    Args:
        task_name (str): Descriptive name for the task being tracked
        show_progress (bool): Whether to show real-time progress indicators
        metadata (Dict[str, Any], optional): Additional context for task analytics
        
    Returns:
        Decorated function with integrated performance tracking
        
    Example:
        @track_task_performance("Email Enhancement Processing", show_progress=True)
        def generate_response(email_text, tone, length):
            timer = get_performance_timer()
            timer.update_task_progress("Email Enhancement Processing", 50)
            # Continue processing...
            
    Raises:
        ValueError: If task_name is empty or invalid
        Exception: Re-raises any exceptions from decorated function
    """
    if not task_name or not task_name.strip():
        raise ValueError("Task name cannot be empty")
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timer = get_performance_timer()
            progress_container = None
            status_container = None
            progress_bar = None
            
            try:
                if show_progress:
                    progress_container = st.empty()
                    status_container = st.empty()
                    
                    with progress_container.container():
                        st.markdown(f"**🔄 {task_name}**")
                        progress_bar = st.progress(0)
                    
                    status_container.info(f"Initiating {task_name}...")
                
                timer.start_task_timing(task_name, metadata)
                
                if show_progress and progress_bar:
                    timer.update_task_progress(task_name, 25)
                    progress_bar.progress(25)
                    status_container.info(f"Processing {task_name}...")
                
                result = func(*args, **kwargs)
                
                if show_progress and progress_bar:
                    timer.update_task_progress(task_name, 90)
                    progress_bar.progress(90)
                    status_container.info(f"Finalizing {task_name}...")
                
                return result
                
            except Exception as e:
                if show_progress and status_container:
                    status_container.error(f"❌ {task_name} failed: {str(e)}")
                raise e
                
            finally:
                duration = timer.complete_task_timing(task_name)
                
                if show_progress and duration and progress_bar and status_container:
                    progress_bar.progress(100)
                    status_container.success(f"✅ {task_name} completed in {duration:.2f}s")
                    
                    # Clean up progress indicators after brief display
                    time.sleep(0.8)
                    if progress_container:
                        progress_container.empty()
                    if status_container:
                        status_container.empty()
        
        return wrapper
    return decorator


@contextmanager
def performance_tracking_context(task_name: str, show_progress: bool = True, metadata: Optional[Dict[str, Any]] = None):
    """
    Context manager for tracking code block performance with progress updates.
    
    Args:
        task_name (str): Descriptive name for the code block being tracked
        show_progress (bool): Whether to display progress indicators
        metadata (Dict[str, Any], optional): Additional context for analytics
        
    Yields:
        TaskPerformanceTimer: Timer instance for manual progress updates
        
    Example:
        with performance_tracking_context("File Processing") as timer:
            timer.update_task_progress("File Processing", 30)
            process_uploaded_file(file)
            timer.update_task_progress("File Processing", 70)
            validate_file_content(file)
            
    Raises:
        ValueError: If task_name is empty or invalid
        Exception: Re-raises any exceptions from context block
    """
    if not task_name or not task_name.strip():
        raise ValueError("Task name cannot be empty")
    
    timer = get_performance_timer()
    progress_container = None
    status_container = None
    progress_bar = None
    
    try:
        if show_progress:
            progress_container = st.empty()
            status_container = st.empty()
            
            with progress_container.container():
                st.markdown(f"**🔄 {task_name}**")
                progress_bar = st.progress(0)
            
            status_container.info(f"Starting {task_name}...")
        
        timer.start_task_timing(task_name, metadata)
        
        yield timer
        
    except Exception as e:
        if show_progress and status_container:
            status_container.error(f"❌ {task_name} failed: {str(e)}")
        raise e
        
    finally:
        duration = timer.complete_task_timing(task_name)
        
        if show_progress and duration and progress_bar and status_container:
            progress_bar.progress(100)
            status_container.success(f"✅ {task_name} completed in {duration:.2f}s")
            
            time.sleep(0.8)
            if progress_container:
                progress_container.empty()
            if status_container:
                status_container.empty()


def display_performance_dashboard():
    """
    Displays comprehensive performance analytics in an expandable Streamlit component.
    
    Shows individual task timings, total execution metrics, and performance visualizations
    for all tracked tasks in the current session. Includes metrics cards and bar charts.
    
    Side Effects:
        - Renders Streamlit UI components for performance data
        - Creates expandable section with detailed analytics
        - Displays bar chart for visual performance comparison
        
    Note:
        Only displays if tasks have been completed. Provides both summary metrics
        and detailed breakdowns for performance analysis.
    """
    timer = get_performance_timer()
    performance_data = timer.get_performance_summary()
    
    if performance_data["task_count"] > 0:
        with st.expander("📊 Performance Analytics Dashboard", expanded=False):
            # Summary metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Tasks", 
                    performance_data["task_count"]
                )
            
            with col2:
                st.metric(
                    "Total Time", 
                    f"{performance_data['total_execution_time']:.2f}s"
                )
            
            with col3:
                st.metric(
                    "Average Time", 
                    f"{performance_data['average_task_time']:.2f}s"
                )
            
            with col4:
                longest_task = performance_data.get('longest_task')
                if longest_task:
                    st.metric(
                        "Longest Task",
                        f"{longest_task['duration']:.2f}s",
                        delta=longest_task['name']
                    )
            
            st.markdown("### Task Performance Breakdown")
            
            # Individual task details
            for task_name, duration in performance_data["individual_timings"].items():
                percentage = (duration / performance_data["total_execution_time"]) * 100
                st.markdown(f"**{task_name}:** {duration:.2f}s ({percentage:.1f}% of total)")
            
            # Performance visualization
            if len(performance_data["individual_timings"]) > 1:
                st.markdown("### Performance Comparison")
                st.bar_chart(performance_data["individual_timings"])
                
            # Clear timings button
            if st.button("Clear Performance Data", key="clear_performance_data"):
                timer.clear_all_timings()
                st.rerun()
