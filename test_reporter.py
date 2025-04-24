import unittest
import reporter
from os import path, environ, remove

class TestReporter(unittest.TestCase):

    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)
        environ['LOG_DIR'] = "/home/matvey/Documents/Work/ADAM-Server/Reporting/modules/test_files"

    
    def test_report_with_single_date_generated_when_start_and_end_equal(self):
        start: str = "2025-04-17"
        end: str = "2025-04-17"

        reporter.report(start=start, end=end)

        self.assertTrue(path.isfile(f"./reports/report-{start}.tex"))

        # Delte generated report after testing
        remove(f"./reports/report-{start}.tex")


    def test_report_with_time_frame_generated_when_start_and_end_are_different(self):
        start: str = "2025-04-01"
        end: str = "2025-04-17"

        reporter.report(start=start, end=end)

        self.assertTrue(path.isfile(f"./reports/report-{start}-{end}.tex"))

        # Delte generated report after testing
        remove(f"./reports/report-{start}-{end}.tex")


    def test_full_report_generated_from_earliest_log_to_latest_log(self):
        start: str = "2025-04-06"
        end: str = "2025-04-17" 
        ""
        reporter.report(full=True)

        self.assertTrue(path.isfile(f"./reports/report-{start}-{end}.tex"))

        # Delte generated report after testing
        remove(f"./reports/report-{start}-{end}.tex")


if __name__ == '__main__':
    unittest.main()