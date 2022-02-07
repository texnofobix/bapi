import pytest

from bdantic import models
from datetime import date
from .search import FullTextSearch, search_accounts, search_directives


def test_index_entry():
    fts = FullTextSearch([])
    fts._index_entry(1, "some words", "data")

    assert fts._entries[1] == "data"
    assert fts._index["some"] == {1}
    assert fts._index["words"] == {1}


def test_search():
    index = [
        ("some words", "data1"),
        ("more words", "data2"),
        ("something else", "data3"),
    ]
    fts = FullTextSearch(index)

    expected = ["data1", "data2"]
    assert fts.search("words") == expected

    expected = ["data1"]
    assert fts.search("some") == expected

    expected = ["data2"]
    assert fts.search("more words") == expected

    expected = ["data3"]
    assert fts.search("something else")


@pytest.mark.parametrize(
    "query, expected",
    [
        ("a test string", ["a", "test", "string"]),
        ("a test string.", ["a", "test", "string"]),
        ("A TEST string", ["a", "test", "string"]),
    ],
)
def test_tokenize(query, expected):
    fts = FullTextSearch([])

    tokens = fts._tokenize(query)
    assert tokens == expected


def test_search_accounts():
    accounts = [
        "Assets:Test",
        "Assets:Bank:Test",
        "Expenses:Stuff",
        "Liabilities:Credit",
    ]

    fts = search_accounts(accounts)
    assert fts.search("Assets") == ["Assets:Test", "Assets:Bank:Test"]
    assert fts.search("Test") == ["Assets:Test", "Assets:Bank:Test"]
    assert fts.search("Stuff") == ["Expenses:Stuff"]
    assert fts.search("Liabilities") == ["Liabilities:Credit"]


def test_search_directives():
    # Close
    d = models.Close(
        date=date.today(),
        meta=None,
        account="Assets:Test",
    )
    fts = search_directives([d])
    assert fts.search("Assets:Test") == [d]
    assert fts.search("Assets") == []

    # Commodity
    d = models.Commodity(date=date.today(), meta=None, currency="USD")
    fts = search_directives([d])
    assert fts.search("USD") == [d]
    assert fts.search("CAD") == []

    # Document
    d = models.Document(
        date=date.today(),
        meta=None,
        account="Assets:Test",
        filename="test/file.jpg",
        tags={"tag1"},
        links={"link1"},
    )
    fts = search_directives([d])
    assert fts.search("Assets:Test") == [d]
    assert fts.search("file.jpg") == [d]
    assert fts.search("tag1") == [d]
    assert fts.search("link1") == [d]
    assert fts.search("link") == []

    # Event
    d = models.Event(
        date=date.today(),
        meta=None,
        type="test",
        description="some kind of event",
    )
    fts = search_directives([d])
    assert fts.search("test") == [d]
    assert fts.search("some kind") == [d]
    assert fts.search("events") == []

    # Note
    d = models.Note(
        date=date.today(),
        meta=None,
        account="Assets:Test",
        comment="A test comment",
    )
    fts = search_directives([d])
    assert fts.search("Assets:Test") == [d]
    assert fts.search("a test") == [d]
    assert fts.search("comments") == []

    # Open
    d = models.Open(
        date=date.today(),
        meta=None,
        account="Assets:Test",
        currencies=["USD", "CAD"],
    )
    fts = search_directives([d])
    assert fts.search("Assets:Test") == [d]
    assert fts.search("USD") == [d]
    assert fts.search("EUR") == []

    # Pad
    d = models.Pad(
        date=date.today(),
        meta=None,
        account="Assets:Test",
        source_account="Assets:Test1",
    )
    fts = search_directives([d])
    assert fts.search("Assets:Test") == [d]
    assert fts.search("Assets:Test1") == [d]
    assert fts.search("Assets") == []

    # Price
    d = models.Price(
        date=date.today(),
        meta=None,
        currency="USD",
        amount=models.Amount(number=None, currency=None),
    )
    fts = search_directives([d])
    assert fts.search("USD") == [d]
    assert fts.search("EUR") == []

    # Query
    d = models.Query(
        date=date.today(),
        meta=None,
        name="Test query",
        query_string="SELECT *",
    )
    fts = search_directives([d])
    assert fts.search("query") == [d]
    assert fts.search("SELECT") == [d]
    assert fts.search("queries") == []

    # Transaction
    d = models.Transaction(
        date=date.today(),
        meta=None,
        flag="*",
        payee="The Store",
        narration="Bought some things",
        links={"link1"},
        tags={"tag1"},
        postings=[],
    )
    fts = search_directives([d])
    assert fts.search("store") == [d]
    assert fts.search("things") == [d]
    assert fts.search("link1") == [d]
    assert fts.search("tag1") == [d]
    assert fts.search("Bought some more things") == []
