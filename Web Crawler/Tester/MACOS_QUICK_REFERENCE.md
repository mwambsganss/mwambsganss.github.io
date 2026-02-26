# 🚀 Quick Reference - macOS Commands

## 💡 Important: Use `pip3` and `python3` on macOS

On macOS, the commands are:
- ❌ `pip` → ✅ `pip3`
- ❌ `python` → ✅ `python3`

---

## 📦 Installation (Now Complete!)

✅ **Dependencies Installed Successfully!**

All these packages are now installed:
- pytest 9.0.2 (testing framework)
- pytest-cov 7.0.0 (coverage)
- pytest-mock 3.15.1 (mocking)
- psutil 7.2.2 (memory profiling)
- beautifulsoup4 (HTML parsing)
- requests (HTTP library)
- faker 40.5.1 (test data)
- memory-profiler 0.61.0 (performance)

---

## 🎯 Running Tests - Use These Commands

### Navigate to Test Directory
```bash
cd "/Users/V5X8512/Library/CloudStorage/OneDrive-EliLillyandCompany/Documents/Repos/MWambsganss/mwambsganss.github.io/Web Crawler/Tester"
```

### Run Tests (Use python3, not python)
```bash
# Quick validation
python3 quick_start.py

# Run all tests
pytest -v

# Run with coverage
./run_tests.sh coverage

# Run specific test category
pytest -m unit          # Unit tests only
pytest -m "not slow"    # Exclude slow tests
pytest -m integration   # Integration tests

# Run specific tests
pytest -k "sanitize"    # All sanitization tests
pytest -k "url"         # All URL tests
```

---

## 🔧 Useful Commands

### Check Installations
```bash
python3 --version       # Check Python version
pip3 --version         # Check pip version
pip3 list | grep pytest # List pytest packages
```

### Update pip (Optional)
```bash
pip3 install --upgrade pip
```

### Install New Packages
```bash
pip3 install package-name
```

---

## 📝 Created Files You Can Use

### 1. Automated Installation Script
```bash
./install_dependencies.sh
```
This script automatically:
- Detects Python and pip
- Upgrades pip
- Installs all dependencies
- Verifies installation
- Shows helpful messages

### 2. Quick Start Script
```bash
python3 quick_start.py
```
Runs a few quick tests to verify everything works.

### 3. Test Runner Script
```bash
./run_tests.sh all        # All tests
./run_tests.sh unit       # Unit tests only
./run_tests.sh coverage   # With coverage report
./run_tests.sh performance # Performance tests
```

---

## 🎓 Next Steps

1. ✅ **Dependencies installed** - Already done!

2. **Run quick validation:**
   ```bash
   cd "/Users/V5X8512/Library/CloudStorage/OneDrive-EliLillyandCompany/Documents/Repos/MWambsganss/mwambsganss.github.io/Web Crawler/Tester"
   python3 quick_start.py
   ```

3. **Run all tests:**
   ```bash
   pytest -v
   ```

4. **Generate coverage report:**
   ```bash
   ./run_tests.sh coverage
   ```

5. **View coverage:**
   ```bash
   open coverage_report/index.html
   ```

---

## 🐛 Troubleshooting

### If you get "command not found: pytest"
Use Python module syntax:
```bash
python3 -m pytest -v
```

### If you get "command not found: pip"
Use pip3:
```bash
pip3 install package-name
```

### If you need to reinstall everything
```bash
./install_dependencies.sh
```

Or manually:
```bash
pip3 install -r test_requirements.txt
```

---

## 📂 File Locations

**Test Suite Directory:**
```
/Users/V5X8512/Library/CloudStorage/OneDrive-EliLillyandCompany/Documents/Repos/MWambsganss/mwambsganss.github.io/Web Crawler/Tester/
```

**Main Crawler:**
```
/Users/V5X8512/Library/CloudStorage/OneDrive-EliLillyandCompany/Documents/Repos/MWambsganss/mwambsganss.github.io/Web Crawler/web_crawler.py
```

---

## ✅ You're All Set!

Everything is installed and ready to go. Start testing with:

```bash
cd "/Users/V5X8512/Library/CloudStorage/OneDrive-EliLillyandCompany/Documents/Repos/MWambsganss/mwambsganss.github.io/Web Crawler/Tester"
python3 quick_start.py
```

🎉 Happy Testing!
