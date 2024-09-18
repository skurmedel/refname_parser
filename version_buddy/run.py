from argparse import ArgumentParser

from dataclasses import dataclass
import sys
from version_buddy import formatter
from version_buddy.semver import SemVer
from version_buddy import semver


@dataclass
class ParseOutput:
    version: SemVer


def do_parse(arguments) -> ParseOutput:
    version_string = arguments.string
    version = semver.parse(version_string)

    return ParseOutput(version=version)


def cli(args=None):
    argparser = ArgumentParser(description="TODO")

    # FORMATTING OPTIONS
    argparser.add_argument("--json_indent", type=int, default=1)

    cmds = argparser.add_subparsers(required=True)

    # PARSE COMMAND
    parse_cmd = cmds.add_parser("parse")
    parse_cmd.add_argument("string", type=str)
    parse_cmd.set_defaults(handler=do_parse)

    # HANDLE SUBCOMMAND
    parsed_arguments = argparser.parse_args(args)
    output = parsed_arguments.handler(parsed_arguments)

    json_formatter = formatter.into_json(indent=parsed_arguments.json_indent)
    print(json_formatter(output))
    sys.stdout.write("\n")
