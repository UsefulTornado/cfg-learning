from src.cfg_learner import CFGLearner
from src.cky_parser import CKYParser
from src.cfg_parser import CFGParser
from src.utils import get_words_from_grammar

from pathlib import Path


def test_from_generated_grammars():
    max_words = 20
    grammars_folder = "tests/generated_grammars"
    grammar_paths = list(Path(grammars_folder).glob(r"*.txt"))
    total = len(grammar_paths)
    total_learned = 0
    not_learned = []

    for path in grammar_paths:
        target_cfg = CFGParser().parse_grammar(path)
        words = get_words_from_grammar(target_cfg)[:1000]
        cfg_learner = CFGLearner()

        print("\n" + "=" * 50 + "\n")
        print(str(path), end="\n\n")
        print(words[: max_words + 1])

        for idx in range(1, max_words + 1):
            cfg = cfg_learner.strong_learn(words[:idx])
            cky_parser = CKYParser(cfg)
            correct = sum(cky_parser.accepts(word) for word in words)
            print(f"Accuracy of grammar learned by {idx} words: {correct/len(words)}")
            if correct == len(words):
                total_learned += 1
                break
            elif idx == max_words:
                not_learned.append(path)

    print(f"\nTotal learned grammars: {total_learned} out of {total}")
    print(f"Grammars that are not learned: {not_learned}")
