from slack_bot import Quote


def test_quote():
    quote = Quote(quote="a yo quote hey", author="Author here", title="Title Here")
    assert (
        quote.to_message()
        == f"""a yo quote hey
- Author here, Title Here"""
    )
