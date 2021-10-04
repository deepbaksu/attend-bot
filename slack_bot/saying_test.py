from slack_bot import quotes


def test_no_duplicate_is_found_in_saying_yaml():
    seen_quotes = set()

    for quote in quotes:
        if quote not in seen_quotes:
            seen_quotes.add(quote)
        else:
            assert 0, f"중복된 명언이 발견되었습니다. {quote}를 제거해주세요."
