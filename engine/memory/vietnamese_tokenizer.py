"""
Vietnamese Tokenizer for FTS5
Uses underthesea or simple Vietnamese word segmentation
"""

import re
from typing import List

try:
    from underthesea import word_tokenize
    HAS_UNDERTHESEA = True
except ImportError:
    HAS_UNDERTHESEA = False


def tokenize_vietnamese(text: str) -> str:
    """
    Tokenize Vietnamese text for FTS5 indexing
    Returns space-separated tokens
    """
    if not text:
        return ""
    
    # Normalize Unicode (NFC)
    text = text.strip()
    
    # Remove zero-width characters
    text = ''.join(char for char in text if ord(char) >= 32)
    
    # Try to use underthesea if available
    if HAS_UNDERTHESEA:
        try:
            tokens = word_tokenize(text)
            return ' '.join(tokens)
        except Exception:
            pass
    
    # Fallback: Simple tokenization
    # Split by spaces and punctuation
    tokens = re.findall(r'\b\w+\b', text.lower())
    return ' '.join(tokens)


def normalize_vietnamese(text: str) -> str:
    """
    Normalize Vietnamese text (remove diacritics for search)
    """
    # Remove diacritics mapping
    vietnamese_map = {
        'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
        'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
        'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
        'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
        'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
        'đ': 'd',
    }
    
    result = []
    for char in text.lower():
        result.append(vietnamese_map.get(char, char))
    
    return ''.join(result)

