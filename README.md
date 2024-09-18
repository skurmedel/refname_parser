# version buddy
Version Buddy helps you with your software versioning tasks. Version Buddy has full semantic 
versioning 2.0 (SemVer) support.

A small sample of the functionality in Version Buddy:
- Compare SemVer strings.
- Bump a SemVer easily.
- Replace version strings in TOML or JSON files.
- Parse Git ref-strings and extract the version and branch data.
- Output parsed data in a variety of formats, such as JSON or straight into the outputs of a Github 
Actions job.

# Dependencies
Version Buddy targets Python 3.10. 

# Questions

## Why Python?
Version Buddy is intended for CI workflows and container use. Python is portable, widely understood
and often bundled with the environment, allowing it to be included with minimal hassle.

## Why a custom parser?
It is easier to extend and we avoid dependencies. Self-contained software is nice.

# TODO
- [x] SemVer parser
- [ ] SemVer comparisons
- [ ] Basic CLI interface
- [ ] Output as JSON
- [ ] Output as Github Actions "output syntax"