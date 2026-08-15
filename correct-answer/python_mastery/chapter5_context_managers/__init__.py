"""Chapter 5: Context Managers & Resource Lifecycle (Reference Solution)."""

from .atomic_transaction import AtomicTransaction
from .resource_pool import DynamicResourceStack, MockResource, managed_resource

__all__ = [
    "AtomicTransaction",
    "MockResource",
    "managed_resource",
    "DynamicResourceStack",
]
