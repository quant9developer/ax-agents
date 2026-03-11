from enterprise_ai_platform.core.capability_registry import CapabilityRegistry


def test_registry_has_required_capabilities() -> None:
    from enterprise_ai_platform.agents import unit  # noqa: F401

    capabilities = CapabilityRegistry.list_capabilities()
    assert "summarization" in capabilities
    assert "classification" in capabilities
    assert "translation" in capabilities
