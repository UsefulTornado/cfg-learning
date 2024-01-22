from .cfg_learner import CFGLearner
from .cfg import CFGrammar, Nonterminal, Terminal, Rule
from .cky_parser import CKYParser
from .utils import to_iterable, get_words_from_grammar

from collections import defaultdict
import time
import random


def generate_random_grammar():
    symbols = list(map(chr, range(ord("a"), ord("z") + 1)))
    alphabet = random.sample(symbols, k=random.randint(2, 4))
    terminals = list(map(Terminal, alphabet))
    nonterminals = [Nonterminal("S")] + list(
        map(
            lambda x: Nonterminal(f"[[{x}]]"),
            random.sample(symbols, k=random.randint(1, 5)),
        )
    )

    rules = []
    samples = list(set(nonterminals[1:] + terminals))

    for nt in nonterminals:
        for _ in range(random.randint(1, 3)):
            rhs = random.sample(samples, k=min(random.randint(1, 3), len(samples)))
            rules.append(Rule(nt, rhs))

    for nt in nonterminals[1:]:
        rules.append(Rule(nt, random.sample(terminals, k=1)))

    return CFGrammar(nonterminals[0], rules)


def _get_substrings_with_contexts(
    words: str | list[str] | set[str],
) -> list[tuple[str, str, str]]:
    return [
        (word[:i], word[i:j], word[j:])
        for word in to_iterable(words)
        for i in range(len(word))
        for j in range(i + 1, len(word) + 1)
    ]


def check_approx_substitutability(grammar, restrict_time=True):
    start = time.time()

    words = get_words_from_grammar(grammar)[:7]
    contexts = defaultdict(set)

    for word in words:
        for l, v, r in _get_substrings_with_contexts(word):
            contexts[v].add((l, r))

    cky_parser = CKYParser(grammar)
    ctxs = {ctx for context_values in contexts.values() for ctx in context_values}

    for ctx in ctxs:
        for v in contexts.keys():
            if cky_parser.accepts(ctx[0] + v + ctx[1]):
                if restrict_time and time.time() - start > 10:
                    return False
                contexts[v].add(ctx)

    for ctx1 in contexts.values():
        for ctx2 in contexts.values():
            if ctx1 != ctx2 and ctx1 & ctx2 != set():
                return False

    return True


def generate_approx_substitutable_grammar():
    random_cfg = generate_random_grammar()
    words = get_words_from_grammar(random_cfg)
    learner = CFGLearner()

    for i in range(7, 1, -1):
        cfg = learner.strong_learn(words[:i], restrict_time=True)
        if (
            cfg
            and check_approx_substitutability(cfg)
            and len(get_words_from_grammar(cfg)) > 10
        ):
            return cfg

    return generate_approx_substitutable_grammar()
