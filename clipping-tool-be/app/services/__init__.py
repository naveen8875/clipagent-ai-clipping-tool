"""
Services Package

Exports all service instances for easy importing.
"""

from app.services.project_service import project_service, ProjectService

__all__ = [
    "project_service",
    "ProjectService"
]
