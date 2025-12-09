import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_project_translator import main


def test_format_question_for_output_empty():
    """Test formatting empty question."""
    result = main.format_question_for_output("")
    assert result == ""


def test_format_question_for_output_none():
    """Test formatting None question."""
    result = main.format_question_for_output(None)
    assert result == ""


def test_format_question_for_output_with_period():
    """Test formatting question that already ends with a period."""
    question = "Can you help me with this code."
    result = main.format_question_for_output(question)
    assert result == question  # Should not add another period


def test_format_question_for_output_with_question_mark():
    """Test formatting question that ends with a question mark."""
    question = "What is wrong with this function?"
    result = main.format_question_for_output(question)
    assert result == question  # Should keep the question mark


def test_format_question_for_output_with_exclamation():
    """Test formatting question that ends with an exclamation."""
    question = "This code needs urgent help!"
    result = main.format_question_for_output(question)
    assert result == question  # Should keep the exclamation


def test_format_question_for_output_with_colon():
    """Test formatting question that ends with a colon."""
    question = "Here's my problem:"
    result = main.format_question_for_output(question)
    assert result == question  # Should keep the colon


def test_format_question_for_output_no_punctuation():
    """Test formatting question without ending punctuation."""
    question = "Can you refactor this code"
    result = main.format_question_for_output(question)
    assert result == "Can you refactor this code."  # Should add period


def test_format_question_for_output_extra_whitespace():
    """Test formatting question with extra whitespace."""
    question = "  Can you help me?  \n\n  "
    result = main.format_question_for_output(question)
    assert result == "Can you help me?"  # Should trim whitespace


def test_format_question_for_output_multiline():
    """Test formatting multiline question."""
    question = "First line\nSecond line\nThird line?"
    result = main.format_question_for_output(question)
    assert result == "First line\nSecond line\nThird line?"  # Should preserve newlines


def test_format_question_for_output_leading_trailing_newlines():
    """Test formatting question with leading/trailing newlines."""
    question = "\n\nCan you help?\n\n"
    result = main.format_question_for_output(question)
    assert result == "Can you help?"  # Should trim newlines


def test_format_question_for_output_with_extra_spaces():
    """Test formatting question with extra internal spaces."""
    question = "Can  you   help    me?"
    result = main.format_question_for_output(question)
    # Should preserve internal spaces as they might be intentional
    assert result == question
