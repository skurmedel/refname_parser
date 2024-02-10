# version buddy
Version Buddy helps you with your software versioning tasks. Version Buddy has full semantic 
versioning 2.0 (SemVer) support.

Here are some of the tools and capabilities of Version Buddy:
- Compare SemVer strings.
- Bump a SemVer easily.
- Replace version strings in TOML or JSON files.
- Parse Git ref-strings and extract the version and branch data.
- Output parsed data in a variety of formats, such as JSON or straight into the outputs of a Github 
Actions job.

# Dependencies
Version Buddy targets Python 3.8. 

# TODO
- [x] SemVer parser
- [ ] SemVer comparisons
- [ ] Basic CLI interface
  - [ ] SemVer parse
  - [ ] SemVer compare
  - [ ] Output as JSON
  - [ ] Output as Github Actions "output syntax"

# Questions

## Why Python?
The main use case for Version Buddy is in build & CI workflows. A lot CI toolchains make us of 
Python at some point during a build. It is also commonly bundled in containers used for builds.

Restricting ourselves to Python helps with build times. It is a small download and nothing 
Version Buddy does is computationally heavy.

## Why a custom parser?
It is easier to extend and we avoid dependencies. Self-contained software is nice.

