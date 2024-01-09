from src.cfg_learner import CFGLearner
from src.cfg import CFGrammar, Nonterminal, Terminal, Rule
from src.cky_parser import CKYParser

import random
import nltk
from nltk.parse.generate import generate


def generate_random_grammar():
    symbols = list(map(chr, range(ord("a"), ord("z") + 1)))
    alphabet = random.sample(symbols, k=random.randint(3, 8))
    terminals = list(map(Terminal, alphabet))
    nonterminals = [Nonterminal("S")] + list(
        map(
            lambda x: Nonterminal(f"[[{x}]]"),
            random.sample(symbols, k=random.randint(1, 5)),
        )
    )
    rules = []
    samples = nonterminals[1:] + terminals
    for nt in nonterminals:
        for _ in range(random.randint(1, 5)):
            rhs = random.sample(samples, k=min(random.randint(1, 4), len(samples)))
            rules.append(Rule(nt, rhs))
    return CFGrammar(nonterminals[0], rules)


def convert_cfg_to_nltk(cfg):
    start = nltk.grammar.Nonterminal(cfg.start.symbol)
    productions = [
        nltk.grammar.Production(
            lhs=nltk.grammar.Nonterminal(rule.left.symbol),
            rhs=[
                nltk.grammar.Nonterminal(x.symbol)
                if isinstance(x, Nonterminal)
                else x.symbol
                for x in rule.right
            ],
        )
        for rule in cfg.rules
    ]
    return nltk.grammar.CFG(start, productions)


def test_from_positive_examples():
    target_cfg = generate_random_grammar()
    print(target_cfg)
    nltk_cfg = convert_cfg_to_nltk(target_cfg)
    words = list(map(lambda x: "".join(x), generate(nltk_cfg, n=20, depth=10)))
    cfg_learner = CFGLearner()

    for idx in range(1, 6):
        cfg = cfg_learner.strong_learn(words[:idx])
        cky_parser = CKYParser(cfg)
        correct = sum(cky_parser.accepts(word) for word in words)
        print(f"Accuracy of grammar learned by {idx} words: {correct/len(words)}")
