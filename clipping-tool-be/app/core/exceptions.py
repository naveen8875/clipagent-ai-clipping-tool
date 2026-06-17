"""
Custom Exceptions

Defines custom exception classes for the ClipAgent application.
"""

class ClipAgentException(Exception):
    """Base exception for ClipAgent application"""
    
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ProjectNotFoundException(ClipAgentException):
    """Raised when a project is not found"""
    
    def __init__(self, project_id: str):
        super().__init__(
            message=f"Project not found: {project_id}",
            status_code=404,
            details={"project_id": project_id}
        )


class ProjectAlreadyExistsException(ClipAgentException):
    """Raised when trying to create a project that already exists"""
    
    def __init__(self, project_id: str):
        super().__init__(
            message=f"Project already exists: {project_id}",
            status_code=409,
            details={"project_id": project_id}
        )


class InvalidFileException(ClipAgentException):
    """Raised when an uploaded file is invalid"""
    
    def __init__(self, filename: str, reason: str):
        super().__init__(
            message=f"Invalid file: {filename}",
            status_code=400,
            details={"filename": filename, "reason": reason}
        )


class ProcessingException(ClipAgentException):
    """Raised when video processing fails"""
    
    def __init__(self, project_id: str, step: int, reason: str):
        super().__init__(
            message=f"Processing failed at step {step}",
            status_code=500,
            details={"project_id": project_id, "step": step, "reason": reason}
        )


class LLMException(ClipAgentException):
    """Raised when LLM API call fails"""
    
    def __init__(self, provider: str, reason: str):
        super().__init__(
            message=f"LLM API error ({provider})",
            status_code=502,
            details={"provider": provider, "reason": reason}
        )


class VideoProcessingException(ClipAgentException):
    """Raised when FFmpeg video processing fails"""
    
    def __init__(self, reason: str):
        super().__init__(
            message="Video processing failed",
            status_code=500,
            details={"reason": reason}
        )


class ConfigurationException(ClipAgentException):
    """Raised when configuration is invalid"""
    
    def __init__(self, reason: str):
        super().__init__(
            message="Configuration error",
            status_code=500,
            details={"reason": reason}
        )

