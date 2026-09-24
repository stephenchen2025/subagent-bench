def check_chunks():
    from textkit import chunks
    assert chunks.chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert chunks.chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]
    assert chunks.chunk([], 3) == []
    assert chunks.chunk("abcde", 5) == [["a", "b", "c", "d", "e"]]


def check_errors():
    from textkit import chunks
    try:
        chunks.chunk([1], 0)
    except ValueError:
        return
    raise AssertionError("no ValueError")
