import os
import pathlib

import pytest
from freezegun import freeze_time

from sync_tips import Tip, parse_tip_file, get_latest_tips

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

files = """20221130102028.md
20221130102010.md
20221201102028.md
20221201134231.md"""


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


@pytest.fixture
def note_files(tmpdir_factory):
    # casting because LocalPath does not have touch()
    notes_dir = pathlib.Path(tmpdir_factory.mktemp("notes"))
    for file in files.split():
        (notes_dir / file).touch()
    assert len(os.listdir(notes_dir)) == 4
    return notes_dir


@pytest.mark.parametrize(
    "file, expected",
    [
        ("note1", expected_tip1),
        ("note2", expected_tip2),
    ],
)
def test_parsing_note_files(request, file, expected):
    note_file = request.getfixturevalue(file)
    assert parse_tip_file(note_file) == expected


@freeze_time("2022-12-1")
def test_all_new_tips(note_files):
    tips = get_latest_tips(tips_dir=note_files)
    # 20221130 and 20221201 tips
    expected = ['20221130102010', '20221130102028', '20221201102028', '20221201134231']
    assert sorted(p.stem for p in tips) == expected


@freeze_time("2022-12-2")
def test_two_new_tips(note_files):
    tips = get_latest_tips(tips_dir=note_files)
    # only 20221201 tips
    expected = ["20221201102028", "20221201134231"]
    assert sorted(p.stem for p in tips) == expected


@freeze_time("2022-12-3")
def test_no_new_tips(note_files):
    tips = get_latest_tips(tips_dir=note_files)
    # no tips, they are all outdated
    assert [p.stem for p in tips] == []
