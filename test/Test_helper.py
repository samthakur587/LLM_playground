# Define the test function
from ..helpers import *


def test_hello():
    # Call the function and get the result
    result = hello()

    expected_result = "Hello, World!"

    # Check if the result matches the expected result
    assert result == expected_result
