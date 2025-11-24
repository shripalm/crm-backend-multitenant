from contextvars import ContextVar

client_context: ContextVar[str] = ContextVar('client')