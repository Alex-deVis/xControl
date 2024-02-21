import time


def wait_for(condition: callable, timeout: float, interval: float = 0.1) -> bool:
    """Wait for a condition to be met, with a timeout."""
    assert callable(condition)
    assert isinstance(timeout, float) or isinstance(timeout, int)
    assert isinstance(interval, float) or isinstance(interval, int)

    start = time.time()
    while not condition():
        if time.time() - start > timeout:
            return False
        time.sleep(interval)
    return True


def wait_to_be_set(
    condition: callable, timeout: float, interval: float = 0.1
) -> object:
    """Wait for a condition value to be set, with a timeout."""

    assert callable(condition)
    assert isinstance(timeout, float) or isinstance(timeout, int)
    assert isinstance(interval, float) or isinstance(interval, int)

    result = condition()

    start = time.time()
    while result is None:
        if time.time() - start > timeout:
            break
        time.sleep(interval)
        result = condition()
    return result
