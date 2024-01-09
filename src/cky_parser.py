from .cfg import Terminal, CFGrammar


class CKYParser:
    def __init__(self, grammar):
        self.grammar = grammar

    def accepts(self, word):
        chars = list(word)
        grammar = CFGrammar.to_chomsky_normal_form(self.grammar)
        nonterminals = [grammar.start] + list(grammar.nonterminals - {grammar.start})
        table = [
            [[False for _ in range(len(nonterminals))] for _ in range(len(chars))]
            for _ in range(len(chars))
        ]

        for char_idx, char in enumerate(chars):
            for rule in grammar.rules:
                if len(rule.right) == 1 and rule.right[0] == Terminal(char):
                    table[0][char_idx][nonterminals.index(rule.left)] = True

        for l in range(1, len(chars)):
            for s in range(len(chars) - l):
                for p in range(l):
                    for rule in grammar.rules:
                        if len(rule.right) == 2:
                            if (
                                table[p][s][nonterminals.index(rule.right[0])]
                                and table[l - p - 1][s + p + 1][
                                    nonterminals.index(rule.right[1])
                                ]
                            ):
                                table[l][s][nonterminals.index(rule.left)] = True

        return table[len(chars) - 1][0][0]
