# utils.py

import re
from better_profanity import profanity

def is_valid_name(name):
    """Check if the name contains only alphanumeric characters, spaces, and hyphens."""
    return bool(re.match(r'^[a-zA-Z0-9\s-]+$', name))

def is_meaningful(name):
    """Check if the name is not in a list of meaningless words."""
    meaningless_words = ['asdf', 'qwerty', 'zxcv', 'hjkl']
    return not any(word in name.lower() for word in meaningless_words)

def validate_name(name, check_profanity=True):
    """Validate a name for valid characters, meaningfulness, and optionally profanity."""
    if not is_valid_name(name):
        return False, "Name should only contain alphanumeric characters, spaces, and hyphens."
    
    if not is_meaningful(name):
        return False, "Please use a meaningful name."
    
    if check_profanity and profanity.contains_profanity(name):
        return False, "Name contains inappropriate language."
    
    return True, ""