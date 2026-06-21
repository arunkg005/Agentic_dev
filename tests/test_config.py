import pytest
from unittest.mock import patch
import config

def test_call_llm_primary_success():
    with patch("config._call_gemini", return_value="success output") as mock_gemini:
        res = config.call_llm("test prompt", api_key="testkey", json_output=False, provider="Gemini (Google)")
        assert res == "success output"
        mock_gemini.assert_called_once()

def test_call_llm_fallback_to_groq_when_gemini_fails():
    def mock_gemini_fail(*args, **kwargs):
        raise ValueError("Gemini limit reached")

    with patch("config._call_gemini", side_effect=mock_gemini_fail):
        with patch("config._call_groq", return_value="groq success output") as mock_groq:
            # Provide both keys so fallback is triggered
            with patch("config.GEMINI_API_KEY", "primary_key"), patch("config.GROQ_API_KEY", "fallback_key"):
                res = config.call_llm("test prompt", api_key=None, json_output=False, provider="Gemini (Google)")
                assert res == "groq success output"
                mock_groq.assert_called_once()
