from lib.parser import parse_chat_text

SAMPLE = """[19/07/17, 9:07:11 PM] Sid: This is better😂😂
[19/07/17, 9:45:38 PM] Anisha: 😂
[19/07/17, 10:38:13 PM] Anisha: I am never gonna be free, might be on discount sometime, but mostly fresh..
[19/07/17, 10:38:19 PM] Anisha: I hope u get this joke
[20/07/17, 7:05:01 AM] Anisha: Really?
Well maybe..
‎[19/07/17, 11:36:32 PM] Sid: ‎image omitted
"""

def test_basic_parse():
    msgs = parse_chat_text(SAMPLE)
    assert len(msgs) == 6
    assert msgs[0].sender == "Sid"
    assert msgs[0].text == "This is better😂😂"
    assert msgs[0].ts.year == 2017 and msgs[0].ts.month == 7 and msgs[0].ts.day == 19

def test_multiline_continuation():
    msgs = parse_chat_text(SAMPLE)
    assert msgs[4].text == "Really?\nWell maybe.."

def test_media_classification():
    msgs = parse_chat_text(SAMPLE)
    assert msgs[5].is_media is True
    assert msgs[5].media_type == "image"
