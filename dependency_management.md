# Dependency Management Guide

This project uses `pip-tools` to manage Python dependencies. Here's how to use it effectively.

## Initial Setup

1. Make sure your virtual environment is activated:
   ```bash
   .venv\Scripts\activate  # Windows
   # OR
   source .venv/bin/activate  # Unix/MacOS
   ```

2. Install pip-tools:
   ```bash
   pip install pip-tools
   ```

## Managing Dependencies

### Adding New Dependencies

1. Add the dependency to `requirements.in` (not directly to requirements.txt)
2. Run pip-compile to update requirements.txt:
   ```bash
   pip-compile requirements.in
   ```
3. Sync your environment with the new requirements:
   ```bash
   pip-sync
   ```

### Updating Dependencies

To update all dependencies to their latest versions:
```bash
pip-compile --upgrade requirements.in
pip-sync
```

To update a specific package:
```bash
pip-compile --upgrade-package openai requirements.in
pip-sync
```

### Docker Builds

When building Docker images, continue to use the generated `requirements.txt` file in your Dockerfile:
```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

## Best Practices

1. Never edit `requirements.txt` directly; always update `requirements.in` and recompile
2. Keep development dependencies separate in a `dev-requirements.in` file
3. Run `pip-sync` after pulling changes from version control
4. Commit both `requirements.in` and `requirements.txt` to version control

## Additional Commands

### Generate requirements with hashes (for security)
```bash
pip-compile --generate-hashes requirements.in
```

### Create separate dev requirements
```bash
pip-compile dev-requirements.in
```

### Combine requirements
```bash
pip-sync requirements.txt dev-requirements.txt
``` 