# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2016-2021 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <https://www.gnu.org/licenses/>.

"""Backend-independent qute://* code.

Module attributes:
    pyeval_output: The output of the last :pyeval command.
    _HANDLERS: The handlers registered via decorators.
"""

import html
# import json
# import os
# import time
# import textwrap
# import urllib
# import collections
# import secrets
# from typing import TypeVar, Callable, Dict, List, Optional, Union, Sequence, Tuple

from PyQt5.QtCore import QUrl

# import qutebrowser
# from qutebrowser.browser import pdfjs, downloads, history
# from qutebrowser.config import config, configdata, configexc
from qutebrowser.utils import log
# from qutebrowser.qt import sip
import ignition

css = """
body {
margin:40px auto;
max-width:650px;
line-height:1.6;
font-size:18px;
color:#444;
padding:0 10px;
}
h1,h2,h3 {
    line-height:1.2;
}
ul {
    list-style: none;
    margin-left: 0;
    padding-left: 0;
}

li {
    padding-left: 1em;
    text-indent: -1em;
}

li:before {
    font-weight: bold;
    content: "*";
    padding-right: 5px;
}

pre {
    line-height: initial;
    font-family: menlo,lucida console,consolas,courier new,courier,monospace;
}
"""


def html_from_gemtext(gemtext):
    body = ''
    body += '<html><meta charset="utf-8" />'
    body += f'<head><style>{css}</style></head>'
    body += '<body>'
    verbatim = False
    inlist = False
    for line in gemtext.split('\n'):
        escaped = html.escape(line, quote=True)
        if line.startswith('```'):
            if not verbatim:
                body += '<pre>'
            else:
                body += '</pre>'
            verbatim = not verbatim
            continue
        if line.startswith('*'):
            if not inlist:
                inlist = True
                body += '<ul>'
            body += f'<li>{escaped[1:]}</li>'
            continue
        elif inlist:
            inlist = False
            body += '</ul>\n'
        if verbatim:
            body += html.escape(line)
        elif line.startswith('#'):
            header_level = 0
            for i in line:
                if i == '#':
                    header_level += 1
                else:
                    break
            body += f'<h{header_level}>{escaped}</h{header_level}>'
        elif line.startswith('>'):
            body += f'<blockquote>{escaped}</blockquote>'
        elif line.startswith('=>'):
            link_text = line[2:].strip()
            body += '=&gt '
            if len(link_text.split()) >= 2:
                link = link_text.split()[0]
                desc = html.escape(' '.join(link_text.split()[1:]))
                body += f'<a href="{link}">{desc}</a><br>'
            else:
                link = link_text
                body += f'<a href="{link}">{link}</a><br>'
        else:
            body += escaped + '<br>'
        body += '\n'
    body += '</html></body>'
    return body


def data_for_url(url: QUrl):
    path = url.url()
    response = ignition.request(path)

    data = response.data()
    log.network.debug(data)
    log.network.debug(html.escape(data))
    html_text = html_from_gemtext(data)
    return 'text/html', html_text.encode('utf-8')
