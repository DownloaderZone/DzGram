#!/usr/bin/env python3
"""Generate the Sphinx API reference pages for the whole DzGram package.

Walk the `pyrogram` package and emit one `.rst` page per module under
`docs/source/api/`. Run from the `docs` directory:

    python generate_api.py
"""

import ast
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "source"
PKG = ROOT.parent / "pyrogram"

SKIP_MODULES = {"__init__.py", "__pycache__"}


def write(path: pathlib.Path, content: str):
    """Write *content* only when it changed.

    Sphinx uses the modification time of a source file to decide what needs to
    be rebuilt.  Rewriting every generated page therefore turned even a small
    documentation edit into a full API rebuild.  Keeping unchanged files in
    place makes subsequent builds genuinely incremental.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def get_classes(source: pathlib.Path):
    """Return the list of top-level class names defined in a module."""
    tree = ast.parse(source.read_text(encoding="utf-8"))
    return [n.name for n in tree.body if isinstance(n, ast.ClassDef)]


def get_methods(source: pathlib.Path):
    """Return the list of `async def` method names defined in a module."""
    tree = ast.parse(source.read_text(encoding="utf-8"))
    methods = []
    for n in tree.body:
        if isinstance(n, ast.ClassDef):
            for m in n.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(m.name)
    return methods


def header(title: str) -> str:
    return title + "\n" + "=" * len(title) + "\n\n"


def autoclass_page(title: str, module: str, names, opts=":members:\n    :member-order: bysource"):
    body = header(title)
    for name in names:
        body += f".. autoclass:: {module}.{name}\n    {opts}\n\n"
    return body


def autofunction_page(title: str, names):
    body = header(title)
    for name in names:
        # Client methods are bound methods, not module-level functions.
        # automethod avoids Sphinx repeatedly treating the entire Client API
        # as a function during autodoc resolution.
        body += f".. automethod:: pyrogram.Client.{name}\n\n"
    return body


def toctree_page(title: str, entries, caption=None, hidden=False):
    body = header(title)
    body += ".. toctree::\n    :maxdepth: 1\n"
    if hidden:
        body += "    :hidden:\n"
    body += "\n"
    for entry in entries:
        body += f"    {entry}\n"
    return body


def generate_methods():
    base = SRC / "api" / "methods"
    categories = []

    for cat in sorted(p for p in (PKG / "methods").iterdir() if p.is_dir() and p.name != "__pycache__"):
        pages = []
        for py in sorted(cat.glob("*.py")):
            if py.name in SKIP_MODULES:
                continue
            methods = get_methods(py)
            if not methods:
                continue
            for method in methods:
                stem = method
                write(base / cat.name / f"{stem}.rst", autofunction_page(py.stem, [method]))
                pages.append(stem)

        if not pages:
            continue

        write(base / cat.name / "index.rst", toctree_page(cat.name.capitalize(), pages, hidden=True))
        categories.append(cat.name)

    write(base / "index.rst", toctree_page("Methods", [f"{c}/index" for c in categories]))


def generate_types():
    base = SRC / "api" / "types"
    categories = []

    for cat in sorted(p for p in (PKG / "types").iterdir() if p.is_dir() and p.name != "__pycache__"):
        if cat.name == "pyromod":
            continue
        pages = []
        for py in sorted(cat.glob("*.py")):
            if py.name in SKIP_MODULES or py.name == "list.py" or py.name == "object.py":
                continue
            classes = get_classes(py)
            if not classes:
                continue
            for class_name in classes:
                stem = class_name
                write(
                    base / cat.name / f"{stem}.rst",
                    autoclass_page(class_name, f"pyrogram.types.{cat.name}.{py.stem}", [class_name]),
                )
                pages.append(stem)

        if not pages:
            continue

        write(base / cat.name / "index.rst", toctree_page(cat.name.replace("_", " ").capitalize(), pages, hidden=True))
        categories.append(cat.name)

    write(base / "index.rst", toctree_page("Types", [f"{c}/index" for c in categories]))


def generate_enums():
    base = SRC / "api" / "enums"
    pages = []

    for py in sorted((PKG / "enums").glob("*.py")):
        if py.name in SKIP_MODULES:
            continue
        classes = get_classes(py)
        if not classes:
            continue
        for class_name in classes:
            stem = class_name
            write(base / f"{stem}.rst", autoclass_page(class_name, f"pyrogram.enums.{py.stem}", [class_name]))
            pages.append(stem)

    write(base / "index.rst", toctree_page("Enums", pages))


def generate_handlers():
    base = SRC / "api" / "handlers"
    pages = []

    for py in sorted((PKG / "handlers").glob("*.py")):
        if py.name in SKIP_MODULES:
            continue
        classes = get_classes(py)
        if not classes:
            continue
        for class_name in classes:
            stem = class_name
            write(
                base / f"{stem}.rst",
                autoclass_page(class_name, f"pyrogram.handlers.{py.stem}", [class_name]),
            )
            pages.append(stem)

    write(base / "index.rst", toctree_page("Handlers", pages))


def get_imported_names(source: pathlib.Path):
    """Return the class names imported by `from .<module> import <name>` lines."""
    names = []
    tree = ast.parse(source.read_text(encoding="utf-8"))
    for n in tree.body:
        if isinstance(n, ast.ImportFrom) and n.level == 1 and n.module:
            for alias in n.names:
                if not alias.asname:
                    names.append(alias.name)
    return names


def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def generate_raw():
    base = SRC / "api" / "raw"

    def pkg_page(module, title, members=None, extra=""):
        if members is not None:
            listing = ".. automodule:: " + module + "\n    :no-index:\n    :members: " + ", ".join(members) + "\n\n"
            return header(title) + listing + extra
        return (
            header(title)
            + f".. automodule:: {module}\n    :members:\n    :undoc-members:\n    :imported-members:\n\n"
            + extra
        )

    def gen(kind, title, chunk):
        root = PKG / "raw" / kind
        out = base / kind
        pages = []
        for cat in sorted(p for p in root.iterdir() if p.is_dir() and p.name != "__pycache__"):
            pages.append(cat.name)
            write(
                out / f"{cat.name}.rst",
                pkg_page(f"pyrogram.raw.{kind}.{cat.name}", f"{title}: {cat.name}"),
            )
        init = root / "__init__.py"
        if init.exists():
            names = [n for n in get_imported_names(init)]
            for i, part in enumerate(chunked(names, chunk)):
                pages.append(f"index-part-{i}")
                write(
                    out / f"index-part-{i}.rst",
                    pkg_page(f"pyrogram.raw.{kind}", f"{title} (part {i + 1})", members=part),
                )
        toctree = ".. toctree::\n    :maxdepth: 1\n    :hidden:\n\n" + "".join(f"    {c}\n" for c in pages)
        write(out / "index.rst", header(title) + toctree)

    gen("types", "Raw Types", chunk=120)
    gen("functions", "Raw Functions", chunk=120)
    gen("base", "Raw Base", chunk=120)

    write(
        base / "index.rst",
        header("Raw API")
        + "DzGram exposes the entire low-level Telegram API (MTProto schema) "
        "under the ``pyrogram.raw`` package. These objects are produced by the "
        "TL compiler and mirror the Telegram API scheme 1:1.\n\n"
        ".. toctree::\n    :maxdepth: 1\n\n"
        "    types/index\n"
        "    functions/index\n"
        "    base/index\n",
    )


def generate_misc():
    base = SRC / "api"

    write(
        base / "client.rst",
        header("Client")
        + ".. autoclass:: pyrogram.Client\n    :no-members:\n\n"
        "The :class:`~pyrogram.Client` class inherits all methods documented in "
        "the :doc:`methods/index` section.\n",
    )

    write(
        base / "filters" / "index.rst",
        header("Filters")
        + ".. automodule:: pyrogram.filters\n    :members:\n    :undoc-members:\n",
    )

    for module, title in [
        ("dispatcher", "Dispatcher"),
        ("sync", "Sync"),
        ("utils", "Utils"),
    ]:
        write(
            base / f"{module}.rst",
            header(title) + f".. automodule:: pyrogram.{module}\n    :members:\n",
        )

    write(
        base / "errors" / "exceptions.rst",
        header("Exceptions")
        + ".. automodule:: pyrogram.errors.exceptions\n    :members:\n    :undoc-members:\n",
    )
    write(
        base / "errors" / "rpc_error.rst",
        header("RPC Errors")
        + "Every possible Telegram API error, one class per error. Errors are "
        "subclasses of their :doc:`exceptions` categories.\n\n"
        ".. automodule:: pyrogram.errors.rpc_error\n    :members:\n    :undoc-members:\n",
    )
    write(
        base / "errors" / "index.rst",
        toctree_page("Errors", ["exceptions", "rpc_error"]),
    )

    storage_pages = []
    for py in sorted((PKG / "storage").glob("*.py")):
        if py.name in SKIP_MODULES:
            continue
        classes = get_classes(py)
        if not classes:
            continue
        for class_name in classes:
            stem = class_name
            write(
                base / "storage" / f"{stem}.rst",
                autoclass_page(class_name, f"pyrogram.storage.{py.stem}", [class_name]),
            )
            storage_pages.append(stem)
    write(base / "storage" / "index.rst", toctree_page("Storage", storage_pages))

    session_pages = []
    for py in sorted((PKG / "session").glob("*.py")):
        if py.name in SKIP_MODULES:
            continue
        classes = get_classes(py)
        if not classes:
            continue
        for class_name in classes:
            stem = class_name
            write(
                base / "session" / f"{stem}.rst",
                autoclass_page(class_name, f"pyrogram.session.{py.stem}", [class_name]),
            )
            session_pages.append(stem)
    write(base / "session" / "index.rst", toctree_page("Session", session_pages))

    write(
        base / "index.rst",
        header("API Reference")
        + ".. toctree::\n    :maxdepth: 1\n\n"
        "    client\n"
        "    methods/index\n"
        "    types/index\n"
        "    bound-methods/index\n"
        "    enums/index\n"
        "    filters/index\n"
        "    handlers/index\n"
        "    errors/index\n"
        "    storage/index\n"
        "    session/index\n"
        "    dispatcher\n"
        "    sync\n"
        "    utils\n",
    )


def generate_bound_methods():
    """Curated page documenting the most important bound methods."""
    types_list = [
        "Message",
        "CallbackQuery",
        "InlineQuery",
        "User",
        "Chat",
        "ChatMember",
        "MessageReactionUpdated",
    ]
    body = header("Bound Methods")
    body += (
        "Bound methods are methods attached to the objects returned by the API "
        "(e.g. :meth:`~pyrogram.types.Message.reply`), which allow you to act "
        "on them without passing the client explicitly.\n\n"
        "They are documented together with their parent type in the "
        ":doc:`../types/index` reference.\n\n"
        ".. autosummary::\n    :nosignatures:\n\n"
    )
    for name in types_list:
        body += f"    pyrogram.types.{name}\n"
    write(SRC / "api" / "bound-methods" / "index.rst", body)


def main():
    generate_methods()
    generate_types()
    generate_enums()
    generate_handlers()
    generate_raw()
    generate_misc()
    generate_bound_methods()
    print("API reference generated under", SRC / "api")


if __name__ == "__main__":
    main()
