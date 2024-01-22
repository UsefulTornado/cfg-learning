import re

from .cfg import Nonterminal, Rule, Terminal, CFGrammar


class CFGParser:
    pattern = re.compile(r"(\[\[[a-zA-Z]+[0-9]*\]\])|([a-zA-Z]|[0-9])")

    def _parse_rule(self, line):
        splitted = self.pattern.split(line)
        symbols = [sym for sym in splitted if sym and self.pattern.match(sym)]
        left = Nonterminal(symbols[0])
        right = []
        for sym in symbols[1:]:
            if sym[0] == "[":
                right.append(Nonterminal(sym))
            else:
                right.append(Terminal(sym))

        return Rule(left, right)

    def parse_grammar(self, path):
        with open(path, mode="r", encoding="utf-8") as file:
            lines = file.readlines()
        return CFGrammar(rules=[self._parse_rule(line) for line in lines])
