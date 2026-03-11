class PlatformError(Exception):
    retryable: bool = False


class AgentError(PlatformError):
    pass


class AgentTimeoutError(AgentError):
    retryable = True


class CapabilityNotFoundError(PlatformError):
    pass


class ToolError(PlatformError):
    retryable = True


class LLMError(PlatformError):
    retryable = True


class LLMRateLimitError(LLMError):
    retryable = True


class ValidationError(PlatformError):
    pass


class AuthenticationError(PlatformError):
    pass
