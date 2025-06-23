# AI Bug Reporter with Advanced Classification

## Overview
This is a desktop application built with Python's Tkinter that helps software testers and developers generate detailed bug reports using AI (Cohere API). The app supports advanced bug classification, estimated time to fix, and saves reports in a local SQLite database.

---

## Features
- **AI-Powered Bug Report Generation:** Automatically generate detailed bug reports from user input using Cohere's language model.
- **Advanced Bug Classification:** The report includes predicted bug type (UI, Backend, Network, Performance, Security, Other).
- **Estimated Time to Fix:** AI provides a time estimate to resolve the bug.
- **Database Storage:** Save bug reports locally with timestamps for future reference.
- **Report Browsing:** View previously saved bug reports with quick access to their title and timestamp.
- **Easy-to-use GUI:** Tabbed interface for creating and viewing bug reports.

---

## Installation

### Prerequisites
- Python 3.7+
- Install required packages:
```bash
pip install cohere tkinter
