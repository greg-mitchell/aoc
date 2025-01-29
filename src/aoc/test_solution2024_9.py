import solution2024_9 as sol
import unittest


class TestLeftmostFreeIndex(unittest.TestCase):
    def setUp(self):
        pass

    def test_oneFileLongEmpty_returnsStartOfEmpty(self):
        disk = sol.parse_input("15")

        lfi = sol.leftmost_free_index(disk)

        self.assertEqual(lfi, 1)


    def test_oneFileLongEmpty_startInEmpty_returnsStartIndex(self):
        disk = sol.parse_input("15")

        lfi = sol.leftmost_free_index(disk, start_i=2)

        self.assertEqual(lfi, 2)


    def test_oneFileShortEmpty_sizeTooBig_returnsNone(self):
        disk = sol.parse_input("12")

        lfi = sol.leftmost_free_index(disk, size=3)

        self.assertIsNone(lfi)


    def test_oneFile_startInEmpty_sizeTooBig_returnsNone(self):
        disk = sol.parse_input("15")

        lfi = sol.leftmost_free_index(disk, start_i=4, size=3)

        self.assertIsNone(lfi)

    def test_twoFiles_firstEmptyTooSmall_returnsStartOfSecond(self):
        disk = sol.parse_input("2234")

        lfi = sol.leftmost_free_index(disk, size=3)

        self.assertEqual(lfi, 7)


if __name__ == "__main__":
    unittest.main()