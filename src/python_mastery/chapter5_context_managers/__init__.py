"""Chapter 5: Context Managers & Resource Lifecycle."""

from .atomic_transaction import AtomicTransaction
from .resource_pool import DynamicResourceStack, managed_resource

__all__ = ["AtomicTransaction", "managed_resource", "DynamicResourceStack"]
