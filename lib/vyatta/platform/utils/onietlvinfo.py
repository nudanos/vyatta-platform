#!/usr/bin/env python3

# Copyright (c) 2020 AT&T Intellectual Property.
# All rights reserved.
""" Decode the ONIE TLV data blob """


# See
# https://opencomputeproject.github.io/onie/design-spec/hw_requirements.html
class ONIETLVInfo:

    TLVINFO_HEADER = 'TlvInfo'
    TLVINFO_INVALID = 0x0
    TLVINFO_TLV_FIELDS = 11
    TLVINFO_TLV_HEADER = 2
    TLVINFO_PRODUCT_NAME = 0x21
    TLVINFO_PART_NUMBER = 0x22
    TLVINFO_SERIAL_NUMBER = 0x23
    TLVINFO_MAC_1_BASE = 0x24
    TLVINFO_MANUFACTURE_DATE = 0x25
    TLVINFO_DEVICE_VERSION = 0x26
    TLVINFO_LABEL_REVISION = 0x27
    TLVINFO_PLATFORM_NAME = 0x28
    TLVINFO_ONIE_VERSION = 0x29
    TLVINFO_NUM_MACS = 0x2A
    TLVINFO_MANUFACTURER = 0x2B
    TLVINFO_COUNTRY_CODE = 0x2C
    TLVINFO_VENDOR = 0x2D
    TLVINFO_DIAG_VERSION = 0x2E
    TLVINFO_SERVICE_TAG = 0x2F
    TLVINFO_VENDOR_EXTENSION = 0xFD
    TLVINFO_CRC_32 = 0xFE

    # TLV types whose value is a string, by their key in the decoded data
    STRING_FIELDS = {
        TLVINFO_PRODUCT_NAME: 'product_name',
        TLVINFO_PART_NUMBER: 'part_number',
        TLVINFO_SERIAL_NUMBER: 'serial_number',
        TLVINFO_MANUFACTURE_DATE: 'manufacture_date',
        TLVINFO_LABEL_REVISION: 'label_revision',
        TLVINFO_PLATFORM_NAME: 'platform_name',
        TLVINFO_ONIE_VERSION: 'onie_version',
        TLVINFO_MANUFACTURER: 'manufacturer',
        TLVINFO_COUNTRY_CODE: 'country_code',
        TLVINFO_VENDOR: 'vendor',
        TLVINFO_DIAG_VERSION: 'diag_version',
        TLVINFO_SERVICE_TAG: 'service_tag',
    }

    def decode_variable(self, data, start, length):
        return ''.join(f'{data[b]:c}' for b in range(start, start + length))

    def decode_int(self, data, start):
        return int(data[start] << 24 | data[start + 1] << 16
                   | data[start + 2] << 8 | data[start + 3])

    def decode_short(self, data, start):
        return int(data[start] << 8 | data[start + 1])

    def decode_other(self, tlv_type, data, start, length):
        """
        The key and value of a TLV whose value is not a string, or None
        for a type this does not decode.
        """
        if tlv_type == self.TLVINFO_MAC_1_BASE:
            return 'base_mac', ':'.join(f'{data[b]:02x}'
                                        for b in range(start, start + length))
        if tlv_type == self.TLVINFO_DEVICE_VERSION:
            return 'device_version', int(data[start])
        if tlv_type == self.TLVINFO_NUM_MACS:
            return 'num_macs', self.decode_short(data, start)
        if tlv_type == self.TLVINFO_VENDOR_EXTENSION:
            return 'vendor_extension', (
                self.decode_int(data, start),
                self.decode_variable(data, start + 4, length - 4))
        if tlv_type == self.TLVINFO_CRC_32:
            return 'crc-32', self.decode_int(data, start)
        return None

    def decode(self, eeprom_data):
        header = self.decode_variable(eeprom_data, 0, 7)
        if header != self.TLVINFO_HEADER:
            raise ValueError('The CPU EEPROM is corrupted or empty.')

        total_len = eeprom_data[9] * 256 + eeprom_data[10]

        decoded_data = {}

        i = self.TLVINFO_TLV_FIELDS
        while i < total_len:
            tlv_type = eeprom_data[i]
            tlv_len = eeprom_data[i + 1]
            tlv_start = i + self.TLVINFO_TLV_HEADER

            if tlv_type == self.TLVINFO_INVALID:
                # This shouldn't happen. If it does, something is very wrong.
                raise ValueError('The CPU EEPROM is corrupted or empty.')

            if tlv_type in self.STRING_FIELDS:
                decoded_data[self.STRING_FIELDS[tlv_type]] = \
                    self.decode_variable(eeprom_data, tlv_start, tlv_len)
            else:
                field = self.decode_other(tlv_type, eeprom_data, tlv_start,
                                          tlv_len)
                if field is not None:
                    decoded_data[field[0]] = field[1]

            i += tlv_len + self.TLVINFO_TLV_HEADER

        return decoded_data
