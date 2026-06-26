import os
import yaml
import pytest

@pytest.fixture
def profile_path():
    return "/home/tangleroot013/god_stack/stealth_profiles.yaml"

def test_stealth_profiles_exist(profile_path):
    """Verifies profile configuration mapping exists on the local desk filesystem."""
    assert os.path.exists(profile_path), "Primary runtime profile 'stealth_profiles.yaml' is missing."

def test_profile_structural_integrity(profile_path):
    """Validates structural fields inside user profile configurations."""
    if not os.path.exists(profile_path):
        pytest.skip("Profile target omitted. Skipping parser validation logic.")
        
    with open(profile_path, "r") as f:
        config = yaml.safe_load(f)
        
    assert "default_profile" in config, "Missing base 'default_profile' configuration payload block."
    assert "high_privacy_profile" in config, "Missing 'high_privacy_profile' matrix tracking configuration."
    
    # Assert signature keys map correctly
    default = config["default_profile"]
    assert "user_agent" in default
    assert "viewport" in default
    assert isinstance(default["viewport"], dict)
