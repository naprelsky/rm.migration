# -*- coding: utf-8 -*-
""" Unit test module """

import unittest
from migration import Workload, MountPoint, MigrationTarget


class TestWorkload(unittest.TestCase):
    def setUp(self):
        self.wl1 = Workload('192.168.1.3')
        self.wl1.set_credentials('admin', 'admin')

        self.wl2 = Workload('')
        self.wl3 = Workload('192.168.1.1')

    def test_connect(self):
        self.assertTrue(self.wl1.connect())

    def test_authorize(self):
        self.assertTrue(self.wl1.authorize())

    def test_connect_no_ip(self):
        with self.assertRaises(Exception):
            self.wl2.connect()

    def test_connect_no_credentials(self):
        with self.assertRaises(Exception):
            self.wl3.connect()


class TestMountPoint(unittest.TestCase):
    def setUp(self):
        self.mp1 = MountPoint('C:\\')

    def test_has_size(self):
        self.assertGreater(self.mp1.total_size, 0)


class TestMigrationTarget(unittest.TestCase):
    def setUp(self):
        self.mt = MigrationTarget('aws')
        self.mt.set_cloud_credentials('admin', 'admin')

    def test_unsupported(self):
        with self.assertRaises(Exception):
            MigrationTarget('openstack')

    def test_cloud_connection(self):
        self.assertTrue(self.mt.connect_to_cloud())


if __name__ == '__main__':
    unittest.main()
