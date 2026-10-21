# Copyright (c) 2026, NuDanOS contributors.
#
# SPDX-License-Identifier: LGPL-2.1-only

import socket
import unittest
from unittest import mock

from vyatta.phy.basephy import PhyAccessException
from vyatta.phy.marvell88e1111 import Marvell88E1111Phy


class FakeBus:
    """An SMBus whose PHY control register keeps the given value"""

    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.writes = []

    def read_word_data(self, addr, reg):
        del addr, reg
        return socket.htons(self.ctrl)

    def write_word_data(self, addr, reg, value):
        self.writes.append((addr, reg, socket.ntohs(value)))


class TestSoftReset(unittest.TestCase):
    def test_reset_that_never_completes_times_out(self):
        phy = Marvell88E1111Phy()
        bus = FakeBus(Marvell88E1111Phy.CTRL_RESET)
        with mock.patch('vyatta.phy.marvell88e1111.sleep') as fake_sleep:
            with self.assertRaises(PhyAccessException):
                # pylint: disable-next=W0212 ; reason: under test
                phy._phy_soft_reset(bus)
        self.assertEqual(fake_sleep.call_count, 8)

    def test_completed_reset_returns(self):
        phy = Marvell88E1111Phy()
        # pylint: disable-next=W0212 ; reason: under test
        phy._phy_soft_reset(FakeBus(0))


if __name__ == '__main__':
    unittest.main()
