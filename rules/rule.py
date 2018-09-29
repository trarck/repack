import re


class BaseRule:
    def __init__(self, rule):
        self.rule = rule

    def test(self, value):
        if self.rule:
            return self.rule.test(value)
        return False


class EqualRule(BaseRule):
    def __init__(self, rule):
        BaseRule.__init__(self, rule)

    def test(self, value):
        return self.rule == value


class NotEqualRule(BaseRule):
    def __init__(self, rule):
        BaseRule.__init__(self, rule)

    def test(self, value):
        return self.rule != value


class LessRule(BaseRule):
    def __init__(self, rule):
        BaseRule.__init__(self, rule)

    def test(self, value):
        return value < self.rule


class BigRule(BaseRule):
    def __init__(self, rule):
        BaseRule.__init__(self, rule)

    def test(self, value):
        return value > self.rule


class LessTenRule(BaseRule):
    def __init__(self, rule):
        BaseRule.__init__(self, rule)

    def test(self, value):
        return value <= self.rule


class BigTenRule(BaseRule):
    def __init__(self, rule):
        BaseRule.__init__(self, rule)

    def test(self, value):
        return value >= self.rule


class NotRule(BaseRule):
    def __init__(self, rule):
        BaseRule.__init__(self, rule)

    def test(self, value):
        return not self.rule.test(value)


class AndRule(BaseRule):
    def __init__(self, rule, rule_ext):
        BaseRule.__init__(self, rule)
        self.rule_ext = rule_ext

    def test(self, value):
        return self.rule.test(value) and self.rule_ext.test(value)


class OrRule(BaseRule):
    def __init__(self, rule, rule_ext):
        BaseRule.__init__(self, rule)
        self.rule_ext = rule_ext

    def test(self, value):
        return self.rule.test(value) or self.rule_ext.test(value)


class RegexpMatchRule(BaseRule):
    def __init__(self, rule):
        BaseRule.__init__(self, rule)

    def test(self, value):
        return re.match(self.rule, value) is not None


class RegexpSearchRule(BaseRule):
    def __init__(self, rule):
        BaseRule.__init__(self, rule)

    def test(self, value):
        return re.search(self.rule, value) is not None


class AnyRule(BaseRule):
    def __init__(self, *rules):
        self.rules = rules

    def test(self, value):
        for rule in self.rules:
            if rule.test(value):
                return True
        return False


class AllRule(BaseRule):
    def __init__(self, *rules):
        self.rules = rules

    def test(self, value):
        for rule in self.rules:
            if not rule.test(value):
                return False
        return True


class ContainsRule(BaseRule):
    def __init__(self, rule):
        BaseRule.__init__(self, rule)

    def test(self, value):
        return str(value).find(self.rule) > -1
