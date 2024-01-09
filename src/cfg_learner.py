from .cfg import Terminal, Nonterminal, CongruentClass, Rule, CFGrammar
from .cky_parser import CKYParser
from .graph import Graph
from .utils import to_iterable

from collections import defaultdict
from itertools import product


class CFGLearner:
    """
    A class that learns Context-free grammar from a set of words
    using a strong learning algorithm for substitutable context-free languages
    by A. Clark.
    """

    def __init__(self):
        ...

    def _get_substrings(self, words: str | list[str] | set[str]) -> set[str]:
        return {
            word[i:j]
            for word in to_iterable(words)
            for i in range(len(word))
            for j in range(i + 1, len(word) + 1)
        }

    def _get_substring_pairs(
        self, words: str | list[str] | set[str]
    ) -> set[tuple[str, str]]:
        return {
            (word[:i], word[i:])
            for word in to_iterable(words)
            for i in range(1, len(word))
        }

    def _get_substrings_with_contexts(
        self, words: str | list[str] | set[str]
    ) -> set[tuple[str, str, str]]:
        return {
            (word[:i], word[i:j], word[j:])
            for word in to_iterable(words)
            for i in range(len(word))
            for j in range(i + 1, len(word) + 1)
        }

    def weak_learn(self, words: list[str]) -> CFGrammar:
        substrings = self._get_substrings(words)
        nonterminals = {x: Nonterminal(f"[[{x}]]") for x in substrings}
        start_nonterminals = set(map(nonterminals.get, words))

        lexical_productions = [
            Rule(nonterminals[a], [Terminal(a)])
            for a in filter(lambda x: len(x) == 1, substrings)
        ]

        branching_productions = [
            Rule(nonterminals[x[0] + x[1]], list(map(nonterminals.get, x)))
            for x in self._get_substring_pairs(substrings)
        ]

        context_triples = list(self._get_substrings_with_contexts(words))
        substitutables = []
        unary_productions = []

        for i in range(len(context_triples) - 1):
            for j in range(i + 1, len(context_triples)):
                if (
                    context_triples[i][0] == context_triples[j][0]
                    and context_triples[i][-1] == context_triples[j][-1]
                ):
                    substitutables.append(
                        (context_triples[i][1], context_triples[j][1])
                    )

        for sub in substitutables:
            unary_productions.append(Rule(nonterminals[sub[0]], [nonterminals[sub[1]]]))
            unary_productions.append(Rule(nonterminals[sub[1]], [nonterminals[sub[0]]]))

        start_nonterminal = Nonterminal("S")

        rules = (
            [Rule(start_nonterminal, [nt]) for nt in start_nonterminals]
            + lexical_productions
            + branching_productions
            + unary_productions
        )

        return CFGrammar(start_nonterminal, rules)

    def _get_congruent_classes(
        self, words: list[str], grammar: CFGrammar
    ) -> list[CongruentClass]:
        classes = defaultdict(set)
        cky_parser = CKYParser(grammar)

        def add_congruent_class_if_exists(substring):
            for l_cl, r_cl in classes.keys():
                if cky_parser.accepts(l_cl + substring + r_cl):
                    classes[(l_cl, r_cl)].add(substring)
                    return True
            return False

        for word in words:
            for l, v, r in self._get_substrings_with_contexts(word):
                if not add_congruent_class_if_exists(v):
                    classes[(l, r)].add(v)

        return list(map(CongruentClass, classes.values()))

    def _test_class_primality(
        self, hclass: CongruentClass, classes: list[CongruentClass]
    ) -> bool:
        words_classes = {word: cls.words for cls in classes for word in cls.words}

        for u, v in self._get_substring_pairs(hclass.rep):
            if hclass.words.issubset(
                {
                    "".join(words)
                    for words in product(words_classes[u], words_classes[v])
                }
            ):
                return False
        return True

    def _get_prime_decomposition(
        self, cls: CongruentClass, prime_classes: list[CongruentClass]
    ) -> list[CongruentClass]:
        if cls in prime_classes:
            return [cls]

        words_prime_classes = {word: cls for cls in prime_classes for word in cls.words}
        graph = Graph()

        for i in range(len(cls.rep)):
            for j in range(i + 1, len(cls.rep) + 1):
                if cls.rep[i:j] in words_prime_classes:
                    graph.add_edge(i, j, 1)

        shortest_path = graph.shortest_path(0, len(graph.vertices) - 1)

        return [
            words_prime_classes[cls.rep[shortest_path[i] : shortest_path[i + 1]]]
            for i in range(len(shortest_path) - 1)
        ]

    def strong_learn(self, words):
        weak_cfg = self.weak_learn(words)
        classes = self._get_congruent_classes(words, weak_cfg)
        prime_classes = list(
            filter(lambda x: self._test_class_primality(x, classes), classes)
        )
        prime_decompositions = {
            cls.rep: self._get_prime_decomposition(cls, prime_classes)
            for cls in classes
        }

        nonterminals = {cls.rep: Nonterminal(f"[[{cls.rep}]]") for cls in prime_classes}
        start = Nonterminal("S")

        lexical_productions = [
            Rule(nonterminals[a], [Terminal(a)])
            for a in filter(lambda x: len(x) == 1, nonterminals.keys())
        ]

        init_productions = [
            Rule(
                start,
                [nonterminals[cls.rep] for cls in prime_decompositions[word]],
            )
            for word in set(words) & set(prime_decompositions.keys())
        ]

        branching_productions = []
        prime_strings = set(sum([list(cls.words) for cls in prime_classes], []))

        for N, M, Q in product(prime_classes, prime_classes, classes):
            Q_primes = prime_decompositions[Q.rep]
            production = Rule(
                nonterminals[N.rep],
                [nonterminals[M.rep]] + [nonterminals[cls.rep] for cls in Q_primes],
            )

            # print("============")
            # print(N.rep, N.words)
            # print(M.rep, M.words)
            # print(Q.rep, Q.words)
            # print(production)

            if M.rep + "".join([cls.rep for cls in Q_primes]) in N.words and all(
                M.rep + "".join([cls.rep for cls in Q_primes[:i]]) not in prime_strings
                for i in range(1, len(Q_primes))
            ):
                branching_productions.append(production)

        return CFGrammar(
            start, init_productions + lexical_productions + branching_productions
        )
