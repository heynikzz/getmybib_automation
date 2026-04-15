# Selenium Pytest Automation Framework

Scalable UI automation framework built with:
- Python
- Selenium
- Pytest
- Page Object Model (POM)

## Project Structure

```text
getmybib_automation/
├── conftest.py
├── pytest.ini
├── .env.example
├── locators/
│   ├── __init__.py
│   └── login_page_locators.py
├── pages/
│   ├── __init__.py
│   ├── base_page.py
│   └── login_page.py
├── tests/
│   ├── __init__.py
│   ├── test_login.py
│   └── test_login_page.py
└── utils/
    ├── __init__.py
    ├── config.py
    ├── driver_factory.py
    └── logger.py
```

## Setup

1. Create and activate virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create environment file:

```bash
cp .env.example .env
```

## Run Tests

```bash
pytest
```

Example overrides:

```bash
pytest --browser=firefox --headless
pytest --base-url=https://www.saucedemo.com
```
