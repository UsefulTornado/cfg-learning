from src.cfg_learner import CFGLearner
from src.cfg import CFGrammar, Nonterminal, Terminal, Rule

import nltk
from nltk.parse.generate import generate


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
    target_cfg = CFGrammar(
        start=Nonterminal("S"),
        rules=[
            Rule(Nonterminal("S"), [Nonterminal("[[c]]")]),
            Rule(Nonterminal("[[a]]"), [Terminal("a")]),
            Rule(Nonterminal("[[b]]"), [Terminal("b")]),
            Rule(Nonterminal("[[c]]"), [Terminal("c")]),
            Rule(
                Nonterminal("[[c]]"),
                [Nonterminal("[[a]]"), Nonterminal("[[c]]"), Nonterminal("[[b]]")],
            ),
        ],
    )
    nltk_cfg = convert_cfg_to_nltk(target_cfg)
    words = list(map(lambda x: "".join(x), generate(nltk_cfg, n=10)))
    cfg_learner = CFGLearner()

    for idx in range(1, len(words) + 1):
        cfg = cfg_learner.strong_learn(words[:idx])
        if cfg == target_cfg:
            print(f"Grammar correctly learned for {idx} steps")
            break
