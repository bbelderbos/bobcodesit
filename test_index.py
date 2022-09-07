import pytest

from index import create_index, group_notes_by_tag, INDEX_NAME, NOTES_DIR

EXPECTED_OUTPUT = """# Notes index

## Productivity

- [Pybites productivity tips](notes/20220817104440.md)

## Python

- [Enumerate](notes/20220817104441.md)
- [Pathlib](notes/20220817104442.md)
- [Pybites productivity tips](notes/20220817104440.md)
"""


@pytest.fixture
def notes_dir(tmp_path):
    notes_dir = tmp_path / NOTES_DIR
    notes_dir.mkdir()
    return notes_dir


@pytest.fixture
def create_notes(notes_dir):
    note_base = "2022081710444"
    notes = (
        "# Pybites productivity tips\n\nblabla\n\n#productivity #Python",
        "# enumerate\n\nfor i, line in enumerate(lines, start=1):\n\n#python",
        "# pathlib\n\nyou can use home() and cwd() on a Path object\n\n#python"
    )
    for i, note in enumerate(notes):
        file = notes_dir / f"{note_base}{i}.md"
        with open(file, "w") as f:
            f.write(note + "\n")


def test_create_index(create_notes, notes_dir):
    tag_index_tree = group_notes_by_tag(notes_dir)
    create_index(tag_index_tree)

    with open(INDEX_NAME) as f:
        content = f.read().strip()

    # stripping off header
    actual = content.splitlines()[5:]
    expected = EXPECTED_OUTPUT.splitlines()[2:]

    assert actual == expected
