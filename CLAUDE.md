# CLAUDE.md - Project Instructions

This file provides instructions for Claude Code when working on this repository.

## Repository Overview

This is a GitHub Pages repository containing:
- **Web Crawler tools** - Python-based web scraping utilities with test suites
- **NGSM documents** - Lilly Service Management AI Agents documentation and analysis
- **Analysis scripts** - Cortex capability mapping and automation tools

---

## Custom Configuration

### 🎸 Guitar-Themed Spinner Messages

This repository uses custom guitar and music-themed spinner verbs configured in `~/.claude/settings.json`:

**Spinner Verbs:**
- "Tuning the strings" - General preparation
- "Finding the right chord" - Searching/analyzing
- "Playing through the progression" - Processing/working
- "Reading the tablature" - Reading code
- "Composing a new riff" - Writing new code
- "Laying down the track" - Committing changes
- "Sound checking" - Testing
- "Adjusting the levels" - Configuring
- "Fixing a broken string" - Debugging
- "Finding the right note" - Searching
- "Staging the performance" - Git staging
- "Committing the jam session" - Git commit
- "Recording to tape" - Saving files
- "Building the guitar" - Building/compiling
- "Preparing for the gig" - Setup tasks
- "Plugging in the amp" - Initializing
- "Dialing in the tone" - Fine-tuning
- "Checking the mix" - Reviewing
- "Learning the melody" - Understanding code
- "Writing the arrangement" - Planning/designing

These messages reflect the repository owner's musical interests while maintaining professional functionality.

---

## General Guidelines

### Code Quality Standards

1. **Python Code**
   - Follow PEP 8 style guidelines
   - Use type hints where appropriate
   - Write descriptive docstrings for functions and classes
   - Prefer explicit over implicit
   - Keep functions focused and single-purpose

2. **Testing**
   - Always run tests after making changes to code
   - Maintain >80% code coverage for critical components
   - Use the test suite in `Web Crawler/Tester/` for web crawler changes
   - Add tests for new features before implementation (TDD)

3. **Documentation**
   - Update README files when adding new features
   - Keep documentation in sync with code
   - Use clear, concise markdown formatting
   - Include examples for complex functionality

---

## Git & Version Control

### Commit Message Format

