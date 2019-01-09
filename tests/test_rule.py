import re
import utils
import unittest
from rules import *


class CppParseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("in setup class")

    @classmethod
    def tearDownClass(cls):
        print("in tear down class")

    def setUp(self):
        print("in setup")

    def tearDown(self):
        print("in tear down")

    def test_equal(self):
        eq = EqualRule(1)
        self.assertTrue(eq.test(1))
        self.assertFalse(eq.test(2))
        self.assertFalse(eq.test("2"))

    def test_big(self):
        bg = BigRule("2")
        self.assertTrue(bg.test("1"))
        self.assertFalse(bg.test(2))
        self.assertFalse(bg.test("3"))

    def test_big(self):
        eq = EqualRule(1)
        n = NotRule(eq)
        self.assertFalse(n.test(1))
        self.assertTrue(n.test(2))
        self.assertTrue(n.test("2"))

    def test_big_less_and(self):
        bg = BigRule(1)
        less = LessRule(5)
        and_rule = AndRule(less, bg)
        self.assertTrue(and_rule.test(3))
        self.assertFalse(and_rule.test(6))

    def test_big_less_or(self):
        bg = BigRule(5)
        less = LessRule(1)
        or_rule = OrRule(less, bg)
        self.assertFalse(or_rule.test(3))
        self.assertTrue(or_rule.test(0))

    def test_match_txt(self):
        reg_math_text = RegexpMatchRule(r'.*\.txt')
        self.assertTrue(reg_math_text.test("aa.txt"))
        self.assertFalse(reg_math_text.test("aa.jpg"))

    def test_match_pic(self):
        reg_math_jpg = RegexpMatchRule(r'.*\.jpg')
        reg_math_png = RegexpMatchRule(r'.*\.png')
        pic_rule = OrRule(reg_math_jpg, reg_math_png)
        self.assertFalse(pic_rule.test("aa.txt"))
        self.assertTrue(pic_rule.test("aa.jpg"))

    def test_any(self):
        reg_math_text = RegexpMatchRule(r'.*\.txt')
        reg_math_jpg = RegexpMatchRule(r'.*\.jpg')
        reg_math_png = RegexpMatchRule(r'.*\.png')
        any_rule = AnyRule(reg_math_text, reg_math_jpg, reg_math_png)
        self.assertTrue(any_rule.test("aa.txt"))
        self.assertTrue(any_rule.test("aa.jpg"))

    def test_all(self):
        all_rule = AllRule([BigRule(2), BigRule(5), LessRule(10)])
        self.assertFalse(all_rule.test(4))
        self.assertTrue(all_rule.test(7))
