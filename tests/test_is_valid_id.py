import unittest

import bot

class TestIsValidId(unittest.TestCase):
    def setUp(self):
        # Setup a sample player_ids dictionary
        # In the real game, keys are integers (player IDs) and values are player objects
        self.player_ids = {
            1: "Player 1",
            2: "Player 2",
            5: "Player 5"
        }

    def test_valid_no_responses(self):
        """Test variations of 'no' that should be accepted."""
        valid_nos = ["no", "NO", "No", "nO", " no ", "  NO  "]
        for val in valid_nos:
            with self.subTest(val=val):
                self.assertTrue(bot.is_valid_id(val, self.player_ids))

    def test_valid_player_ids(self):
        """Test numeric inputs that correspond to valid player IDs."""
        valid_ids = ["1", "2", "5", " 1 ", "5 "]
        for val in valid_ids:
            with self.subTest(val=val):
                self.assertTrue(bot.is_valid_id(val, self.player_ids))

    def test_invalid_player_ids(self):
        """Test numeric inputs that do not correspond to valid player IDs."""
        invalid_ids = ["3", "4", "0", "-1", "100"]
        for val in invalid_ids:
            with self.subTest(val=val):
                self.assertFalse(bot.is_valid_id(val, self.player_ids))

    def test_non_numeric_inputs(self):
        """Test non-numeric string inputs."""
        invalid_strings = ["abc", "1.5", "one", " ", "", "n o", "nope"]
        for val in invalid_strings:
            with self.subTest(val=val):
                self.assertFalse(bot.is_valid_id(val, self.player_ids))

if __name__ == '__main__':
    unittest.main()
