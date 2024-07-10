import re
from typing import Optional, Callable


def is_empty_or_whitespace(s):
    return s.strip() == ""


def search_in_str(s: str, pattern: str, regex: bool, on_match: Optional[Callable[[re.Match], str]] = None,
                  on_non_match: Optional[Callable[[str], str]] = None) -> str:
    if regex:
        return split_map_join(s, pattern, on_match, on_non_match)
    else:
        pattern = re.escape(pattern)
        return split_map_join(s, pattern, on_match, on_non_match)


def split_map_join(s: str, pattern: str, on_match: Optional[Callable[[re.Match], str]] = None,
                   on_non_match: Optional[Callable[[str], str]] = None) -> str:
    """
    Splits the string, converts its parts, and combines them into a new string.

    The pattern is used to split the string into parts and separating matches.
    Each match of re.finditer(pattern, s) on this string is used as a match,
    and the substrings between the end of one match (or the start of the string)
    and the start of the next match (or the end of the string) is treated as a
    non-matched part.

    Each match is converted to a string by calling on_match. If on_match
    is omitted, the matched substring is used.

    Each non-matched part is converted to a string by a call to on_non_match.
    If on_non_match is omitted, the non-matching substring itself is used.

    Then all the converted parts are concatenated into the resulting string.

    Example:
        result = split_map_join('Eats shoots leaves', r'shoots', on_match=lambda m: m.group(0), on_non_match=lambda n: '*')
        print(result)  # *shoots*
    """
    try:
        matches = list(re.finditer(pattern, s))
    except Exception as e:
        raise e
    parts = []
    last_end = 0

    for match in matches:
        # Add the non-matched part
        non_matched_part = s[last_end:match.start()]
        if on_non_match:
            parts.append(on_non_match(non_matched_part))
        else:
            parts.append(non_matched_part)

        # Add the matched part
        if on_match:
            parts.append(on_match(match))
        else:
            parts.append(match.group(0))

        last_end = match.end()

    # Add the last non-matched part
    non_matched_part = s[last_end:]
    if on_non_match:
        parts.append(on_non_match(non_matched_part))
    else:
        parts.append(non_matched_part)

    return ''.join(parts)
