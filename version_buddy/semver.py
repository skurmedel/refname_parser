"""Utilities for SemVer 2.0 parsing.

The Grammar
===========
Taken verbatim from the SemVer.org site (2024-02):

.. code-block:: bnf
    <valid semver> ::= <version core>
                    | <version core> "-" <pre-release>
                    | <version core> "+" <build>
                    | <version core> "-" <pre-release> "+" <build>

    <version core> ::= <major> "." <minor> "." <patch>

    <major> ::= <numeric identifier>

    <minor> ::= <numeric identifier>

    <patch> ::= <numeric identifier>

    <pre-release> ::= <dot-separated pre-release identifiers>

    <dot-separated pre-release identifiers> ::= <pre-release identifier>
                                            | <pre-release identifier> "." <dot-separated pre-release identifiers>

    <build> ::= <dot-separated build identifiers>

    <dot-separated build identifiers> ::= <build identifier>
                                        | <build identifier> "." <dot-separated build identifiers>

    <pre-release identifier> ::= <alphanumeric identifier>
                            | <numeric identifier>

    <build identifier> ::= <alphanumeric identifier>
                        | <digits>

    <alphanumeric identifier> ::= <non-digit>
                                | <non-digit> <identifier characters>
                                | <identifier characters> <non-digit>
                                | <identifier characters> <non-digit> <identifier characters>

    <numeric identifier> ::= "0"
                        | <positive digit>
                        | <positive digit> <digits>

    <identifier characters> ::= <identifier character>
                            | <identifier character> <identifier characters>

    <identifier character> ::= <digit>
                            | <non-digit>

    <non-digit> ::= <letter>
                | "-"

    <digits> ::= <digit>
            | <digit> <digits>

    <digit> ::= "0"
            | <positive digit>

    <positive digit> ::= "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

    <letter> ::= "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J"
            | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T"
            | "U" | "V" | "W" | "X" | "Y" | "Z" | "a" | "b" | "c" | "d"
            | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n"
            | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x"
            | "y" | "z"

Limits
======
There are some artificial limits imposed by the parser. They are mostly provided to catch bugs and
discourage denial of service attacks.

Invariants
==========
The types used in this module tries to check their invariants on creation, but this is Python and 
almost nothing is immutable. 

Note that it's usually not a good idea to change the values of SemVer and Identifier after creation,
as you lose these checks. For example, this would print an invalid SemVer:

.. code:: python
    version = SemVer(1, 0, -1)
    print(str(version))
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Self, Tuple

# A string will fail parsing if contains more code units than this. Python uses UCS-4 at most,
# a maximum bytesize would be MAX_VERSION_STRING_CODEUNIT_COUNT * 4.
MAX_VERSION_STRING_CODEUNIT_COUNT = 256


@dataclass(slots=True)
class Identifier:
    """An identifier used for a pre-release or build version."""

    value: str

    def __init__(self, value: str, _validated=False) -> None:
        if not _validated:
            if not value or not all(map(is_latin_alphanumeric, value)):
                raise SemVerParseError(
                    "An identifier must be a non-empty (latin) alphanumeric string"
                )

        self.value = value

    def __str__(self) -> str:
        return self.value


@dataclass(slots=True)
class SemVer:
    """A SemVer version triple plus optional pre-release and build identifiers."""

    major: int
    minor: int
    patch: int

    prerelease_identifiers: list[Identifier] = field(default_factory=lambda: list())
    build_identifiers: list[Identifier] = field(default_factory=lambda: list())

    def __str__(self) -> str:
        prerelease = ".".join(map(str, self.prerelease_identifiers))
        build = ".".join(map(str, self.build_identifiers))

        s = f"{self.major}.{self.minor}.{self.patch}"
        if prerelease:
            s += "-"
            s += prerelease
        if build:
            s += "+"
            s += build

        return s


class SemVerParseError(BaseException):
    pass


@dataclass
class SemVerParseOptions:
    pass


def parse(s: str, options: SemVerParseOptions = SemVerParseOptions()) -> SemVer:
    """
    Tries to parse a SemVer string. This parser is intentionally very strict.

    Notably, this means that the only allowed alphanumeric characters are the ones in the latin
    block.

    :param s: Input string
    :param options: Additional options, usually needed when used as a sub-parser.
    :raises SemVerParseError:
    :raises TypeError: Bad string type.

    Limits
    ------
    Will never read a string larger than `MAX_VERSION_STRING_CODEPOINT_COUNT`. This can be useful
    when reading the version from a stream, as it limits the number of data to be read.

    Grammar
    -------
    See https://semver.org/ or the module docs.
    """
    if not isinstance(s, str):
        raise TypeError("s must be a string")
    if len(s) > MAX_VERSION_STRING_CODEUNIT_COUNT:
        raise SemVerParseError("Limit exceeded: MAX_VERSION_STRING_CODEUNIT_COUNT")

    p = _ParserState(s)

    major = _expect_version_component(p, "major")
    expect_delimiter(p)
    minor = _expect_version_component(p, "minor")
    expect_delimiter(p)
    patch = _expect_version_component(p, "patch")

    prerelease_identifiers = []
    if p.peek_and_then(is_prerelease_start):
        p.advance()
        prerelease_identifiers = _expect_identifiers(p, "pre-release")

    build_identifiers = []
    if p.peek_and_then(is_build_start):
        p.advance()
        build_identifiers = _expect_identifiers(p, "build")

    if not p.at_end():
        raise SemVerParseError(f"Unexpected character at offset {p.offset}")

    return SemVer(
        major,
        minor,
        patch,
        prerelease_identifiers=prerelease_identifiers,
        build_identifiers=build_identifiers,
    )


class _ParserState:
    def __init__(self, input: str) -> None:
        self.input = input
        self.offset = 0

    def peek(self) -> str | None:
        if self.offset < len(self.input):
            return self.input[self.offset]

        return None

    def peek_and_then(self, f: Callable[[str], Any]) -> Any | None:
        candidate = self.peek()
        if candidate is not None:
            return f(candidate)
        else:
            return None

    def advance(self) -> str:
        # Note that we allow the offset to point just after the last code unit. This is helpful for
        # error reporting.
        if self.offset < len(self.input):
            c = self.peek()
            self.offset += 1
            return c
        else:
            raise SemVerParseError("Internal Error: advanced beyond input")

    def at_end(self) -> bool:
        return self.offset == len(self.input)


def _expect_version_component(p: _ParserState, name: str) -> int:
    def isdigit(s):
        return s.isdigit()

    def next_is_digit():
        return p.peek_and_then(isdigit)

    num_str = ""

    should_be_zero = False
    if next_is_digit():
        num_str += (c := p.advance())
        should_be_zero = c == "0"
    else:
        raise SemVerParseError(f"Expected {name} version number at offset {p.offset}")

    if next_is_digit() and should_be_zero:
        raise SemVerParseError(
            f"Unexpected digit at offset {p.offset}, numbers cannot start with zero"
        )

    while next_is_digit():
        num_str += p.advance()

    return int(num_str)


def expect_delimiter(p: _ParserState):
    if not p.peek_and_then(is_dot):
        raise SemVerParseError(f"Expected delimiter at offset {p.offset}")
    else:
        p.advance()


def is_latin_alphanumeric(c: str):
    import string

    return c in string.ascii_letters or c in string.digits


def is_unicode_alphanumeric(c: str):
    import unicodedata

    # https://www.unicode.org/reports/tr44/#General_Category_Values
    return unicodedata.category(c) in [
        "Lu",
        "Ll",
        "Lt",
        "Lm",
        "Lo",
        "Nd",
        "Nl",
        "No",
    ]


def check_if_char(expected: str):
    def inner(c: str) -> bool:
        return c == expected

    return inner


is_dot = check_if_char(".")
is_prerelease_start = check_if_char("-")
is_build_start = check_if_char("+")


def _expect_identifiers(p: _ParserState, name: str) -> list[str]:
    identifiers = []

    def next_is_alphanumeric():
        def is_alnum(c):
            if is_latin_alphanumeric(c):
                return True
            elif is_unicode_alphanumeric(c):
                raise SemVerParseError(
                    f"""Unexpected alphanumeric character "{c}" at offset {p.offset} (SemVer is latin alphabet only)"""
                )
            return False

        return p.peek_and_then(is_alnum)

    while True:
        if next_is_alphanumeric():
            current = p.advance()
            while next_is_alphanumeric():
                current += p.advance()

            identifiers.append(Identifier(current, _validated=True))
        else:
            raise SemVerParseError(f"Expected {name} identifier at offset {p.offset}")

        if p.peek_and_then(is_dot):
            p.advance()
        else:
            break

    if not identifiers:
        raise SemVerParseError(f"Expected {name} identifier at offset {p.offset}")

    return identifiers
