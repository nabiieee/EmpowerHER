import pytest
from app.graph.empower_graph import run_match_workflow, _heuristic_intent


def test_heuristic_intent_parsing():
    """Test the heuristic intent parsing function."""
    message = "I'm a UX designer looking for remote work opportunities"
    result = _heuristic_intent(message)

    assert "goals" in result
    assert "skills" in result
    assert "industry_focus" in result
    assert "seniority" in result

    # Should detect UX/design skills
    assert any("ux" in skill.lower() or "design" in skill.lower() for skill in result["skills"])


def test_workflow_execution():
    """Test the complete workflow execution."""
    test_message = "I'm a woman returning to tech after a career break, interested in data science."

    result = run_match_workflow(test_message)

    # Check response structure
    assert "summary" in result
    assert "mentors" in result
    assert "jobs" in result
    assert "next_steps" in result

    # Check that mentors have required fields
    if result["mentors"]:
        mentor = result["mentors"][0]
        assert "name" in mentor
        assert "title" in mentor
        assert "match_reason" in mentor

    # Check that jobs have required fields
    if result["jobs"]:
        job = result["jobs"][0]
        assert "title" in job
        assert "company" in job
        assert "match_reason" in job

    # Check next steps
    assert isinstance(result["next_steps"], list)
    assert len(result["next_steps"]) > 0


def test_workflow_with_different_inputs():
    """Test workflow with various input types."""
    test_cases = [
        "I want to be a product manager",
        "Looking for frontend development mentors",
        "Backend engineer seeking career advice",
        "UX researcher interested in health tech"
    ]

    for message in test_cases:
        result = run_match_workflow(message)
        assert "summary" in result
        assert "mentors" in result
        assert "jobs" in result
        assert len(result["mentors"]) > 0 or len(result["jobs"]) > 0