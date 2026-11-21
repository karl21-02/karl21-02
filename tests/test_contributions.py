"""Real calendar parsing and streak boundary cases, independent of network access."""
import datetime as dt
import unittest

from scripts.fetch_contributions import build_data, parse_contributions


TODAY = dt.date(2026, 11, 21)


class ContributionTests(unittest.TestCase):
    def test_counts_come_from_tooltips_and_dates_are_sorted_without_future_days(self):
        html = '''<table><tr>
        <td class="ContributionCalendar-day" id="b" data-date="2026-11-21" data-level="4"></td>
        <td class="ContributionCalendar-day" id="a" data-date="2026-11-20" data-level="0"></td>
        <td class="ContributionCalendar-day" id="c" data-date="2026-11-22" data-level="4"></td>
        </tr></table>
        <tool-tip for="a">No contributions on November 20th.</tool-tip>
        <tool-tip for="b">1,234 contributions on November 21st.</tool-tip>
        <tool-tip for="c">12 contributions on November 22nd.</tool-tip>'''
        self.assertEqual(parse_contributions(html, TODAY), [
            {"date": "2026-11-20", "count": 0, "level": 0},
            {"date": "2026-11-21", "count": 1234, "level": 4},
        ])

    def test_missing_or_unreadable_calendar_fails_instead_of_publishing_zeroes(self):
        for html in ["<html>Sign in</html>", '''
            <td class="ContributionCalendar-day" data-date="2026-11-21" data-level="3"></td>''']:
            with self.subTest(html=html), self.assertRaises(ValueError):
                parse_contributions(html, TODAY)

    def test_today_can_be_unfinished_without_breaking_yesterdays_streak(self):
        days = [
            {"date": "2026-11-18", "count": 0, "level": 0},
            {"date": "2026-11-19", "count": 2, "level": 1},
            {"date": "2026-11-20", "count": 3, "level": 2},
            {"date": "2026-11-21", "count": 0, "level": 0},
        ]
        result = build_data(days, TODAY)
        self.assertEqual(result.get("current_streak"), 2)
        self.assertEqual(result.get("longest_streak"), 2)
        self.assertEqual(result.get("total_contributions"), 5)
        self.assertEqual(result.get("monthly"), {"2026-11": 5})

    def test_a_gap_before_yesterday_ends_the_current_streak(self):
        days = [
            {"date": "2026-11-18", "count": 5, "level": 1},
            {"date": "2026-11-20", "count": 3, "level": 1},
            {"date": "2026-11-21", "count": 4, "level": 1},
        ]
        result = build_data(days, TODAY)
        self.assertEqual(result.get("current_streak"), 2)
        self.assertEqual(result.get("longest_streak"), 2)

    def test_old_data_cannot_claim_an_active_current_streak(self):
        result = build_data([{"date": "2026-11-18", "count": 5, "level": 1}], TODAY)
        self.assertEqual(result.get("current_streak"), 0)
        self.assertEqual(result.get("longest_streak"), 1)

    def test_empty_data_is_rejected(self):
        with self.assertRaises(ValueError):
            build_data([], TODAY)


if __name__ == "__main__":
    unittest.main()
