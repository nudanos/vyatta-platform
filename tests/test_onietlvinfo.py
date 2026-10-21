# Copyright (c) 2026, NuDanOS contributors.
#
# SPDX-License-Identifier: LGPL-2.1-only

import unittest

from vyatta.platform.utils.onietlvinfo import ONIETLVInfo


def tlv(tlv_type, value):
    return [tlv_type, len(value)] + list(value)


def eeprom(*tlvs):
    body = [b for t in tlvs for b in t]
    # "TlvInfo\0", version 1, then the 2-byte total length (header included)
    total = 11 + len(body)
    return list(b'TlvInfo\x00') + [1, total >> 8, total & 0xff] + body


class TestDecode(unittest.TestCase):
    def test_every_field(self):
        data = eeprom(
            tlv(0x21, b'Prod'), tlv(0x22, b'P-1'), tlv(0x23, b'SN9'),
            tlv(0x24, bytes([0, 0x11, 0x22, 0x33, 0x44, 0x55])),
            tlv(0x25, b'01/02/2026 10:00:00'), tlv(0x26, bytes([7])),
            tlv(0x27, b'L2'), tlv(0x28, b'x86_64-plat'), tlv(0x29, b'2020.1'),
            tlv(0x2A, bytes([1, 2])), tlv(0x2B, b'Maker'), tlv(0x2C, b'US'),
            tlv(0x2D, b'Vend'), tlv(0x2E, b'D1'), tlv(0x2F, b'Tag'),
            tlv(0x99, b'unknown type, skipped'),
            tlv(0xFD, bytes([0, 0, 0x30, 0x39]) + b'ext'),
            tlv(0xFE, bytes([0xde, 0xad, 0xbe, 0xef])))
        self.assertEqual(ONIETLVInfo().decode(data), {
            'product_name': 'Prod', 'part_number': 'P-1',
            'serial_number': 'SN9', 'base_mac': '00:11:22:33:44:55',
            'manufacture_date': '01/02/2026 10:00:00', 'device_version': 7,
            'label_revision': 'L2', 'platform_name': 'x86_64-plat',
            'onie_version': '2020.1', 'num_macs': 258,
            'manufacturer': 'Maker', 'country_code': 'US', 'vendor': 'Vend',
            'diag_version': 'D1', 'service_tag': 'Tag',
            'vendor_extension': (12345, 'ext'), 'crc-32': 0xdeadbeef})

    def test_bad_header(self):
        with self.assertRaises(ValueError):
            ONIETLVInfo().decode(list(b'NotTlvInfo') + [0] * 8)

    def test_invalid_tlv_type(self):
        with self.assertRaises(ValueError):
            ONIETLVInfo().decode(eeprom(tlv(0x00, b'x')))


if __name__ == '__main__':
    unittest.main()
