import os
import sys
import traceback

class Input:

    def __init__(self, args, logger):
        self.args = args
        self.logger = logger

    def get_text_lines(self):
        return self._extract_text()

    def get_text(self):
        return '\n'.join(self._extract_text())

    # Opens the input file and pulls out the relevant lines
    def _extract_text(self):
        try:
            with open(self.args.input, 'r') as f:
                lines = f.readlines()

            if not self.args.lines:
                return lines

            lines = self._filter_lines(lines)

            return lines
        except Exception as e:
            self.logger.fatal_error(e)

    def _filter_lines(self, lines):
        if not self.args.lines:
            raise ValueError("Line numbers or range must be provided")
            
        filtered_lines = []
        parts = self.args.lines.split(',')

        for part in parts:
            if '-' in part:
                start, end = map(int, part.split('-'))
                if start < 1 or end > len(lines) or start > end:
                    raise ValueError(f"Invalid line range: {part}")
                filtered_lines.extend(lines[start-1:end])
            else:
                n = int(part)
                if n < 1 or n > len(lines):
                    raise ValueError(f"Invalid line number: {part}")
                filtered_lines.append(lines[n-1])

        return filtered_lines


