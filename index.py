"""Script to create an index file from my Zettelkasten notes (md files)"""
from collections import defaultdict
from pathlib import Path
import re
from typing import NamedTuple

INDEX_NAME = "index.md"
NOTES_DIR = Path("notes")
TAG_REGEX = re.compile(r"#\S+")
HEADER = """# Bob's code tips archive

Idea from [this post](https://www.edwinwenink.xyz/posts/42-vim_notetaking/).
This file gets generated by [this script](index.py).

"""


class Note(NamedTuple):
    title: str
    filename: str


def _filter_valid_tag_lines(filename, lines: list[str]) -> list[str]:
    in_code_block = False
    tag_lines = []
    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block and line.startswith("#"):
            tag_lines.append(line)
    return tag_lines


def group_notes_by_tag(
    directory: Path = Path.cwd() / NOTES_DIR,
) -> defaultdict[str, list[Note]]:
    notes_grouped_by_tags = defaultdict(list)

    filenames = directory.glob("*.md")

    for filename in filenames:
        note_content = filename.read_text()
        lines = note_content.splitlines()
        title = lines.pop(0).strip("# ").capitalize()
        no_code_lines = _filter_valid_tag_lines(str(filename), lines)
        tag_content = "\n".join(no_code_lines)
        tags = re.findall(TAG_REGEX, tag_content)

        for tag in tags:
            tag = tag.lstrip("#").title()
            notes_grouped_by_tags[tag].append(Note(title=title, filename=filename.name))

    return notes_grouped_by_tags


def create_index(tag_index_tree: defaultdict[str, list[Note]]) -> None:
    output = [HEADER]

    for tag, notes in sorted(tag_index_tree.items()):
        tag = tag.lower().capitalize()
        output.append(f"## {tag}\n\n")

        for note in sorted(notes):
            note_filepath = NOTES_DIR / note.filename
            output.append(f"- [{note.title}]({note_filepath})\n")

        output.append("\n")

    with open(INDEX_NAME, "w") as f:
        f.write("".join(output))


if __name__ == "__main__":
    tag_index_tree = group_notes_by_tag()
    create_index(tag_index_tree)
