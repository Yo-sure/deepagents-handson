from course.qna import search_materials, read_material, CORPUS


def test_materials_cover_lessons_and_solutions():
    index = read_material("INDEX.md")
    for name in ["graph", "mcp", "a2a", "harness", "wrap"]:
        assert f"textbook/{name}.md" in index
    assert "notebooks/build-agent-solution.md" in index
    assert "notebooks/harness-build-solution.md" in index
    assert "visited" in search_materials("visited")
    assert "셀" in read_material("notebooks/build-agent-solution.md")


def test_material_reader_cannot_read_environment_or_outside_paths():
    for path in ["../.env", str(CORPUS.parent / ".env"), "../../AGENTS.md"]:
        assert "경로만" in read_material(path)
    assert len(read_material("notebooks/build-agent-solution.md", line_count=9999).splitlines()) <= 160
