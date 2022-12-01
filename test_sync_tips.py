import pytest

from sync_tips import parse_tip_file, Tip

note1_content = """# Some title

Some description

```
>>> start_index, end_index = [
...     i for i, line in enumerate(lines)
...     if line.strip() == "~~~"
... ]
```

#tag
"""
note2_content = """# Another tip

Multiline
description
and extra newline


```
>>> print("hello")

```

#tag1 #tag2
"""

expected_tip1 = Tip(
    title="Some title",
    description="Some description",
    code='>>> start_index, end_index = [\n...     i for i, line in enumerate(lines)\n...     if line.strip() == "~~~"\n... ]',
)
expected_tip2 = Tip(
    title="Another tip",
    description="Multiline\ndescription\nand extra newline",
    code='>>> print("hello")',
)


@pytest.fixture
def note1(tmp_path):
    note_path = tmp_path / "note1"
    note_path.write_text(note1_content)
    return note_path


@pytest.fixture
def note2(tmp_path):
    note_path = tmp_path / "note2"
    note_path.write_text(note2_content)
    return note_path


@pytest.mark.parametrize(
    "file, expected",
    [
        ("note1", expected_tip1),
        ("note2", expected_tip2),
    ],
)
def test_parsing_note_files(request, file, expected):
    note_file = request.getfixturevalue(file)
    actual = parse_tip_file(note_file)
    assert actual == expected
