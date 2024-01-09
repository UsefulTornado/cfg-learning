from src.cfg_learner import CFGLearner
from src.cfg import Nonterminal, Terminal, Rule, CongruentClass


def test__get_substrings():
    cfg_learner = CFGLearner()
    assert cfg_learner._get_substrings(["abc", "bcf"]) == {
        "a",
        "b",
        "c",
        "ab",
        "bc",
        "abc",
        "f",
        "cf",
        "bcf",
    }
    assert cfg_learner._get_substrings("ab") == {"a", "b", "ab"}
    assert cfg_learner._get_substrings(["ab"]) == {"a", "b", "ab"}
    assert cfg_learner._get_substrings("") == set()
    assert cfg_learner._get_substrings([]) == set()


def test__get_substring_pairs():
    cfg_learner = CFGLearner()
    assert cfg_learner._get_substring_pairs(["abc", "abcde"]) == {
        ("a", "bc"),
        ("ab", "c"),
        ("a", "bcde"),
        ("ab", "cde"),
        ("abc", "de"),
        ("abcd", "e"),
    }
    assert cfg_learner._get_substring_pairs("ab") == {("a", "b")}
    assert cfg_learner._get_substring_pairs("") == set()


def test__get_substrings_with_contexts():
    cfg_learner = CFGLearner()
    assert cfg_learner._get_substrings_with_contexts("abc") == {
        ("", "a", "bc"),
        ("", "ab", "c"),
        ("", "abc", ""),
        ("a", "b", "c"),
        ("a", "bc", ""),
        ("ab", "c", ""),
    }
    assert cfg_learner._get_substrings_with_contexts({"abc", "ac"}) == {
        ("", "a", "bc"),
        ("", "ab", "c"),
        ("", "abc", ""),
        ("a", "b", "c"),
        ("a", "bc", ""),
        ("ab", "c", ""),
        ("a", "c", ""),
        ("", "a", "c"),
        ("", "ac", ""),
    }
    assert cfg_learner._get_substrings_with_contexts("a") == {("", "a", "")}
    assert cfg_learner._get_substrings_with_contexts("") == set()


def test_weak_learn():
    cfg_learner = CFGLearner()
    cfg = cfg_learner.weak_learn(["c", "acb"])
    assert cfg.nonterminals == {
        Nonterminal("S"),
        Nonterminal("[[a]]"),
        Nonterminal("[[b]]"),
        Nonterminal("[[c]]"),
        Nonterminal("[[ac]]"),
        Nonterminal("[[cb]]"),
        Nonterminal("[[acb]]"),
    }
    assert set(cfg.rules) == {
        # initial
        Rule(Nonterminal("S"), [Nonterminal("[[acb]]")]),
        Rule(Nonterminal("S"), [Nonterminal("[[c]]")]),
        # lexical
        Rule(Nonterminal("[[a]]"), [Terminal("a")]),
        Rule(Nonterminal("[[b]]"), [Terminal("b")]),
        Rule(Nonterminal("[[c]]"), [Terminal("c")]),
        # branching
        Rule(Nonterminal("[[ac]]"), [Nonterminal("[[a]]"), Nonterminal("[[c]]")]),
        Rule(Nonterminal("[[cb]]"), [Nonterminal("[[c]]"), Nonterminal("[[b]]")]),
        Rule(Nonterminal("[[acb]]"), [Nonterminal("[[ac]]"), Nonterminal("[[b]]")]),
        Rule(Nonterminal("[[acb]]"), [Nonterminal("[[a]]"), Nonterminal("[[cb]]")]),
        # unary
        Rule(Nonterminal("[[c]]"), [Nonterminal("[[acb]]")]),
        Rule(Nonterminal("[[acb]]"), [Nonterminal("[[c]]")]),
    }


def test__get_congruent_classes():
    cfg_learner = CFGLearner()

    words = ["ab"]
    cfg = cfg_learner.weak_learn(words)
    assert set(cfg_learner._get_congruent_classes(words, cfg)) == {
        CongruentClass(["a"]),
        CongruentClass(["b"]),
        CongruentClass(["ab"]),
    }

    words = ["c", "acb", "aacbb"]
    cfg = cfg_learner.weak_learn(words)
    assert set(cfg_learner._get_congruent_classes(words, cfg)) == {
        CongruentClass(["a"]),
        CongruentClass(["b"]),
        CongruentClass(["c", "acb", "aacbb"]),
        CongruentClass(["ac", "aacb"]),
        CongruentClass(["cb", "acbb"]),
        CongruentClass(["aa"]),
        CongruentClass(["aac"]),
        CongruentClass(["cbb"]),
        CongruentClass(["bb"]),
    }


