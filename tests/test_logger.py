# type: ignore
import os.path
import socket
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from freezegun import freeze_time

from AntEye.Loggers import logger
from AntEye.Loggers.file import FileLogger, HTMLLogger
from AntEye.Monitors.monitor import MonitorFail, MonitorNull
from AntEye.AntEye import AntEye
from AntEye.version import VERSION


class TestLogger(unittest.TestCase):
    def test_default(self):
        config_options = {}
        test_logger = logger.Logger(config_options)
        self.assertEqual(
            test_logger.dependencies, [], "logger did not set default dependencies"
        )

    def test_dependencies(self):
        config_options = {"depend": ["a", "b"]}
        test_logger = logger.Logger(config_options)
        self.assertEqual(
            test_logger.dependencies,
            ["a", "b"],
            "logger did not set dependencies to given list",
        )
        with self.assertRaises(TypeError):
            test_logger.dependencies = "moo"
        test_logger.dependencies = ["b", "c"]
        self.assertEqual(
            test_logger.check_dependencies(["a"]),
            True,
            "logger thought a dependency had failed",
        )
        self.assertEqual(
            test_logger.connected, True, "logger did not think it was connected"
        )
        self.assertEqual(
            test_logger.check_dependencies(["a", "b"]),
            False,
            "logger did not think a dependency failed",
        )
        self.assertEqual(
            test_logger.connected, False, "logger thought it was connected"
        )

    def test_groups(self):
        with patch.object(logger.Logger, "save_result2") as mock_method:
            this_logger = logger.Logger({"groups": "nondefault"})
            s = AntEye(Path("tests/monitor-empty.ini"))
            s.add_monitor("test", MonitorNull())
            s.log_result(this_logger)
        mock_method.assert_not_called()

        with patch.object(logger.Logger, "save_result2") as mock_method:
            this_logger = logger.Logger({"groups": "nondefault"})
            s = AntEye(Path("tests/monitor-empty.ini"))
            s.add_monitor("test", MonitorNull("unnamed", {"group": "nondefault"}))
            s.log_result(this_logger)
        mock_method.assert_called_once()