Use conventional commit format:
```
<type>: <short description>

<detailed description>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or modifications
- `refactor:` - Code refactoring
- `style:` - Code style changes (formatting, etc.)
- `chore:` - Maintenance tasks

### Before Committing

1. ✅ Run tests if code was modified
2. ✅ Check for secrets or sensitive data
3. ✅ Review staged changes with `git diff --cached`
4. ✅ Ensure commit message is descriptive
5. ✅ Verify no unnecessary files are included (.DS_Store, .bak, etc.)

### What NOT to Commit

❌ `.DS_Store` files (macOS system files)
❌ `.bak` backup files
❌ Test output directories (`coverage_report/`, `__pycache__/`)
❌ Real secrets or credentials
❌ Large binary files without good reason
❌ Personal API keys or tokens

---

## Project-Specific Instructions

### Web Crawler

**Location:** `Web Crawler/`

1. **Making Changes:**
   - Always run the test suite after modifications
   - Use `python3 -m pytest -v` in the `Web Crawler/Tester/` directory
   - Ensure all 61 tests pass before committing
   - Check code coverage with `./run_tests.sh coverage`

2. **Security:**
   - The `sanitize_html()` function is critical for removing secrets
   - Always test sanitization with the provided test fixtures
   - Never disable or weaken secret removal patterns
   - Add tests for any new secret patterns

3. **Test Data:**
   - All test secrets in `fixtures/` are FAKE and for testing only
   - Never use real credentials in test data
   - Clearly mark test data as "FAKE" in comments

### NGSM Documents

**Location:** `NGSM/`

1. **Markdown Files:**
   - Use consistent heading levels (H1 for title, H2 for sections)
   - Keep tables formatted and readable
   - Use bullet points for lists
   - Link to related documents where appropriate

2. **Analysis Scripts:**
   - Document script purpose at the top of each file
   - Include usage examples in docstrings
   - Handle errors gracefully with informative messages

### Cortex Integration

1. **Cortex Capability Mapping:**
   - Keep `CORTEX_MAPPING_REPORT.md` up to date
   - Document all Cortex toolkits and their capabilities
   - Link agent requirements to available Cortex features

2. **Toolkit Documentation:**
   - Clearly describe toolkit purposes
   - Note configuration requirements
   - Include usage examples

---

## macOS-Specific Notes

Since this repo is primarily used on macOS:

1. **Python Commands:**
   - Always use `python3` (not `python`)
   - Always use `pip3` (not `pip`)
   - Commands are in zsh shell

2. **Path Handling:**
   - Be aware of spaces in OneDrive paths
   - Quote paths with spaces
   - Use absolute paths when necessary

3. **File Permissions:**
   - Scripts should be executable: `chmod +x script.sh`
   - Check permissions before running shell scripts

---

## Testing Philosophy

### When to Run Tests

- ✅ After any code changes
- ✅ Before committing
- ✅ After pulling updates
- ✅ When adding new features
- ✅ When fixing bugs

### Test Categories

Use pytest markers to run specific test categories:
```bash
pytest -m unit          # Fast unit tests
pytest -m integration   # Integration tests
pytest -m "not slow"    # Exclude performance tests
pytest -k "sanitize"    # Tests matching pattern
```

### Coverage Goals

- **Minimum:** 80% for all code
- **Critical functions:** 100% (e.g., sanitize_html)
- **New features:** 90%+ coverage required

---

## Working with Secrets

### Secret Sanitization

1. **Never commit real secrets**
   - Always use fake/dummy credentials in test data
   - Run sanitization on all HTML output
   - Review diffs before committing

2. **Patterns to Redact:**
   - Azure AD client secrets (Q~ pattern)
   - Client IDs (UUIDs in context)
   - Bearer tokens
   - API keys (sk_test_, api_key_, etc.)
   - Access tokens

3. **Testing Sanitization:**
   - Add test cases for new secret patterns
   - Verify redaction with test fixtures
   - Check that normal content is preserved

---

## Common Tasks

### Running Tests
```bash
cd "Web Crawler/Tester"
python3 -m pytest -v
```

### Installing Dependencies
```bash
cd "Web Crawler/Tester"
./install_dependencies.sh
```

### Checking Coverage
```bash
cd "Web Crawler/Tester"
./run_tests.sh coverage
open coverage_report/index.html
```

### Quick Validation
```bash
cd "Web Crawler/Tester"
python3 quick_start.py
```

---

## Error Handling

### When Tests Fail

1. Read the error message carefully
2. Check which test failed and why
3. Run the specific test with `-vv` for more detail
4. Fix the issue in the code
5. Re-run all tests to ensure nothing else broke
6. Update tests if the behavior change was intentional

### When Dependencies Are Missing

```bash
cd "Web Crawler/Tester"
pip3 install -r test_requirements.txt
```

---

## Performance Considerations

1. **Web Crawler:**
   - Use appropriate delays between requests
   - Respect robots.txt
   - Don't overwhelm servers
   - Use connection pooling (already implemented)

2. **Tests:**
   - Keep unit tests fast (<0.01s each)
   - Use mocking for external dependencies
   - Mark slow tests with `@pytest.mark.slow`

---

## Documentation Standards

### README Files

- Include installation instructions
- Provide usage examples
- List requirements
- Show expected output
- Link to related documentation

### Code Comments

- Explain WHY, not WHAT
- Document non-obvious behavior
- Include examples for complex logic
- Keep comments up to date

### Markdown

- Use proper heading hierarchy
- Format code blocks with language tags
- Keep line length reasonable
- Use tables for structured data

---

## Preferred Workflow

1. **Before Making Changes:**
   - Understand the current implementation
   - Read relevant documentation
   - Check existing tests
   - Review related code

2. **While Making Changes:**
   - Make small, focused commits
   - Test frequently
   - Update documentation alongside code
   - Add tests for new functionality

3. **Before Committing:**
   - Run full test suite
   - Review all changes
   - Update relevant documentation
   - Verify no secrets or unnecessary files

4. **After Committing:**
   - Push to remote repository
   - Verify CI/CD passes (if configured)
   - Update related documentation if needed

---

## Questions or Issues?

For issues with:
- **Claude Code:** `/help` command or https://github.com/anthropics/claude-code/issues
- **Tests:** Check `Web Crawler/Tester/README.md`
- **macOS Commands:** See `Web Crawler/Tester/MACOS_QUICK_REFERENCE.md`

---

## Repository Maintenance

### Regular Tasks

- Keep dependencies updated
- Run test suite periodically
- Review and update documentation
- Clean up old branches
- Remove stale files

### File Organization

- Keep related files together
- Use descriptive directory names
- Avoid deep nesting
- Document directory structure in READMEs

---

*Last Updated: 2026-02-26*
*This file should be updated when project standards or workflows change*
