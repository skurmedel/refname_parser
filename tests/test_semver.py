from dataclasses import dataclass
from io import StringIO
import re
from pytest import raises

from version_buddy.semver import *


def test_parse_bad_types():
    for val in [None, 123, [1, 2, 3]]:
        with raises(TypeError):
            parse(val)


def test_parse_passes():
    cases = [
        ("0.0.0", SemVer(0, 0, 0)),
        ("1.0.0", SemVer(1, 0, 0)),
        ("0.1.0", SemVer(0, 1, 0)),
        ("0.0.1", SemVer(0, 0, 1)),
        ("200.3000.40000", SemVer(200, 3000, 40000)),
        (
            "1.0.0-123",
            SemVer(1, 0, 0, prerelease_identifiers=[Identifier("123")]),
        ),
        (
            "1.0.0-123.abc123",
            SemVer(
                1,
                0,
                0,
                prerelease_identifiers=[
                    Identifier("123"),
                    Identifier("abc123"),
                ],
            ),
        ),
        ("1.0.0+456", SemVer(1, 0, 0, build_identifiers=[Identifier("456")])),
        (
            "1.0.0+456.def456",
            SemVer(
                1,
                0,
                0,
                build_identifiers=[Identifier("456"), Identifier("def456")],
            ),
        ),
        (
            "1.0.0-123.abc123+456.def456",
            SemVer(
                1,
                0,
                0,
                prerelease_identifiers=[
                    Identifier("123"),
                    Identifier("abc123"),
                ],
                build_identifiers=[Identifier("456"), Identifier("def456")],
            ),
        ),
    ]

    for input, expected in cases:
        print(f""""{input}" should give: {expected}""")
        actual = parse(input)
        assert expected == actual


def test_parse_errors():
    cases = [
        ("", """Expected major version number at offset 0"""),
        ("a", """Expected major version number at offset 0"""),
        (".", """Expected major version number at offset 0"""),
        ("1", """Expected delimiter at offset 1"""),
        ("1.", """Expected minor version number at offset 2"""),
        ("1.1", """Expected delimiter at offset 3"""),
        ("1.1.", """Expected patch version number at offset 4"""),
        ("1.1.1-", """Expected pre-release identifier at offset 6"""),
        ("1.1.1-a.", """Expected pre-release identifier at offset 8"""),
        ("1.1.1+", """Expected build identifier at offset 6"""),
        ("1.1.1+a.", """Expected build identifier at offset 8"""),
        ("1.1.1-a+", """Expected build identifier at offset 8"""),
        ("1.1.1-a+b.", """Expected build identifier at offset 10"""),
        ("1.1.1-a+b.c ", """Unexpected character at offset 11"""),
        ("01.0.0", """Unexpected digit at offset 1, numbers cannot start with zero"""),
        ("0.01.0", """Unexpected digit at offset 3, numbers cannot start with zero"""),
        ("0.0.01", """Unexpected digit at offset 5, numbers cannot start with zero"""),
        (
            "1.0.0-123.abc\u0985",
            """Unexpected alphanumeric character "\u0985" at offset 13 (SemVer is latin alphabet only)""",
        ),
    ]

    for input, message in cases:
        with raises(SemVerParseError, match=re.escape(message)):
            print(f""""{input}" should raise: {message}""")
            parse(input)


def test_parse_input_too_long():
    # This cuneiform sign requires four bytes in UTF, which means its a good way to make sure we
    # don't accidently limit by bytes instead of units.
    CUNEIFORM_SIGN_A = "\u12000"

    # This should fail before we even parse, so what the characters are doesn't matter much.
    too_long = CUNEIFORM_SIGN_A * (MAX_VERSION_STRING_CODEUNIT_COUNT + 1)

    with raises(SemVerParseError, match=re.escape("Limit exceeded")):
        parse(too_long)


def test_parse_roundtrip_str():
    version = SemVer(
        1,
        0,
        0,
        prerelease_identifiers=[Identifier("123"), Identifier("abc123")],
        build_identifiers=[Identifier("456"), Identifier("def456")],
    )
    assert "1.0.0-123.abc123+456.def456" == str(version)
    assert version == parse(str(version))


def test_identifier():
    pass_inputs = ["0", "123", "abc0123", "abcefd"]

    for case in pass_inputs:
        Identifier(case)

    fail_inputs = ["", " 123", "123 ", "abc\u0985"]

    for case in fail_inputs:
        with raises(SemVerParseError):
            Identifier(case)
