"""
Test using mimesis with pytest for automatic test data
"""
import pytest


def name_to_upper(name: str):
    return name.upper()


@pytest.mark.parametrize("mimesis_locale", ["de", "nl", "uk"])
@pytest.mark.repeat(3)
def test_name_to_upper(mimesis, mimesis_locale):
    """
    This test case uses generated data and will run 3 times for each locale.
    """
    name = mimesis("full_name")
    assert name_to_upper(name) == name.upper()
