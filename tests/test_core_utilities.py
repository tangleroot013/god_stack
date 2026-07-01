#!/usr/bin/env python3
import unittest
from url_sanitizer import UrlSanitizer

class TestUrlSanitizer(unittest.TestCase):
    def test_case_insensitive_schemes(self):
        input_url = "HTTPS://NEWS.YCOMBINATOR.COM/item?id=1"
        expected = "https://news.ycombinator.com/item?id=1"
        self.assertEqual(UrlSanitizer.normalize(input_url), expected)

    def test_fragment_stripping(self):
        input_url = "https://news.ycombinator.com/front#comments-section"
        expected = "https://news.ycombinator.com/front"
        self.assertEqual(UrlSanitizer.normalize(input_url), expected)

    def test_missing_scheme_prepend(self):
        input_url = "news.ycombinator.com/news"
        expected = "https://news.ycombinator.com/news"
        self.assertEqual(UrlSanitizer.normalize(input_url), expected)

    def test_tracking_parameter_removal(self):
        input_url = "https://news.ycombinator.com/item?id=45&utm_source=twitter&fbclid=xyz123"
        expected = "https://news.ycombinator.com/item?id=45"
        self.assertEqual(UrlSanitizer.normalize(input_url), expected)
