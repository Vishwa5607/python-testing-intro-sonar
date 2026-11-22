from text import count_lines, count_characters, count_bytes
import pytest
import requests


@pytest.fixture
def test_file_generator(tmp_path):
    def _test_file(n_lines):
        filename = tmp_path / "temp_file.txt"
        with open(filename, "w") as f:
            for _ in range(n_lines):
                f.write("hello\n")
        return filename

    return _test_file


@pytest.mark.parametrize("n_lines", [0, 1, 2, 3, 5, 88])
def test_count_lines(test_file_generator, n_lines):
    test_file = test_file_generator(n_lines=n_lines)
    assert count_lines(test_file) == n_lines


@pytest.mark.parametrize("n_lines", [0, 1, 2, 3, 5, 88])
def test_count_characters(test_file_generator, n_lines):
    test_file = test_file_generator(n_lines=n_lines)
    assert count_characters(test_file) == n_lines * 6


def test_count_bytes_good(monkeypatch):
    # this is a better test: we monkeypatch requests to return known binary data for this test
    # the test no longer depends on the exact contents of a file on the internet being available and unchanged to work

    # This is the object we will return when the code does requests.get(url)
    class FakeRequestsGetReturnObject:
        def __init__(self):
            # hard-code content for this test
            self.content = b"abc123"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        requests, "get", lambda *args, **kwargs: FakeRequestsGetReturnObject()
    )
    assert count_bytes("the-url-is-ignored-in-this-test") == 6


@pytest.fixture
def named_tmp_file(tmp_path):
    def _callable(name):
        return tmp_path / name

    return _callable


def test_tmp_file(named_tmp_file):
    tmp_file = named_tmp_file("tempy.temp")
    assert tmp_file.name == "tempy.temp"


def test_count_bytes_passes_timeout(monkeypatch):
    seen = {}

    class FakeResponse:
        content = b"xyz"

        def raise_for_status(self):
            pass

    def fake_get(url, **kwargs):
        seen.update(kwargs)
        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)
    assert count_bytes("http://example.invalid") == 3
    assert seen["timeout"] > 0


def test_count_bytes_http_error(monkeypatch):
    class FakeErrorResponse:
        content = b"<html>Not Found</html>"

        def raise_for_status(self):
            raise requests.HTTPError("404")

    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeErrorResponse())
    with pytest.raises(requests.HTTPError):
        count_bytes("http://example.invalid")


def test_count_characters_non_ascii(tmp_path):
    f = tmp_path / "u.txt"
    f.write_text("héllo\n", encoding="utf-8")
    assert count_characters(f) == 6
