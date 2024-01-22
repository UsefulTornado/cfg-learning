import nltk
from nltk.parse.generate import generate
from src.cfg import Nonterminal


def to_iterable(obj: object) -> list | set:
    return obj if isinstance(obj, (list, set)) else [obj]


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


def get_words_from_grammar(cfg, max_depth=8):
    nltk_cfg = convert_cfg_to_nltk(cfg)
    words = set()
    for depth in range(2, max_depth + 1):
        words.update(
            set(map(lambda x: "".join(x), generate(nltk_cfg, n=10**5, depth=depth)))
        )
    return sorted(words, key=len)
