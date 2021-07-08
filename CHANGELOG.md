# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2021-07-08

### Changed
- renamed deadlink-fix to deadlink-replace-redirects
- only follow permanent redirects (301)
- removed `__version__`

### Fixed
- respect the allowed/ignored URL patterns in the config

## [0.2.6] - 2021-07-08

### Added
- --allow-files/--ignore-files command line options
- pre-commit hook

### Fixed
- don't modify hidden files/directories
