import re

from argparse import Namespace
from version_buddy import semver
from version_buddy.run import *


def test_parse():
    version_string = "1.2.3-pr1"
    output = do_parse(Namespace(string=version_string))

    assert semver.parse(version_string) == output.version
