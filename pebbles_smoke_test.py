# requires:
#   - phantomjs or geckodriver installed
#   - selenium from pip

import sys
import unittest
import json
import argparse
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


class SmokeTest(unittest.TestCase):
    def __init__(self, testName, config):
        super(SmokeTest, self).__init__(testName)
        self.config = json.loads(config.read())

    def setUp(self):

        driver = self.config.get("driver", "phantomjs")
        if driver == "PhantomJS":
            self.driver = webdriver.PhantomJS()
            self.driver.delete_all_cookies()
        elif driver == "Firefox":
            self.driver = webdriver.Firefox()
        else:
            raise SystemExit("unknown driver")
        self.img_path = self.config.get("img_path", "/tmp/")
        self.driver.set_window_size(1120, 550)

    def _login(self):
        """
        Do login and wait for the user dashboard to be visible

        Could be made more generic by permitting admin dashboard visible
        :return:
        """
        self.driver.get(self.config["url"])
        self.driver.find_element_by_name(
            'click-show-login').click()
        self.driver.find_element_by_id("email").send_keys(self.config["email"])
        elem = self.driver.find_element_by_id("password")
        elem.send_keys(self.config["password"])
        elem.submit()
        WebDriverWait(self.driver, 3).until(
            expected_conditions.presence_of_element_located((By.ID,
                                                             "user-dashboard"))
        )

    def _logout(self):
        self.driver.get(self.config["url"])
        self.driver.find_element_by_id('logout').click()

    def _test_blueprint_start(self, elem, wait_for_open=False):
        launch_button = elem.find_element_by_css_selector(".panel-footer "
                                                          "span").click()
        start_timeout = self.config.get("timeouts", {}).get(
            "start", 60)
        if not wait_for_open:
            WebDriverWait(self.driver, start_timeout).until(
                expected_conditions.visibility_of_element_located(
                    (By.PARTIAL_LINK_TEXT, "pb-")  # object
                )
            )
        else:
            WebDriverWait(self.driver, start_timeout).until(
                expected_conditions.visibility_of_element_located(
                    (By.PARTIAL_LINK_TEXT, "Open in")  # object
                )
            )
            # have to check non-dummies differently
            # they create a "Click to open" link

    def _test_blueprint_shutdown(self, elem):
        shutdown_button = elem.find_element_by_css_selector("table "
                                                            "button.btn-danger")
        id_ = shutdown_button.id
        shutdown_button.click()
        self._dismiss_shutdown_modal()
        shutdown_timeout = self.config.get("timeouts", {}).get(
            "shutdown", 60)
        WebDriverWait(self.driver, shutdown_timeout).until(
            expected_conditions.invisibility_of_element_located(
                (By.CLASS_NAME, "btn-danger"))
        )

    def _dismiss_shutdown_modal(self):
        """
        Attempts to dismiss a modal by clicking on the first btn-primary
        inside the modal
        :return:
        """
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(
                (By.CLASS_NAME, "modal"))
        )
        yes_button = self.driver.find_element_by_css_selector(
            ".modal .btn-primary").click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.invisibility_of_element_located(
                (By.CLASS_NAME, "modal"))
        )

    def smoke_test(self):
        try:
            self._login()
            elem = self.driver.find_element_by_xpath(
                '//*[@id="user-dashboard"]/div')
            elements = elem.find_elements_by_css_selector("div.panel")
            for child in elem.find_elements_by_css_selector("div.panel"):
                cur_element = child.find_element_by_css_selector(
                    "h3.panel-title")
                blueprint_name = cur_element.text
                for bp in self.config["blueprints"]:
                    if bp in blueprint_name:
                        if "dummy" in blueprint_name.lower():
                            self._test_blueprint_start(child, wait_for_open=False)
                        else:
                            self._test_blueprint_start(child, wait_for_open=True)
                        self._test_blueprint_shutdown(child)
            self._logout()
        except Exception, e:
            import datetime
            fname = datetime.datetime.now().isoformat()+ "_screenshot.png"
            self.driver.save_screenshot(self.img_path + fname)
            sys.stderr.write("failed: " + str(e))
            self._logout()


    def tearDown(self):
        self.driver.quit()


def main(args=None):
    parser = argparse.ArgumentParser(description="Pebbles smoke tester",
                                     usage=("Run with configs to smoke test "
                                            "a running Pebbles instance. "
                                            "Outputs a string (OK/FAIL) that "
                                            "can be "
                                            "redirected to a file. Also "
                                            "returns 0 or nonzero for Posix "
                                            "compliance"))
    parser.add_argument("-c", "--config", type=argparse.FileType("r"),
                        default=sys.stdin, help=("config file in JSON "
                                                 "format. see  "
                                                 "example in "
                                                 "example.config.json for "
                                                 "defaults"
                                                 ))
    parser.add_argument("-o", "--output", default=sys.stdout,
                        type=argparse.FileType("w"),
                        help=("file to print test status string"))
    parser.add_argument("--success", default="OK",
                        help=("text to display if tests run ok"))
    parser.add_argument("--fail", default="FAIL", help=("text to display if "
                                                        "tests do not run ok"))

    args = parser.parse_args()
    suite = unittest.TestSuite()
    suite.addTest(SmokeTest("smoke_test", args.config))
    res = unittest.TextTestRunner(verbosity=0).run(suite)
    if res.wasSuccessful():
        args.output.write(args.success)
    else:
        args.output.write(args.fail)

if __name__ == '__main__':
    main()
