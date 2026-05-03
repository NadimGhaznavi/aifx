# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.15.11] - 2026-05-03 @ 16:32

### Fixed
-  aifx being shadowed by aifs script.

---

## [0.15.10] - 2026-05-03 @ 16:15

### Added
- Package updates

---

## [0.15.9] - 2026-05-03 @ 12:16

### Fixed
- Tutorial page table syntax

---

## [0.15.8] - 2026-05-03 @ 12:02

### Added

- Added an `aifx` project folder and started on building a `AI FX` client
- Setup Qt with PySide6, this will be a Qt application

### Fixed
- Tutorial page table syntax

---

## [0.15.7] - 2026-05-02 @ 23:32

### Added

- Added tutorials 12, 13, 14, 15
- Added an introduction to the website
- Linked the most recent GitHub release to the TOC
- Constants files for accounts, candles, defaults, directories, files, frequencies, pairs, instruments, and prices
- Added initial aifx code and module support

### Changed 

- Numbering: The series author's first two videos don't count in his numbering scheme. 
- Renumbered files and file references to match the tutorial's descriptions, e.g. "...in episode 12..."
- Updated the TOC with the new numbering

---

## [0.14.0] - 2026-05-02 @ 19:40

### Added

- Added tutorials 12, 13, and 14
- Added an introduction to the website
- Linked the most recent GitHub release to the TOC
- Constants files for accounts, candles, defaults, instruments, and prices

---

## [0.11.0] - 2026-05-02 @ 16:11

### Added

- **Website**
  - Create a CNAME record to publish this repo as https://aifx.osoyalce.com
  - Configured the GitHub repo to publish under the DNS name
  - Created a website
    - Created per episode summary pages
    - Created simple access to per episode code artifacts

---

## [0.0.2] - 2026-04-16 @ 23:51

### Added
- GitHub actions workflow to publish to PyPI: `pip install aifx`
- `aifx` skeleton script
