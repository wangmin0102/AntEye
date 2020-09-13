# type: ignore
import unittest

from AntEye.Monitors import host
from AntEye.Monitors.monitor import MonitorConfigurationError


class TestHostMonitors(unittest.TestCase):

    safe_config = {"partition": "/", "limit": "10G"}

    one_KB = 1024
    one_MB = one_KB * 1024
    one_GB = one_MB * 1024
    one_TB = one_GB * 1024

    def test_DiskSpace_brokenConfigOne(self):
        config_options = {}
        with self.assertRaises(MonitorConfigurationError):
            host.MonitorDiskSpace("test", config_options)

    def test_DiskSpace_brokenConfigTwo(self):
        config_options = {"partition": "/"}
        with self.assertRaises(MonitorConfigurationError):
            host.MonitorDiskSpace("test", config_options)

    def test_DiskSpace_brokenConfigThree(self):
        config_options = {"partition": "/", "limit": "moo"}
        with self.assertRaises(ValueError):
            host.MonitorDiskSpace("test", config_options)

    def test_DiskSpace_correctConfig(self):
        m = host.MonitorDiskSpace("test", self.safe_config)
        self.assertIsInstance(m, host.MonitorDiskSpace)

    def test_DiskSpace_size_to_bytes(self):
        self.assertEqual(None, host._size_string_to_bytes(None))

        size = host._size_string_to_bytes("10G")
        self.assertEqual(size, 10737418240, "Failed to convert 10G to bytes")

        size = host._size_string_to_bytes("10M")
        self.assertEqual(size, 10485760, "Failed to convert 10M to bytes")

        size = host._size_string_to_bytes("10K")
        self.assertEqual(size, 10240, "Failed to convert 10K to bytes")

        size = host._size_string_to_bytes("10")
        self.assertEqual(size, 10, "Failed to convert 10 to bytes")

        with self.assertRaises(ValueError):
            host._size_string_to_bytes("a")

    def test_DiskSpace_bytes_to_size_string(self):
        s = host._bytes_to_size_string(10 * self.one_TB)
        self.assertEqual(s, "10.00TiB", "Failed to convert 10TiB to string")

        s = host._bytes_to_size_string(10 * self.one_GB)
        self.assertEqual(s, "10.00GiB", "Failed to convert 10GiB to string")

        s = host._bytes_to_size_string(10 * self.one_MB)
        self.assertEqual(s, "10.00MiB", "Failed to convert 10MiB to string")

        s = host._bytes_to_size_string(10 * self.one_KB)
        self.assertEqual(s, "10.00KiB", "Failed to convert 10KiB to string")

        s = host._bytes_to_size_string(1)
        self.assertEqual(s, "1", "Failed to convert 1B to string")

    def test_DiskSpace_meta(self):
        m = host.MonitorDiskSpace("test", self.safe_config)

        self.assertEqual(
            m.describe(),
            "Checking for at least 10.00GiB free space on /",
            "Failed to verify description",
        )

        self.assertTupleEqual(
            m.get_params(), (10 * self.one_GB, "/"), "Failed to verify params"
        )

    def test_DiskSpace_free(self):
        # Hopefully our test machine has at least 1 byte free on /
        config_options = {"partition": "/", "limit": "1"}
        m = host.MonitorDiskSpace("test", config_options)
        m.run_test()
        self.assertTrue(m.test_success())

        # and hopefully it has a sensible-sized root partition
        config_options = {"partition": "/", "limit": "100000G"}
        m = host.MonitorDiskSpace("test", config_options)
        m.run_test()
        self.assertFalse(m.test_success())

    def test_DiskSpace_invalid_partition(self):
        config_options = {"partition": "moo", "limit": "1"}
        m = host.MonitorDiskSpace("test", config_options)
        m.run_test()
        self.assertFalse(m.test_success(), "Monitor did not fail")
        self.assertRegexpMatches(
            m.last_result,
            "Couldn't get free disk space",
            "Monitor did not report error correctly",
        )

    def test_DiskSpace_get_params(self):
        config_options = {"partition": "/", "limit": "1"}
        m = host.MonitorDiskSpace("test", config_options)
        self.assertTupleEqual(m.get_params(), (1, "/"))

    def test_Filestat_get_params(self):
        config_options = {"maxage": "10", "minsize": "20", "filename": "/test"}
        m = host.MonitorFileStat("test", config_options)
        self.assertTupleEqual(m.get_params(), ("/test", 20, 10))

    def test_Command_get_params(self):
        config_options = {"command": "ls /", "result_regexp": "moo", "result_max": "10"}
        m = host.MonitorCommand("test", config_options)
        self.assertTupleEqual(m.get_params(), (["ls", "/"], "moo", None))

        config_options = {"command": "ls /", "result_max": "10"}
        m = host.MonitorCommand("test", config_options)
        self.assertTupleEqual(m.get_params(), (["ls", "/"], "", 10))


if __name__ == "__main__":
    unittest.main()
