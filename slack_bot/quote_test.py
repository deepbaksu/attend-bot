from slack_bot import Quote
from slack_bot.quote import load_quotes


def test_quote():
    quote = Quote(quote="a yo quote hey", author="Author here", title="Title Here")
    assert (
        quote.to_message()
        == f"""a yo quote hey
- Author here, Title Here"""
    )


def test_load_quotes():
    quotes = load_quotes()
    assert len(quotes) > 0

    q = quotes[0]
    assert q.quote != ""
    assert q.author != ""
