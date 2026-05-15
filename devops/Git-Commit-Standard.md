---
title: Git
layout: default
---

# Introduction

This document outlines a specification for adding human- and machine-readable meaning to commit messages. It is based on the [Conventional Commits Specification](https://www.conventionalcommits.org/) and has been adopted by [Db4E](https://github.com/NadimGhaznavi/Db4E), the [Database 4 Everything](https://db4e.osoyalce.com/) project.

This convention dovetails with the [Semantic Versioning](http://semver.org/) specification by describing the features, fixes, and breaking changes made in commit messages.

---

# Subjects, Categories, Tone

## Subjects

Keep the subject short and sweet, concise enough to read in one glance.

## Optional Paragraph

The *diff* shows *what* changed. The message should give context on *why*.
Using bullets or paragraphs helps organize details, especially for complex changes. Limit line length for terminals and git tools. Insert a blank line after the subject line when creating paragraphs.

## Categories

Category   | Descriptions
-----------|-----------------
`feat`     | A new feature.
`fix`      | A bug fix.
`docs`     | Documentation only changes.
`style`    | Formatting changes, not code changes.
`refactor` | Code changes that neither fixes a bug nor adds a feature.
`test`     | Adding or refactoring Tests.
`chore:`   | Build process or auxiliary tool changes.

## Tone

Write messages like a command:

* **Good:** `Add user authentication`
* **Bad:** `Added user authentication` or `Adding user authentication`

## Examples

Insert a blank line after the subject. if the message is multi-line.

```
feat: add support for remote monerod deployment

This adds the ability to deploy monerod nodes on remote machines
via SSH, including secure key handling and connection retries.
```

```
fix: do not display an empty health box
```

---

# Issues, Tickets and PRs

Where applicable, include reference numbers to project issues, tickets or PRs. For example:

```
fix: race condition on startup (#42)
```

---

# Links 

* [Conventional Commits](https://www.conventionalcommits.org/)
* [Semantic Versioning](https://semver.org/)