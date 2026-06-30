**Prompt:**
Always ensure that any Python command is run inside an activated virtual environment (`.venv`).
Before running a Python command, activate the virtual environment using:

```bash
source .venv/bin/activate
```

Use `uv` to run installations, tests, and other Python commands to ensure they are executed within the virtual environment.

For example, to install a package, use:

```bash
uv pip install <package-name>
```