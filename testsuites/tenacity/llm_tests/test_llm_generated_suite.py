import pytest
from tenacity import retry_if_exception, RetryError, stop_after_attempt, wait_fixed
import time

# Sample function to be tested
def unreliable_function(attempts):
    if attempts < 3:
        raise ValueError("Temporary failure")
    return "Success"

# Retry configuration
retry_strategy = retry_if_exception(lambda e: isinstance(e, ValueError))
stop_strategy = stop_after_attempt(5)
wait_strategy = wait_fixed(1)

@pytest.mark.parametrize("attempts, expected", [
    (1, "Temporary failure"),
    (2, "Temporary failure"),
    (3, "Success"),
])
def test_unreliable_function(attempts, expected):
    if attempts < 3:
        with pytest.raises(ValueError) as excinfo:
            unreliable_function(attempts)
        assert str(excinfo.value) == "Temporary failure"
    else:
        result = unreliable_function(attempts)
        assert result == "Success"

@pytest.mark.parametrize("attempts", [1, 2, 3, 4, 5])
def test_retry_on_failure(attempts):
    retries = 0
    while retries < 5:
        try:
            result = unreliable_function(attempts)
            assert result == "Success"
            break
        except ValueError:
            retries += 1
            time.sleep(1)  # Simulate wait between retries
    else:
        assert retries == 5  # Should fail after 5 attempts

def test_retry_error():
    with pytest.raises(ValueError):
        for _ in range(5):
            unreliable_function(1)  # Always raises ValueError