class TestFileLogger(unittest.TestCase):
    @freeze_time("2020-04-18 12:00+00:00")
    def test_file_append(self):
        temp_logfile = tempfile.mkstemp()[1]
        with open(temp_logfile, "w") as fh:
            fh.write("the first line\n")
        file_logger = FileLogger({"filename": temp_logfile, "buffered": False})
        monitor = MonitorNull()
        monitor.run_test()
        file_logger.save_result2("null", monitor)
        self.assertTrue(os.path.exists(temp_logfile))
        ts = str(int(time.time()))
        with open(temp_logfile, "r") as fh:
            self.assertEqual(fh.readline().strip(), "the first line")
            self.assertEqual(
                fh.readline().strip(), "{} AntEye starting".format(ts)
            )
            self.assertEqual(fh.readline().strip(), "{} null: ok (0.000s)".format(ts))
        try:
            os.unlink(temp_logfile)
        except PermissionError:
            # Windows won't remove a file which is in use
            pass

    @freeze_time("2020-04-18 12:00+01:00")
    def test_file_nonutc(self):
        temp_logfile = tempfile.mkstemp()[1]
        file_logger = FileLogger({"filename": temp_logfile, "buffered": False})
        monitor = MonitorNull()
        monitor.run_test()
        file_logger.save_result2("null", monitor)
        self.assertTrue(os.path.exists(temp_logfile))
        ts = str(int(time.time()))
        with open(temp_logfile, "r") as fh:
            self.assertEqual(
                fh.readline().strip(), "{} AntEye starting".format(ts)
            )
            self.assertEqual(fh.readline().strip(), "{} null: ok (0.000s)".format(ts))
        try:
            os.unlink(temp_logfile)
        except PermissionError:
            # Windows won't remove a file which is in use
            pass

    @freeze_time("2020-04-18 12:00+00:00")
    def test_file_utc_iso(self):
        temp_logfile = tempfile.mkstemp()[1]
        file_logger = FileLogger(
            {"filename": temp_logfile, "buffered": False, "dateformat": "iso8601"}
        )
        monitor = MonitorNull()
        monitor.run_test()
        file_logger.save_result2("null", monitor)
        self.assertTrue(os.path.exists(temp_logfile))
        with open(temp_logfile, "r") as fh:
            self.assertEqual(
                fh.readline().strip(),
                "2020-04-18 12:00:00+00:00 AntEye starting",
            )
            self.assertEqual(
                fh.readline().strip(), "2020-04-18 12:00:00+00:00 null: ok (0.000s)",
            )
        try:
            os.unlink(temp_logfile)
        except PermissionError:
            # Windows won't remove a file which is in use
            pass

    @freeze_time("2020-04-18 12:00+01:00")
    def test_file_nonutc_iso_utctz(self):
        temp_logfile = tempfile.mkstemp()[1]
        file_logger = FileLogger(
            {"filename": temp_logfile, "buffered": False, "dateformat": "iso8601"}
        )
        monitor = MonitorNull()
        monitor.run_test()
        file_logger.save_result2("null", monitor)
        self.assertTrue(os.path.exists(temp_logfile))
        with open(temp_logfile, "r") as fh:
            self.assertEqual(
                fh.readline().strip(),
                "2020-04-18 11:00:00+00:00 AntEye starting",
            )
            self.assertEqual(
                fh.readline().strip(), "2020-04-18 11:00:00+00:00 null: ok (0.000s)",
            )
        try:
            os.unlink(temp_logfile)
        except PermissionError:
            # Windows won't remove a file which is in use
            pass

    @freeze_time("2020-04-18 12:00+01:00")
    def test_file_nonutc_iso_nonutctz(self):
        temp_logfile = tempfile.mkstemp()[1]
        file_logger = FileLogger(
            {
                "filename": temp_logfile,
                "buffered": False,
                "dateformat": "iso8601",
                "tz": "Europe/Warsaw",
            }
        )
        monitor = MonitorNull()
        monitor.run_test()
        file_logger.save_result2("null", monitor)
        self.assertTrue(os.path.exists(temp_logfile))
        with open(temp_logfile, "r") as fh:
            self.assertEqual(
                fh.readline().strip(),
                "2020-04-18 13:00:00+02:00 AntEye starting",
            )
            self.assertEqual(
                fh.readline().strip(), "2020-04-18 13:00:00+02:00 null: ok (0.000s)",
            )
        try:
            os.unlink(temp_logfile)
        except PermissionError:
            # Windows won't remove a file which is in use
            pass


class TestHTMLLogger(unittest.TestCase):
    @staticmethod
    @freeze_time("2020-04-18 12:00:00+00:00")
    def _write_html(logger_options: dict = None) -> str:
        if logger_options is None:
            logger_options = {}
        with patch.object(socket, "gethostname", return_value="fake_hostname.local"):
            temp_htmlfile = tempfile.mkstemp()[1]
            logger_options.update({"filename": temp_htmlfile})
            html_logger = HTMLLogger(logger_options)
            monitor1 = MonitorNull()
            monitor2 = MonitorFail("fail", {})
            monitor1.run_test()
            monitor2.run_test()
            html_logger.start_batch()
            html_logger.save_result2("null", monitor1)
            html_logger.save_result2("fail", monitor2)
            html_logger.end_batch()
        return temp_htmlfile

    def _compare_files(self, test_file, golden_file):
        test_fh = open(test_file, "r")
        golden_fh = open(golden_file, "r")
        self.maxDiff = 6000
        golden_data = golden_fh.read()
        golden_data = golden_data.replace("__VERSION__", VERSION)
        self.assertMultiLineEqual(test_fh.read(), golden_data)
        test_fh.close()
        golden_fh.close()

    def test_html(self):
        test_file = self._write_html()
        golden_file = "tests/html/test1.html"
        self._compare_files(test_file, golden_file)

    def test_html_tz(self):
        test_file = self._write_html({"tz": "Europe/Warsaw"})
        golden_file = "tests/html/test2.html"
        self._compare_files(test_file, golden_file)
