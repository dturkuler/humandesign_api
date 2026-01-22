from humandesign.utils.version import get_version

def test_get_version():
    """Test getting version from pyproject.toml."""
    version = get_version()
    assert version == "3.3.2"
