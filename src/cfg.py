from queue import Queue
from collections import defaultdict
from copy import deepcopy


class Nonterminal:
    def __init__(self, symbol, mark=None):
        self.symbol = symbol
        self.mark = mark

    def __eq__(self, other):
        return (
            isinstance(other, Nonterminal)
            and self.symbol == other.symbol
            and self.mark == other.mark
        )

    def __hash__(self):
        return hash(self.symbol)

    def __str__(self):
        if self.mark:
            return f"{self.symbol}_{self.mark.symbol}"
        return self.symbol


class Terminal:
    def __init__(self, symbol):
        self.symbol = symbol

    def __eq__(self, other):
        return isinstance(other, Terminal) and self.symbol == other.symbol

    def __hash__(self):
        return hash(self.symbol)

    def __str__(self):
        return self.symbol


class Rule:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __eq__(self, other):
        return (
            isinstance(other, Rule)
            and self.left == other.left
            and self.right == other.right
        )

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return f'{self.left} -> {" ".join(map(str, self.right))}'


class CongruentClass:
    def __init__(self, words):
        self.words = words
        self.rep = str(sorted(words, key=lambda x: (len(x), x))[0])

    def __eq__(self, other):
        return (
            isinstance(other, CongruentClass)
            and self.rep == other.rep
            and set(self.words) == set(other.words)
        )

    def __hash__(self):
        return hash(self.rep)

    def __str__(self):
        return f'Representative: {self.rep}\nWords: {" ".join(self.words)}'


