def check_authenticity(content: str) -> bool:
    """
    Mock plagiarism/AI detection check.
    """
    return "plagiarism" not in content.lower()
