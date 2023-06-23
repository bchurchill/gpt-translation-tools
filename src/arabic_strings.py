
import re

class ArabicStrings:

    def __init__(self, logger):
        self.logger = logger

    # how many edits to substring are required to make it a substring of string?
    def substring_distance(self, substring, string):
        m = len(string)
        n = len(substring)
        
        # Create a 2D array to store the minimum edit distances
        min_dist = [[0 for _ in range(n+1)] for _ in range(m+1)]
        indexes = [[0 for _ in range(n+1)] for _ in range(m+1)]

        for i in range(m+1):
            for j in range(n+1):
                if i == 0:
                    min_dist[i][j] = j
                    indexes[i][j] = 0
                    continue

                if j == 0:
                    min_dist[i][j] = 0
                    indexes[i][j] = i
                    continue

                if string[i-1] == substring[j-1]:
                    insertion_cost = 0
                else:
                    insertion_cost = 1

                options = [
                    (insertion_cost + min_dist[i-1][j-1], indexes[i-1][j-1]),
                    (1 + min_dist[i-1][j], 1 + indexes[i-1][j]),
                    (1 + min_dist[i][j-1], indexes[i][j-1])
                ]

                options = sorted(options)
                min_dist[i][j] = options[0][0]
                indexes[i][j] = options[0][1]

                 
        best = float('inf')
        best_index = 0
        for i in range(m+1):
            if min_dist[i][n] < best:
                best = min_dist[i][n]
                best_index = indexes[i][n]

        self.logger.debug("")
        self.logger.debug("")
        self.logger.debug(f"string={string} substring={substring}")
        self.logger.debug("Costs")
        for r in min_dist:
            self.logger.debug("  " + str(r))
        self.logger.debug("Indexes")
        for r in indexes:
            self.logger.debug("  " + str(r))

        return best, best_index

    def strip_diacritical(self, text):
        # Define a pattern for common diacritical marks in Persian and Arabic text
        # this takes out vowel markings, tashteeds, tanveens, etc.
        text = re.sub(r'[\u0640\u064B-\u065f\u0670]', '', text)

        # Replace all whitespace with a single space
        text = re.sub(r'\s+', ' ', text)

        # Replace Persian kaf with Arabic kaf
        text = re.sub(r'[\u06A9]', '\u0643', text)

        # Change all alephs to the same standard alephs
        text = re.sub(r'[\u0622\u0623\u0625\u0671-\u0673]', '\u0627', text)

        # Change all ye and alif maksuras
        text = re.sub(r'[\u06CC\u0649]', '\u064a', text)

        # Fix all the Hes and teh-marbuta
        text = re.sub(r'[\u06C1\u06D5\u06C0\u06C2\u0629\u06C3]', '\u0647', text)

        # Replace Persian lam (not sure if this is even used)
        text = re.sub(r'[\u06B5]', '\u0644', text)

        # Standardize hamzas
        text = re.sub(r'[\u0674\u0624\u0626\u0675]', '\u0621', text)

        # Waw with hamza -> waw
        text = re.sub(r'[\u0624]','\u0648', text)

        # ya with hamza -> ya
        text = re.sub(r'[\u0626]','\u064A', text)

        # lam-aleph combos
        text = re.sub(r'[\uFEF5-\uFEFC]','\u0644\u0627', text)

        # Strip leading and trailing spaces
        text = text.strip()

        return text


