import json

from wikiplant.schemas import validate_paragraph
from wikiplant.structured import flatten_infobox, selected, title_from_url, to_paragraphs

SECTIONS = json.dumps([
    {"type": "section", "name": "Abstract", "has_parts": [
        {"type": "paragraph", "value": "Marlow Junction was a railway station in Lancashire, England, opened in 1851.",
         "links": [{"url": "https://en.wikipedia.org/wiki/Lancashire", "text": "Lancashire"},
                   {"url": "https://en.wikipedia.org/wiki/Marlow_Junction#cite_note-1"},
                   {"url": "https://en.wikipedia.org/wiki/File:Station.jpg"}]}]},
    {"type": "section", "name": "History", "has_parts": [
        {"type": "paragraph", "value": "The booking hall was rebuilt in 1887 after a fire destroyed it.",
         "links": [{"url": "https://en.wikipedia.org/wiki/Booking_hall%2C_rebuilt", "text": "booking hall"}]},
        {"type": "paragraph", "value": "Short"},
        {"type": "section", "name": "Closure", "has_parts": [
            {"type": "paragraph", "value": "Passenger services ended in 1964 and the goods yard closed in 1971."}]}]},
    {"type": "section", "name": "References", "has_parts": [
        {"type": "paragraph", "value": "Smith, J. (1920). Railways of the valley. London."}]},
])


def test_to_paragraphs_keeps_tree_links_and_drops_boilerplate():
    paras = to_paragraphs(7, "Marlow Junction", SECTIONS)
    assert [p["para_id"] for p in paras] == ["7::0", "7:History:0", "7:History/Closure:0"]
    assert paras[0]["outlinks"] == ["Lancashire"]
    assert paras[1]["outlinks"] == ["Booking hall, rebuilt"]
    assert all(validate_paragraph(p) == [] for p in paras)


def test_title_from_url():
    assert title_from_url("https://en.wikipedia.org/wiki/St_Helens%2C_Merseyside#History") == "St Helens, Merseyside"
    assert title_from_url("https://en.wikipedia.org/wiki/Category:Railways") is None
    assert title_from_url("https://example.com/x") is None


def test_flatten_infobox():
    raw = json.dumps([{"type": "infobox", "has_parts": [{"type": "section", "has_parts": [
        {"type": "field", "name": "Opened", "value": "1851"}, {"type": "field", "name": "Closed", "value": "1964"}]}]}])
    assert flatten_infobox(raw) == {"Opened": "1851", "Closed": "1964"}
    assert flatten_infobox(None) == {}


def test_domain_filter():
    assert selected("Marlow Junction railway station", "A former railway station in Lancashire, England.", "uk_industry")
    assert selected("Kersal", "Kersal is a village in Salford, Greater Manchester, England.", "uk_industry")
    assert not selected("Broadmarsh, Tasmania", "Broadmarsh is a town in Tasmania with a British railway.", "uk_industry")
    assert not selected("Darlington (disambiguation)", "Darlington may refer to: a town in England", "uk_industry")
    assert not selected("Paris", "Paris is the capital of France.", "uk_industry")
