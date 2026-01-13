#!/usr/bin/env python3
import subprocess
import re
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent
COMMANDS_DIR = ROOT / "commands"

CLI = "quarto"
BOOK_TITLE = "Quarto CLI Manual"

# -----------------------------
# Utilities
# -----------------------------

def run(cmd):
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)

def get_help(args):
    return run([CLI, *args, "--help"]).strip()

def discover_commands():
    """
    Extract subcommands from `quarto --help`
    """
    help_text = get_help([])
    commands = []
    for line in help_text.splitlines():
        m = re.match(r"\s{2}([a-z][a-z-]+)\s+", line)
        if m:
            commands.append(m.group(1))
    return sorted(set(commands))

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def fenced(text):
    return f"```\n{text}\n```"

# -----------------------------
# Page generators
# -----------------------------

def root_page():
    help_text = get_help([])
    return f"""

---
title: "{CLI}"
---

## NAME
    
{CLI} - scientific and technical publishing system
    
## SYNOPSIS
    
```bash
{CLI} [COMMAND] [OPTIONS]
```
   
## DESCRIPTION
    
{fenced(help_text)}
    
## SEE ALSO
{see_also_links()}
    
"""

def command_page(cmd):
    help_text = get_help([cmd])
    first_line = help_text.splitlines()[0]
    return f"""
    ---
    title: "{CLI} {cmd}"
    ---
    
    ## NAME
    
    {CLI} {cmd} - {first_line}
    
    ## SYNOPSIS
    
    ```bash
    {CLI} {cmd} [OPTIONS]
    ```

    ## DESCRIPTION

    {fenced(help_text)}

    ## SEE ALSO

    * [{CLI}]({CLI}.qmd)
    """

def see_also_links():
    links = []
    for c in COMMANDS:
        links.append(f"- [{CLI} {c}](commands/{CLI}-{c}.qmd)")
        return "\n".join(links)

def write_index():
    today = date.today().isoformat()
    content = f"""
    ---
    title: "{BOOK_TITLE}"
    ---
    
    Generated on **{today}** from live `{CLI} --help` output.
    This book contains a complete command-line reference
    formatted in the style of Unix manual pages.
    
    ## Commands

    {see_also_links()}
    """
    write(ROOT / "index.qmd", content)

# -----------------------------
# Main
# -----------------------------

if name == "main":
    print("Discovering commands...")
    COMMANDS = discover_commands()


print(f"Found commands: {', '.join(COMMANDS)}")

COMMANDS_DIR.mkdir(exist_ok=True)

print("Generating root man page...")
write(COMMANDS_DIR / "quarto.qmd", root_page())

for cmd in COMMANDS:
    print(f"Generating man page: {cmd}")
    write(COMMANDS_DIR / f"quarto-{cmd}.qmd", command_page(cmd))

print("Writing book config...")
write_quarto_yml()
write_index()
print("✅ Done. Run: quarto render")
