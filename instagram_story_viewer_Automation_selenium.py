import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)


# ===================== CONSTANTS =====================
INSTAGRAM_URL = "https://www.instagram.com/"
STORY_URL_TEMPLATE = "https://www.instagram.com/stories/{}/"

DEFAULT_WAIT = 10 
MAX_STORIES = 30 
MAX_STORY_WAIT = 500  # seconds


# ===================== LOGGING =====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("instagram_automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ===================== MAIN CLASS =====================
class InstagramStoryViewer:

    def __init__(self, username: str, password: str):
        logger.info("Initializing Instagram Story Viewer")

        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--mute-audio")

        try:
            self.driver = uc.Chrome(options=chrome_options)
        except Exception as e:
            logger.error(f"Chrome initialization failed: {e}")
            raise

        self.wait = WebDriverWait(self.driver, DEFAULT_WAIT)
        self.username = username
        self.password = password

    # ===================== LOGIN =====================
    def login(self) -> bool:
        logger.info("Logging in to Instagram")
        self.driver.get(INSTAGRAM_URL)
        time.sleep(2)

        # Accept cookies (if present)
        try:
            cookie_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(),'Accept') or contains(text(),'Allow')]")
                )
            )
            cookie_btn.click()
            logger.info("Cookies accepted")
        except TimeoutException:
            logger.info("No cookie dialog")

        # Already logged in check
        try:
            self.driver.find_element(By.XPATH, "//img[contains(@alt,'Profile')]")
            logger.info("Already logged in")
            return True
        except NoSuchElementException:
            pass

        try:
            self.wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(self.username)
            self.wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(self.password)

            self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            ).click()
            cur_url = self.driver.current_url
            while f"https://www.instagram.com/accounts/onetap/?next=%2F" not in cur_url:
                    cur_url = self.driver.current_url
                    time.sleep(1)


            if "challenge" in self.driver.current_url or "captcha" in self.driver.current_url:
                input("⚠️ Complete security check manually and press ENTER...")

            logger.info("Login successful")
            return True

        except TimeoutException:
            logger.error("Login elements not found")
            return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False


    # ===================== START MONITORING =====================
    def start_monitoring(self):
        monitor_script = """
        window.story_click = false;
        
        // 1. Monitor Mouse Clicks on Specific Divs
        document.addEventListener('click', function(e) {
            if (e.target.closest('.x1i10hfl') || e.target.closest('.x1ey2m1c')) {
                window.story_click = true;
            }
        }, true);

        // 2. Monitor Keyboard (Right Arrow)
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowRight') {
                window.story_click = true;
            }
        }, true);
        """
        self.driver.execute_script(monitor_script)

    # ===================== VIEW STORY =====================
    def view_story(self, insta_id: str) -> bool:
        story_url = STORY_URL_TEMPLATE.format(insta_id)
        logger.info(f"Opening story URL: {story_url}")

        try:
            self.driver.get(story_url)
            time.sleep(5)

            if "/stories/" not in self.driver.current_url:
                logger.warning("No stories available (redirected)")
                return False

            # Start monitoring for manual skips
            self.start_monitoring()

            # Try clicking "View story" button
            try:
                self.wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, ".x1i10hfl.xdl72j9.x1q0g3np.x6s0dn4.x78zum5.x1f6kntn.xwhw2v2[role='button']")
                    )).click()
            except TimeoutException:
                logger.info("View story button not found — assuming auto-play")

            story_count = 1
            start_time = time.time()

            while story_count < MAX_STORIES:
                if time.time() - start_time > MAX_STORY_WAIT:
                    logger.warning(f"Max story wait exceeded: {MAX_STORY_WAIT} seconds")
                    break

                if "/stories/" not in self.driver.current_url:
                    break

                try:
                    self.driver.find_element(By.TAG_NAME, "video")
                    logger.info("Video story detected, waiting 10 seconds")
                    click_check = self.driver.execute_script("return window.story_click;")
                    if click_check:
                            story_count += 1
                            self.driver.execute_script("window.story_click = false;")
                    time.sleep(10)
                except NoSuchElementException:
                    logger.info("Image story detected, waiting 5 seconds")
                    click_check = self.driver.execute_script("return window.story_click;")
                    if click_check:
                            story_count += 1
                            self.driver.execute_script("window.story_click = false;")
                    time.sleep(5)

                try:
                    selector_1 = "div.xtijo5x.x1ey2m1c"
                    selector_2 = "div[role='button'] svg[aria-label='Next']"
                    if self.driver.find_elements(By.CSS_SELECTOR, selector_1) or \
                    self.driver.find_elements(By.CSS_SELECTOR, selector_2):
                        click_check = self.driver.execute_script("return window.story_click;")
                        if click_check:
                            story_count += 1
                            time.sleep(1)
                            self.driver.execute_script("window.story_click = false;")
                        logger.info(f"Viewing story {story_count} for {insta_id}")
                        ActionChains(self.driver).send_keys(Keys.ARROW_RIGHT).perform()

                except NoSuchElementException:
                    logger.info("No next story button found, possibly last story")
                    break

            logger.info(f"Finished stories for {insta_id} | Count: {story_count}")
            return True

        except WebDriverException as e:
            logger.error(f"Story error: {e}")
            return False

    # ===================== HOME CHECK =====================
    def is_on_homepage(self) -> bool:
        return self.driver.current_url.rstrip("/") == INSTAGRAM_URL.rstrip("/")

    # ===================== PROCESS FILE =====================
    def process_all_ids(self, file_path: str):
        try:
            with open(file_path, "r") as f:
                ids = [i.strip() for i in f if i.strip()]

            for idx, insta_id in enumerate(ids, start=1):
                logger.info(f"[{idx}/{len(ids)}] Processing {insta_id}")
                self.view_story(insta_id)
                time.sleep(2)

        except Exception as e:
            logger.error(f"ID processing failed: {e}")

    # ===================== CLEANUP =====================
    def close(self):
        if self.driver:
            self.driver.quit()


# ===================== ENTRY POINT =====================
if __name__ == "__main__":
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path)

    USERNAME = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')

    viewer = InstagramStoryViewer(USERNAME, PASSWORD)

    try:
        if viewer.login():
            viewer.process_all_ids("instagramid.txt")
        else:
            logger.error("Login failed")
    finally:
        viewer.close()
