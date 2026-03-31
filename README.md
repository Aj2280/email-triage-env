# Email Triage OpenEnv

A real-world OpenEnv environment for training and evaluating agents on email triage tasks.

## Overview

This environment simulates an email triage task where an agent must process incoming emails, categorize them, and perform actions like replying, forwarding, or archiving.

## Action Space

- `list_emails()`: List all emails in the inbox.
- `get_email(email_id)`: Get the details of a specific email.
- `reply_email(email_id, body)`: Reply to an email.
- `forward_email(email_id, forward_to, body)`: Forward an email.
- `archive_email(email_id)`: Archive an email.
- `mark_as_read(email_id)`: Mark an email as read.

## Observation Space

- Current inbox state.
- Detail of the selected email.
- Action results.

## Tasks

1. **Easy**: Mark a specific email as read.
2. **Medium**: Reply to a customer query with a predefined template.
3. **Hard**: Triage multiple emails, forwarding urgent ones and archiving spam.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

## Running Evaluation

```bash
python inference.py --base-url http://localhost:8000
```
