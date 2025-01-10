from __future__ import annotations

import hashlib
import os.path
import re
from typing import Any
from typing import Dict

import pygments
import pygments.formatters
import pygments.lexers
import pygments.util
from pwnlib.lexer import PwntoolsLexer

import pwndbg
import pwndbg.lib.tempfile
from pwndbg.color import disable_colors
from pwndbg.color import message
from pwndbg.color import theme

pwndbg.config.add_param("syntax-highlight", True, "Source code / assembly syntax highlight")
style = theme.add_param(
    "syntax-highlight-style",
    "monokai",
    "Source code / assembly syntax highlight stylename of pygments module",
)

formatter = pygments.formatters.Terminal256Formatter(style=str(style))
pwntools_lexer = PwntoolsLexer()
lexer_cache: Dict[str, Any] = {}

SYNTAX_HIGHLIGHT_CACHEDIR = pwndbg.lib.tempfile.cachedir("syntax-highlight")


@pwndbg.config.trigger(style)
def check_style() -> None:
    global formatter
    try:
        formatter = pygments.formatters.Terminal256Formatter(style=str(style))

        # Reset the highlighted source cache
        from pwndbg.commands.context import get_highlight_source

        get_highlight_source.cache.clear()
    except pygments.util.ClassNotFound:
        print(
            message.warn(f"The pygment formatter style '{style}' is not found, restore to default")
        )
        style.revert_default()


def syntax_highlight(code: str, filename: str = ".asm") -> str:
    # No syntax highlight if pygment is not installed
    if disable_colors:
        return code

    filename = os.path.basename(filename)

    lexer = lexer_cache.get(filename, None)
    print("syntax highlight", lexer, filename, lexer_cache)

    # If source code is asm, use our customized lexer.
    # Note: We can not register our Lexer to pygments and use their APIs,
    # since the pygment only search the lexers installed via setuptools.
    if not lexer:
        for glob_pat in PwntoolsLexer.filenames:
            pat = "^" + glob_pat.replace(".", r"\.").replace("*", r".*") + "$"
            if re.match(pat, filename):
                lexer = pwntools_lexer
                break

    if not lexer:
        try:
            # Loading a lexer is slow and often done (and is pickable), so let's cache it
            # Note that although guess_lexer_for_filename uses both the
            # filename and code, our lexer_cache (above) only uses the filename
            # as the key. Therefore it is safe for us to use just the filename
            # as the key to this disk cache.
            key = hashlib.sha1(filename.encode("utf-8")).hexdigest()
            cache_file = os.path.join(SYNTAX_HIGHLIGHT_CACHEDIR, key)
            if os.path.exists(cache_file):
                # Cache hit
                with open(cache_file, "r") as f:
                    lexer_name = f.read()
                    lexer = pygments.lexers.get_lexer_by_name(lexer_name)
                    print("cache hit", lexer)
            else:
                # Cache miss
                lexer = pygments.lexers.guess_lexer_for_filename(filename, code, stripnl=False)
                with open(cache_file, "w") as f:
                    f.write(lexer.name)
                    print("cache miss", lexer.name, lexer)
        except pygments.util.ClassNotFound:
            # no lexer for this file or invalid style
            pass

    if lexer:
        lexer_cache[filename] = lexer

        code = pygments.highlight(code, lexer, formatter).rstrip()

    return code
