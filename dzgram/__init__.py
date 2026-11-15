#  DzGram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2024-present Downloader Zone <https://github.com/DownloaderZone>
#
#  This file is part of DzGram, a fork of Pyrogram.
#
#  DzGram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  DzGram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with DzGram.  If not, see <http://www.gnu.org/licenses/>.

"""Import alias for DzGram.

``dzgram`` maps 1:1 onto the ``pyrogram`` package, so both import styles work:

    from pyrogram import Client  # Pyrogram-compatible
    from dzgram import Client    # DzGram-native

Submodules are aliased too (``dzgram.types``, ``dzgram.raw``, ...) and resolve
to the *same* module objects as their ``pyrogram.*`` counterparts, so there is
exactly one copy of every class in memory.
"""

import importlib
import importlib.util
import sys

import pyrogram

_PREFIX = __name__  # "dzgram"
_REAL = "pyrogram"


class _AliasLoader:
    """Loader that reuses the real ``pyrogram`` module for a ``dzgram`` name."""

    def create_module(self, spec):
        real = importlib.import_module(_REAL + spec.name[len(_PREFIX):])
        sys.modules[spec.name] = real
        return real

    def exec_module(self, module):
        # The real module was already executed when it was imported above.
        pass


class _AliasFinder:
    """Meta-path finder redirecting every ``dzgram.*`` import to ``pyrogram.*``."""

    def find_spec(self, fullname, path=None, target=None):
        if not fullname.startswith(_PREFIX + ".") or fullname in sys.modules:
            return None

        real_name = _REAL + fullname[len(_PREFIX):]
        try:
            importlib.import_module(real_name)
        except ImportError:
            return None

        return importlib.util.spec_from_loader(fullname, _AliasLoader())


sys.meta_path.insert(0, _AliasFinder())

# Rebind ``dzgram`` to the real pyrogram module: everything top-level
# (Client, filters, types, enums, ...) is shared with ``import pyrogram``.
sys.modules[__name__] = pyrogram
