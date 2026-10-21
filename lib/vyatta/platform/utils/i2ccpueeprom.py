#!/usr/bin/env python3

# Copyright (c) 2020 AT&T Intellectual Property.
# All rights reserved.
""" Access I2C CPU EEPROM """

from common.logger import Logger
from smbus import SMBus


# pylint: disable-next=R0903 ; reason: callers use it
class I2cCPUEEPROM:

    CPU_EEPROM_SIZE = 256
    CPU_EEPROM_PAGE_SIZE = 0x10
    CPU_EEPROM_PAGE_MASK = CPU_EEPROM_PAGE_SIZE - 1

    def __init__(self):
        log = Logger(__name__)
        self.logger = log.getLogger()

    # expects bus number and hex adress strings
    def dump_cpu_eeprom(self, bnum, addr):
        bus = None
        try:
            bus = SMBus(int(bnum))

            offset = 0
            data = []
            eeprom_addr = int(addr, 16)
            while offset < self.CPU_EEPROM_SIZE:
                blk_off = offset & self.CPU_EEPROM_PAGE_MASK
                _len = self.CPU_EEPROM_SIZE - offset
                maxlen = self.CPU_EEPROM_PAGE_SIZE - \
                    (blk_off & self.CPU_EEPROM_PAGE_MASK)
                _len = min(_len, maxlen)

                for _ in range(_len):
                    res = bus.read_byte(eeprom_addr)
                    data.append(res)

                offset = offset + _len

            return data
        except (OSError, ValueError) as e:
            self.logger.error("Dump CPU EEPROM fail, error: %s", e)
            return None
        finally:
            # None if SMBus() failed: the finally used to raise
            # UnboundLocalError over its error
            if bus is not None:
                bus.close()
