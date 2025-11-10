# Contributing to Google Maps RPC Scraper

Thank you for your interest in contributing to this project! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)

---

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:

- **Be respectful** and inclusive
- **Be collaborative** and constructive
- **Focus on** what is best for the community
- **Show empathy** towards other community members

---

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/google-maps-rpc-scraper.git
   cd google-maps-rpc-scraper/google-maps-scraper-python
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original/google-maps-rpc-scraper.git
   ```

4. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your settings
```

### Verify Setup

```bash
# Run test script
python test_scraper.py

# Should see successful scraping output
```

---

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Bug Fixes** - Fix existing issues
2. **New Features** - Add new functionality
3. **Documentation** - Improve or translate docs
4. **Performance** - Optimize existing code
5. **Testing** - Add or improve tests
6. **UI/UX** - Enhance web application interface

### Finding Work

- Check [Issues](https://github.com/yourusername/google-maps-rpc-scraper/issues)
- Look for `good first issue` or `help wanted` labels
- Read the [Roadmap](#roadmap) in README.md
- Propose your own improvements

---

## Pull Request Process

### Before Submitting

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Test your changes**:
   ```bash
   # Run test script
   python test_scraper.py

   # Test web application
   cd webapp
   python app.py
   # Open http://localhost:5000 and verify functionality
   ```

3. **Update documentation** if needed:
   - Update README.md for user-facing changes
   - Update CLAUDE.md for developer documentation
   - Add docstrings to new functions/classes

4. **Follow coding standards** (see below)

### Submitting PR

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

   **Commit message format**:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style (formatting, no logic change)
   - `refactor:` - Code refactoring
   - `perf:` - Performance improvements
   - `test:` - Adding or updating tests
   - `chore:` - Maintenance tasks

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request** on GitHub:
   - Provide clear title and description
   - Reference related issues (e.g., "Fixes #123")
   - Include screenshots for UI changes
   - List breaking changes if any

### PR Review Process

1. **Automated checks** will run (when CI/CD is set up)
2. **Maintainer review** - May request changes
3. **Address feedback** - Update your PR as needed
4. **Approval** - PR will be merged when approved

---

## Coding Standards

### Python Style

Follow **PEP 8** style guide:

```python
# Good
def scrape_reviews(place_id: str, max_reviews: int = 100) -> Dict:
    """
    Scrape reviews from a Google Maps place.

    Args:
        place_id: Google Maps place ID
        max_reviews: Maximum number of reviews to scrape

    Returns:
        Dict containing reviews and metadata
    """
    pass

# Bad
def scrapeReviews(placeId,maxReviews=100):
    pass
```

### Key Principles

1. **Type Hints**: Use type hints for function parameters and return values
2. **Docstrings**: Add docstrings to all public functions and classes
3. **Comments**: Explain "why", not "what"
4. **Naming**:
   - `snake_case` for functions and variables
   - `PascalCase` for classes
   - `UPPER_CASE` for constants
5. **Line Length**: Max 100 characters (flexible for readability)
6. **Imports**: Group by standard library, third-party, local

### Code Organization

```python
# 1. Encoding declaration (for Thai/Unicode files)
# -*- coding: utf-8 -*-

# 2. Module docstring
"""
Module description
"""

# 3. Windows encoding fix
import sys
import os
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

# 4. Imports (grouped)
import asyncio  # Standard library
from typing import List, Dict, Optional

import httpx  # Third-party

from src.utils.anti_bot_utils import generate_randomized_headers  # Local

# 5. Constants
MAX_RETRIES = 3

# 6. Classes and functions
class MyClass:
    pass

def my_function():
    pass
```

---

## Testing Guidelines

### Manual Testing

**Minimum testing requirements**:

1. **Test with different places**:
   ```bash
   python test_scraper.py
   ```

2. **Test web application**:
   - Search for places (Thai and English)
   - Start scraping task
   - Monitor real-time progress
   - Download results (JSON and CSV)
   - Check output files in `outputs/`

3. **Test edge cases**:
   - Empty search results
   - Places with 0 reviews
   - Places with 1000+ reviews
   - Different date ranges
   - Unlimited mode
   - Various languages (th, en, ja)

### Test Checklist

Before submitting PR, verify:

- [ ] Code runs without errors
- [ ] No console warnings or exceptions
- [ ] Thai characters display correctly
- [ ] Progress bar updates in real-time
- [ ] Output files are properly formatted
- [ ] CSV export works correctly
- [ ] No duplicate reviews
- [ ] Date filtering works as expected
- [ ] Rate limiting doesn't trigger (or handles gracefully)

---

## Documentation

### When to Update Docs

Update documentation when you:

- Add new features
- Change existing functionality
- Add configuration options
- Fix bugs that affect usage
- Add new API methods

### Which Docs to Update

1. **README.md** - User-facing changes
   - Features, installation, usage examples

2. **CLAUDE.md** - Developer documentation
   - Architecture, implementation details, debugging

3. **Code Comments** - Inline explanations
   - Complex algorithms, workarounds, important notes

4. **Docstrings** - Function/class documentation
   - Parameters, return values, examples

### Documentation Style

```python
def scrape_reviews(
    self,
    place_id: str,
    max_reviews: int = 10000,
    date_range: str = "all",
    progress_callback: Optional[callable] = None
) -> Dict:
    """
    Scrape reviews from a Google Maps place.

    This method uses Google's internal RPC API to fetch reviews without
    requiring an API key. It supports date filtering, progress tracking,
    and automatic duplicate detection.

    Args:
        place_id: Google Maps place ID (format: 0x...)
        max_reviews: Maximum reviews to scrape (0 = unlimited)
        date_range: Date filter ("1month", "6months", "1year", "5years", "all")
        progress_callback: Optional callback function(page_num, total_reviews)

    Returns:
        Dict with keys:
            - reviews: List of ProductionReview objects
            - metadata: Dict with scraping stats and performance metrics

    Example:
        >>> scraper = create_production_scraper(language="th", region="th")
        >>> result = await scraper.scrape_reviews(
        ...     place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
        ...     max_reviews=100,
        ...     date_range="1year"
        ... )
        >>> print(f"Scraped {len(result['reviews'])} reviews")

    Note:
        - Google may limit pagination to ~1000-2000 reviews
        - Use date_range filtering to reduce total reviews
        - Progress callback is called after each page (20 reviews)
    """
    pass
```

---

## Bug Reports

### Before Reporting

1. **Search existing issues** - May already be reported
2. **Update to latest version** - Bug may be fixed
3. **Test with test_scraper.py** - Isolate the issue

### Bug Report Template

```markdown
**Describe the bug**
A clear and concise description.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g., Windows 11, macOS 13]
 - Python Version: [e.g., 3.10.5]
 - Browser (if web app): [e.g., Chrome 120]

**Additional context**
Any other relevant information.

**Logs**
```
Paste relevant console output or error messages
```
```

---

## Feature Requests

### Before Requesting

1. **Check roadmap** in README.md - May be planned
2. **Search existing issues** - May already be requested
3. **Consider scope** - Should fit project goals

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Describe the problem: "I'm frustrated when [...]"

**Describe the solution you'd like**
Clear description of desired functionality.

**Describe alternatives you've considered**
Other approaches you've thought about.

**Additional context**
Any other relevant information, mockups, examples.

**Potential implementation**
If you have ideas on how to implement this.
```

---

## Development Guidelines

### Project Structure

Maintain the existing structure:

```
src/
├── scraper/
│   └── production_scraper.py    # Core scraping logic
├── search/
│   └── rpc_place_search.py      # Place search
└── utils/
    ├── anti_bot_utils.py        # Anti-detection
    ├── output_manager.py        # File management
    └── unicode_display.py       # Thai/Unicode support
```

### Adding New Features

1. **Core scraper features** → `src/scraper/production_scraper.py`
2. **Search features** → `src/search/rpc_place_search.py`
3. **Utilities** → `src/utils/`
4. **Web UI** → `webapp/`

### Backward Compatibility

- **Don't break existing APIs** without major version bump
- **Deprecate gracefully** - Warn before removing
- **Provide migration path** in documentation

### Anti-Bot Protection

When modifying anti-bot features:

- **Test thoroughly** - Don't trigger rate limits
- **Be conservative** - Prefer safer over faster
- **Document risks** - Note detection probability
- **Respect Google** - Don't abuse their infrastructure

---

## Community

### Getting Help

- **GitHub Issues** - Technical questions
- **GitHub Discussions** - General questions, ideas
- **Email** - Private security concerns

### Recognition

Contributors will be:
- Listed in README.md acknowledgments
- Credited in release notes
- Mentioned in commit history

---

## License

By contributing, you agree that your contributions will be licensed under the **MIT License**.

---

**Thank you for contributing! 🙏**

Every contribution, no matter how small, helps make this project better for everyone.
