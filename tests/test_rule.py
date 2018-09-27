import re
from rules import *

eq = EqualRule(1)
print(eq.test(1))
print(eq.test(2))
print(eq.test("2"))

bg = BigRule("2")
print(bg.test("1"))
print(bg.test(2))
print(bg.test("3"))

n = NotRule(eq)
print(n.test(1))
print(n.test(2))
print(n.test("2"))

bg = BigRule(1)
less = LessRule(5)
and_rule = AndRule(less, bg)
print(and_rule.test(3))
print(and_rule.test(6))

bg = BigRule(5)
less = LessRule(1)
or_rule = OrRule(less, bg)
print(or_rule.test(3))
print(or_rule.test(0))

print "--------"
reg_math_text = RegexpMatchRule(r'.*\.txt')
print(reg_math_text.test("aa.txt"))
print(reg_math_text.test("aa.jpg"))

reg_math_jpg = RegexpMatchRule(r'.*\.jpg')
reg_math_png = RegexpMatchRule(r'.*\.png')

print "--------"
pic_rule = OrRule(reg_math_jpg, reg_math_png)
print(pic_rule.test("aa.txt"))
print(pic_rule.test("aa.jpg"))

print "--------"
all_rule = OrRule(reg_math_text, OrRule(reg_math_jpg, reg_math_png))
print(all_rule.test("aa.txt"))
print(all_rule.test("aa.jpg"))

print "--------"
any_rule = AnyRule(reg_math_text, reg_math_jpg, reg_math_png)
print(any_rule.test("aa.txt"))
print(any_rule.test("aa.jpg"))
