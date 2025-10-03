# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kakeibo (家計簿) is a serverless application that transfers messages from Slack to Google Sheets for household accounting. It runs on AWS Lambda, triggered by EventBridge every 10 minutes.

## Commands

### Development
- `make run` - Run the application locally
- `make test` - Run all tests with coverage report (HTML output)
- `make lint` - Run all code quality checks (formatting, linting, type checking)

### Testing
- `rye run pytest tests/test_specific.py::TestClass::test_method` - Run a single test
- `rye run pytest -k "test_name"` - Run tests matching a pattern
- `rye run pytest -x` - Stop on first failure

### Deployment
- `make docker-build` - Build Lambda Docker image
- `make docker-push` - Push image to AWS ECR
- `make lambda-test` - Test Lambda function locally
- `make lambda-set-env` - Update Lambda environment variables from .env file

## Architecture

The codebase follows Clean Architecture principles:

```
src/kakeibo/
├── lambda.py          # AWS Lambda handler
├── main.py           # Application bootstrap and dependency injection
├── usecase.py        # Business logic orchestration
├── service.py        # Application services with Protocol interfaces
├── slack.py          # Slack API integration
├── google_sheet.py   # Google Sheets API integration
└── config.py         # Pydantic configuration models
```

### Key Design Patterns
1. **Protocol-based Dependency Injection**: Service interfaces defined with Python Protocols enable testability
2. **Pydantic Configuration**: All config validated through Pydantic models
3. **Structured Logging**: Uses structlog for consistent log formatting

### Data Flow
1. Lambda/main triggered → 2. Fetch Slack messages → 3. Filter by time/content → 4. Transform to sheet format → 5. Append to Google Sheet

### Environment Configuration
Required environment variables:
- `SLACK_API_KEY`: Slack API token
- `SLACK_CHANNEL_ID`: Target Slack channel
- `SPREADSHEET_TITLE`: Google Sheet name
- `CLIENT_SECRET_JSON`: Google API service account credentials

## Testing Approach

- Unit tests in `tests/` mirror source structure
- Use `pytest-mock` for mocking external dependencies
- Use `freezegun` for time-based testing
- Aim for high coverage (currently configured for 85% minimum)