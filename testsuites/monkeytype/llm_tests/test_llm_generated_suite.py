import pytest
from monkeytype import trace
from monkeytype.config import get_default_config
from monkeytype.tracing import CallTraceLogger, CallTrace
from monkeytype.exceptions import MonkeyTypeError
from unittest.mock import MagicMock

@pytest.fixture
def mock_logger():
    logger = MagicMock(spec=CallTraceLogger)
    return logger

def test_trace_calls_with_default_config(mock_logger):
    config = get_default_config()
    with trace(config):
        assert mock_logger is not None

def test_call_trace_initialization():
    func = lambda x: x
    arg_types = {'x': int}
    return_type = str
    yield_type = None

    trace = CallTrace(func, arg_types, return_type, yield_type)
    assert trace.func == func
    assert trace.arg_types == arg_types
    assert trace.return_type == return_type
    assert trace.yield_type == yield_type

def test_call_trace_equality():
    func = lambda x: x
    arg_types = {'x': int}
    return_type = str
    yield_type = None

    trace1 = CallTrace(func, arg_types, return_type, yield_type)
    trace2 = CallTrace(func, arg_types, return_type, yield_type)

    assert trace1 == trace2

def test_call_trace_inequality():
    func1 = lambda x: x
    func2 = lambda y: y
    arg_types1 = {'x': int}
    arg_types2 = {'y': str}
    return_type = str
    yield_type = None

    trace1 = CallTrace(func1, arg_types1, return_type, yield_type)
    trace2 = CallTrace(func2, arg_types2, return_type, yield_type)

    assert trace1 != trace2

def test_call_trace_logger_logging(mock_logger):
    func = lambda x: x
    arg_types = {'x': int}
    return_type = str
    yield_type = None

    trace = CallTrace(func, arg_types, return_type, yield_type)
    mock_logger.log(trace)

    mock_logger.log.assert_called_once_with(trace)

def test_call_trace_logger_flush(mock_logger):
    mock_logger.flush()
    mock_logger.flush.assert_called_once()

def test_invalid_type_error():
    with pytest.raises(MonkeyTypeError):
        raise MonkeyTypeError("This is a test error.")

def test_get_default_config():
    config = get_default_config()
    assert config is not None
    assert hasattr(config, 'trace_store')
    assert hasattr(config, 'trace_logger')
