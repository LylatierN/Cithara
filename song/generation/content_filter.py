from better_profanity import profanity
from dataclasses import dataclass
from typing import Optional


@dataclass
class FilterResult:
    passed: bool
    reason: Optional[str] = None


WHITELISTED_WORDS = [
    # Mild exclamations
    'damn',
    'dammit',
    'hell',
    'heck',
    'crap',
    'shoot',
    'dang',
    'fuck',
    'darn',

    # Body-related but commonly used casually
    'ass',
    'butt',
    'boobs',
    'piss',
    'pissed',

    # Commonly used in music/song lyrics casually
    'sexy',
    'hot',
    'drunk',
    'wasted',
    'stoned',
    'booze',
    'beer',
    'hungover',
]


class ContentFilter:
    def __init__(self):
        profanity.load_censor_words(whitelist_words=WHITELISTED_WORDS)

    def check(self, text: str) -> FilterResult:
        if profanity.contains_profanity(text):
            return FilterResult(
                passed=False,
                reason='Content contains offensive material.'
            )
        return FilterResult(passed=True)

    def check_prompt(self, prompt) -> FilterResult:
        combined = " ".join([
            prompt.title,
            prompt.occasion,
            prompt.lyrics,
        ])
        return self.check(combined)
