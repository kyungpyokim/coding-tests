from unittest.mock import MagicMock

import pytest

from ai_practice.level2_state.retry_policy import retry_with_backoff


class TransientAPIError(Exception):
    """Simulated transient network or rate limit error."""


@pytest.mark.unit
class TestRetryPolicy:
    def test_successful_call_on_first_try(self):
        mock_func = MagicMock(return_value="success")
        decorated = retry_with_backoff(max_retries=3, initial_delay=0.01)(mock_func)

        result = decorated("arg1")
        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_and_eventual_success(self):
        mock_func = MagicMock(
            side_effect=[TransientAPIError("Rate limited"), "recovered!"]
        )
        decorated = retry_with_backoff(
            max_retries=3,
            initial_delay=0.01,
            retryable_exceptions=(TransientAPIError,),
        )(mock_func)

        result = decorated()
        assert result == "recovered!"
        assert mock_func.call_count == 2

    def test_max_retries_exceeded_raises_error(self):
        mock_func = MagicMock(side_effect=TransientAPIError("Persistent 503 error"))
        decorated = retry_with_backoff(
            max_retries=2,
            initial_delay=0.01,
            retryable_exceptions=(TransientAPIError,),
        )(mock_func)

        with pytest.raises(TransientAPIError, match="Persistent 503"):
            decorated()

        # 1 initial attempt + 2 retries = 3 total calls
        assert mock_func.call_count == 3
