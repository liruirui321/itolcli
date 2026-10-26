# Third-party components and provenance

The itolcli source is MIT licensed. This repository does not vendor the source of the projects listed below.

| Component | Relationship | Upstream |
| --- | --- | --- |
| Biopython | Optional runtime dependency for parsing/conversion (`trees` extra); distributed under its own license terms | https://github.com/biopython/biopython |
| PyiTOL 1.0.3 | Optional runtime dependency and subprocess CLI integration (`pyitol` extra), MIT; original author Zichao Zeng | https://github.com/ZengZichao/PyiTOL |
| iTOL | Remote service and documented annotation/API specifications; not bundled or reimplemented | https://itol.embl.de/help.cgi |

PyiTOL source inspected for integration: GitHub main commit `4b0cfb7b057909b4f2e1391dbb10b8f9eafc5309` on 2026-10-26. The dependency is pinned to PyPI release 1.0.3, which need not be identical to that commit. See the installed version's help for its exact interface. Dependency wheels retain their own license files and transitive dependency metadata.

The repository's generated example tree and tables are synthetic. No real user data, credentials, or copied third-party source is included. If upstream source is vendored in the future, retain its copyright notices, license and modification history.