def test__test_class_primality():
    cfg_learner = CFGLearner()
    words = ["c", "acb"]
    cfg = cfg_learner.weak_learn(words)
    classes = cfg_learner._get_congruent_classes(words, cfg)
    prime_classes = list(
        filter(lambda x: cfg_learner._test_class_primality(x, classes), classes)
    )
    assert set(prime_classes) == {
        CongruentClass(["a"]),
        CongruentClass(["b"]),
        CongruentClass(["c", "acb"]),
    }


def test__get_prime_decomposition():
    cfg_learner = CFGLearner()

    prime_classes = [
        CongruentClass(["a"]),
        CongruentClass(["b"]),
        CongruentClass(["c", "acb"]),
    ]

    assert cfg_learner._get_prime_decomposition(
        CongruentClass(["a"]), prime_classes
    ) == [CongruentClass(["a"])]

    assert cfg_learner._get_prime_decomposition(
        CongruentClass(["ac"]), prime_classes
    ) == [CongruentClass(["a"]), CongruentClass(["c", "acb"])]

    assert cfg_learner._get_prime_decomposition(
        CongruentClass(["aacbb"]), prime_classes
    ) == [CongruentClass(["a"]), CongruentClass(["c", "acb"]), CongruentClass(["b"])]


def test_strong_learn1():
    cfg_learner = CFGLearner()
    cfg = cfg_learner.strong_learn(["c", "acb"])
    assert cfg.nonterminals == {
        Nonterminal("S"),
        Nonterminal("[[a]]"),
        Nonterminal("[[b]]"),
        Nonterminal("[[c]]"),
    }
    assert set(cfg.rules) == {
        Rule(Nonterminal("S"), [Nonterminal("[[c]]")]),
        Rule(Nonterminal("[[a]]"), [Terminal("a")]),
        Rule(Nonterminal("[[b]]"), [Terminal("b")]),
        Rule(Nonterminal("[[c]]"), [Terminal("c")]),
        Rule(
            Nonterminal("[[c]]"),
            [Nonterminal("[[a]]"), Nonterminal("[[c]]"), Nonterminal("[[b]]")],
        ),
    }

def test_strong_learn2():
    cfg_learner = CFGLearner()
    cfg = cfg_learner.strong_learn(["ab", "ba", "abab", "abba", "baba", "bbaa"])
    for nt in cfg.nonterminals:
        print(nt)
    assert cfg.nonterminals == {
        Nonterminal("S"),
        Nonterminal("[[b]]"),
        Nonterminal("[[ab]]"),
        Nonterminal("[[a]]"),
    }
    for rule in cfg.rules:
        print(rule)
    assert set(cfg.rules) == {
        Rule(Nonterminal("S"), [Nonterminal("[[ab]]")]),
        Rule(Nonterminal("[[a]]"), [Terminal("a")]),
        Rule(Nonterminal("[[b]]"), [Terminal("b")]),
        Rule(Nonterminal("[[a]]"), [Nonterminal("[[a]]"), Nonterminal("[[ab]]")]),
        Rule(Nonterminal("[[a]]"), [Nonterminal("[[ab]]"), Nonterminal("[[a]]")]),
        Rule(Nonterminal("[[b]]"), [Nonterminal("[[ab]]"), Nonterminal("[[b]]")]),
        Rule(Nonterminal("[[b]]"), [Nonterminal("[[b]]"), Nonterminal("[[ab]]")]),
        Rule(Nonterminal("[[ab]]"), [Nonterminal("[[a]]"), Nonterminal("[[b]]")]),
        Rule(Nonterminal("[[ab]]"), [Nonterminal("[[b]]"), Nonterminal("[[a]]")]),
        Rule(Nonterminal("[[ab]]"), [Nonterminal("[[ab]]"), Nonterminal("[[ab]]")]),
    }