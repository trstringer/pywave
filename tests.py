#!/usr/bin/env python3

import unittest
import pywave

class SwellTests(unittest.TestCase):
    def test_data_retrieve(self):
        swell_data = pywave.SwellData.retrieve_station_data(46053)
        self.assertIsNotNone(swell_data.swell_direction)
        self.assertIsNotNone(swell_data.swell_height)
        self.assertIsNotNone(swell_data.swell_period)

if __name__ == '__main__':
    unittest.main()

