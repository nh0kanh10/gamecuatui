"""
Content Moderation - Simple keyword-based + future LLM moderation
"""

import re
from typing import Tuple

# Simple keyword blacklist (Vietnamese + English)
BLACKLIST_KEYWORDS = [
    # Violence
    "giết", "sát", "máu", "chết", "tử vong",
    "kill", "murder", "death", "blood",
    
    # Sexual content (basic)
    "hiếp", "dâm", "sex", "porn",
    
    # Hate speech
    "đồ chó", "đồ ngu", "fuck", "shit",
    
    # Add more as needed
]

# Patterns to detect prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+previous",
    r"forget\s+all",
    r"new\s+instructions",
    r"system\s+prompt",
    r"you\s+are\s+now",
    r"role:\s*",
    r"assistant:\s*",
    r"user:\s*",
]


def simple_moderate(text: str) -> Tuple[bool, str]:
    """
    Simple keyword-based moderation
    Returns: (is_safe, reason)
    """
    if not text:
        return True, ""
    
    text_lower = text.lower()
    
    # Check blacklist
    for keyword in BLACKLIST_KEYWORDS:
        if keyword in text_lower:
            return False, f"Contains blacklisted keyword: {keyword}"
    
    # Check injection patterns
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False, f"Potential prompt injection detected"
    
    return True, ""


def moderate_content(text: str, strict: bool = False) -> Tuple[bool, str]:
    """
    Moderate content - main entry point
    strict: If True, use stricter rules
    
    Returns: (is_safe, reason)
    """
    if not text:
        return True, ""
    
    # Basic moderation
    is_safe, reason = simple_moderate(text)
    
    if not is_safe:
        return False, reason
    
    # Future: Add LLM-based moderation
    # if strict:
    #     return llm_moderate(text)
    
    return True, ""


def is_safe_content(text: str) -> bool:
    """Quick check if content is safe"""
    is_safe, _ = moderate_content(text)
    return is_safe


def sanitize_content(text: str) -> str:
    """
    Sanitize content by removing unsafe parts
    Returns sanitized text
    """
    if not text:
        return ""
    
    is_safe, _ = moderate_content(text)
    if is_safe:
        return text
    
    # Remove blacklisted keywords
    text_lower = text.lower()
    sanitized = text
    
    for keyword in BLACKLIST_KEYWORDS:
        if keyword in text_lower:
            # Replace with placeholder
            sanitized = re.sub(
                re.escape(keyword),
                "[filtered]",
                sanitized,
                flags=re.IGNORECASE
            )
    
    return sanitized