class CFGrammar:
    def __init__(self, start=Nonterminal("S"), rules=None):
        self.start = start
        self.rules = rules or []
        self.nonterminals = self._get_nonterminals()
        self.rules_by_nonterminals = self._get_rules_by_nonterminals()

    def __eq__(self, other):
        return (
            isinstance(other, CFGrammar)
            and self.start == other.start
            and set(self.rules) == set(other.rules)
        )

    def __str__(self):
        return (
            "Starting: "
            + str(self.start)
            + "\n"
            + "Nonterminals: "
            + " ".join(map(str, self.nonterminals))
            + "\n\n"
            + "Rules:\n\n"
            + "\n".join(map(str, self.rules))
        )

    def save(self, path):
        with open(path, mode="w", encoding="utf-8") as file:
            file.write("\n".join(map(str, self.rules)))

    def _get_nonterminals(self):
        nonterminals = set()
        for rule in self.rules:
            nonterminals.add(rule.left)
            nonterminals.update(
                {sym for sym in rule.right if isinstance(sym, Nonterminal)}
            )
        return nonterminals

    def _get_rules_by_nonterminals(self):
        rules_by_nts = defaultdict(list)
        for rule in self.rules:
            rules_by_nts[rule.left].append(rule)
        return rules_by_nts

    def new_nonterminal(self, sym, used_nonterminals, mark=None):
        suffix = 0
        sym = sym.upper()
        while Nonterminal(sym + str(suffix)) in self.nonterminals | used_nonterminals:
            suffix += 1
        return Nonterminal(sym + str(suffix), mark)

    def first(self, k, symbols):
        def cartesian_product(set1, set2, max_num):
            if not set1:
                return set2
            if not set2:
                return set1
            return {(a + b)[:max_num] for a in set1 for b in set2}

        def first_rec(k, symbols, visited):
            if k == 0:
                return set()

            if not symbols:
                return {tuple()}

            if isinstance(symbols[0], Terminal):
                return cartesian_product(
                    {(symbols[0],)}, first_rec(k - 1, symbols[1:], visited), max_num=k
                )

            curr_visited = deepcopy(visited)
            first = set()

            for rule in self.rules_by_nonterminals[symbols[0]]:
                if (
                    rule.right
                    and rule.right[0] == symbols[0]
                    and symbols[0] in curr_visited
                ):
                    first |= cartesian_product(
                        first_rec(k - 1, rule.right, curr_visited),
                        first_rec(k - 1, symbols[1:], curr_visited),
                        max_num=k,
                    )
                else:
                    curr_visited.add(symbols[0])
                    first |= first_rec(k, rule.right + symbols[1:], curr_visited)

            return first

        return first_rec(k, symbols, set())

    def follow(self, k, nonterminal):
        def follow_rec(k, nonterminal):
            if nonterminal == new_start:
                return {(Terminal("$"),)}

            if nonterminal in visited:
                return set()
            visited.add(nonterminal)

            follow = set()

            for rule in self.rules:
                if nonterminal in rule.right:
                    idx = rule.right.index(nonterminal)
                    previous = rule.right[idx + 1 :]
                    following = follow_rec(k, rule.left)
                    if following:
                        for flw in following:
                            follow |= self.first(k, previous + list(flw))
                    elif previous:
                        follow |= self.first(k, previous)

            return follow

        new_start = self.new_nonterminal(self.start.symbol, set())
        self.rules.append(Rule(new_start, [self.start]))
        visited = set()
        res = follow_rec(k, nonterminal)
        self.rules.pop()

        return res

    @staticmethod
    def remove_long_rules(cfg):
        used_nonterminals = set()
        new_rules = []

        def reduce_rule(left, right):
            if len(right) > 2:
                new_left = cfg.new_nonterminal(left.symbol, used_nonterminals)
                used_nonterminals.add(new_left)
                new_rules.append(Rule(left, [right[0], new_left]))
                reduce_rule(new_left, right[1:])
            else:
                new_rules.append(Rule(left, right))

        for rule in cfg.rules:
            reduce_rule(rule.left, rule.right)

        return CFGrammar(cfg.start, new_rules)

    @staticmethod
    def get_nullable_nonterminals(cfg):
        concerned_rules = {nt: [] for nt in cfg.nonterminals}
        counter = [0] * len(cfg.rules)
        nullable = set()
        nullable_to_process = Queue()

        for idx, rule in enumerate(cfg.rules):
            for sym in rule.right:
                contains_terminal = False
                if isinstance(sym, Nonterminal):
                    concerned_rules[sym].append(idx)
                    counter[idx] += 1
                else:
                    contains_terminal = True
                if contains_terminal:
                    counter[idx] = -1
            if not rule.right:
                nullable_to_process.put(rule.left)

        while not nullable_to_process.empty():
            left = nullable_to_process.get()
            nullable.add(left)
            for idx in concerned_rules[left]:
                counter[idx] -= 1
                if counter[idx] == 0:
                    nullable_to_process.put(cfg.rules[idx].left)

        return nullable

    @staticmethod
    def remove_nullable_rules(cfg):
        new_rules = []
        nullable = CFGrammar.get_nullable_nonterminals(cfg)

        def update_with_combinations(left, right):
            candidates = Queue()
            candidates.put(right)
            while not candidates.empty():
                rule = Rule(left, candidates.get())
                if rule not in new_rules and rule.right:
                    new_rules.append(rule)
                    for idx, sym in enumerate(rule.right):
                        if sym in nullable:
                            candidates.put(rule.right[:idx] + rule.right[idx + 1 :])

        for rule in cfg.rules:
            update_with_combinations(rule.left, rule.right)

        if cfg.start in nullable:
            new_start = cfg.new_nonterminal(cfg.start.symbol, set())
            new_rules.append(Rule(new_start, [cfg.start]))
            new_rules.append(Rule(new_start, []))
            return CFGrammar(new_start, new_rules)

        return CFGrammar(cfg.start, new_rules)

    @staticmethod
    def update_start(cfg):
        new_rules = []
        need_new_start = False
        for rule in cfg.rules:
            if cfg.start in rule.right:
                need_new_start = True
            new_rules.append(rule)

        if need_new_start:
            start = cfg.new_nonterminal(cfg.start.symbol, set())
            new_rules.append(Rule(start, [cfg.start]))
            return CFGrammar(start, new_rules)

        return cfg

    @staticmethod
    def remove_unit_rules(cfg):
        concerned_rules = {nt: set() for nt in cfg.nonterminals}
        new_rules = []
        unit_rules = Queue()
        concerned_unit_rules = set()

        for idx, rule in enumerate(cfg.rules):
            if len(rule.right) == 1 and isinstance(rule.right[0], Nonterminal):
                if rule.left != rule.right[0]:
                    unit_rules.put(rule)
                    concerned_unit_rules.add(rule)
                    concerned_rules[rule.left].add(idx)
            else:
                new_rules.append(Rule(rule.left, rule.right))
                concerned_rules[rule.left].add(idx)

        while not unit_rules.empty():
            unit_rule = unit_rules.get()

            for idx in concerned_rules[unit_rule.right[0]]:
                new_rule = Rule(unit_rule.left, cfg.rules[idx].right)

                if new_rule in concerned_unit_rules:
                    continue
                if len(new_rule.right) == 1 and isinstance(
                    new_rule.right[0], Nonterminal
                ):
                    if new_rule.left != new_rule.right[0]:
                        unit_rules.put(new_rule)
                        concerned_unit_rules.add(new_rule)
                else:
                    if new_rule not in new_rules:
                        new_rules.append(new_rule)

        return CFGrammar(cfg.start, new_rules)

    @staticmethod
    def get_generating_nonterminals(cfg):
        concerned_rules = {nt: [] for nt in cfg.nonterminals}
        counter = [0] * len(cfg.rules)
        generating_to_process = Queue()
        generating = set()

        for idx, rule in enumerate(cfg.rules):
            for sym in rule.right:
                if isinstance(sym, Nonterminal):
                    concerned_rules[sym].append(idx)
                    counter[idx] += 1
            if counter[idx] == 0:
                generating_to_process.put(rule.left)

        while not generating_to_process.empty():
            left = generating_to_process.get()
            generating.add(left)
            for idx in concerned_rules[left]:
                counter[idx] -= 1
                if counter[idx] == 0:
                    generating_to_process.put(cfg.rules[idx].left)

        return generating

    @staticmethod
    def get_reachable_nonterminals(cfg):
        reachable = {cfg.start}
        visited = {nt: False for nt in cfg.nonterminals}

        def visit(nonterminal):
            visited[nonterminal] = True
            for rule in cfg.rules:
                if rule.left == nonterminal:
                    for sym in rule.right:
                        if sym in cfg.nonterminals:
                            reachable.add(sym)
                            if not visited[sym]:
                                visit(sym)

        visit(cfg.start)

        return reachable

    @staticmethod
    def remove_useless_rules(cfg):
        useful_nonterminals = CFGrammar.get_generating_nonterminals(
            cfg
        ) & CFGrammar.get_reachable_nonterminals(cfg)
        new_rules = []

        for rule in cfg.rules:
            if rule.left in useful_nonterminals:
                new_rules.append(Rule(rule.left, rule.right))

        return CFGrammar(cfg.start, new_rules)

    @staticmethod
    def remove_terminal_rules(cfg):
        new_rules = []
        used_nonterminals = set()

        for rule in cfg.rules:
            if len(rule.right) == 2:
                right1, right2 = rule.right[0], rule.right[1]
                if right1 not in cfg.nonterminals:
                    new_right1 = cfg.new_nonterminal(right1.symbol, used_nonterminals)
                    used_nonterminals.add(new_right1)
                    new_rules.append(Rule(new_right1, [right1]))
                    right1 = new_right1
                if right2 not in cfg.nonterminals:
                    new_right2 = cfg.new_nonterminal(right2.symbol, used_nonterminals)
                    used_nonterminals.add(new_right2)
                    new_rules.append(Rule(new_right2, [right2]))
                    right2 = new_right2
                new_rules.append(Rule(rule.left, [right1, right2]))
            else:
                new_rules.append(Rule(rule.left, rule.right))

        return CFGrammar(cfg.start, new_rules)

    @staticmethod
    def to_chomsky_normal_form(cfg):
        new_cfg = CFGrammar.remove_long_rules(cfg)
        new_cfg = CFGrammar.remove_nullable_rules(new_cfg)
        new_cfg = CFGrammar.update_start(new_cfg)
        new_cfg = CFGrammar.remove_unit_rules(new_cfg)
        new_cfg = CFGrammar.remove_useless_rules(new_cfg)
        new_cfg = CFGrammar.remove_terminal_rules(new_cfg)

        return new_cfg
