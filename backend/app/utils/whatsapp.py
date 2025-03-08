from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import current_app
import time
import logging
import pickle
import os
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppBot:
    def __init__(self):
        self.session_file = 'whatsapp_session.pkl'
        self.message_queue = queue.Queue()
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options)

        # Load existing session if available
        if os.path.exists(self.session_file):
            self.driver.get('https://web.whatsapp.com/')
            with open(self.session_file, 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            self.driver.refresh()
            logger.info("Loaded existing WhatsApp session")
        else:
            self.driver.get('https://web.whatsapp.com/')
            logger.info("Please scan the QR code within 20 seconds")
            time.sleep(20)  # Manual QR scan
            with open(self.session_file, 'wb') as f:
                pickle.dump(self.driver.get_cookies(), f)
            logger.info("New WhatsApp session saved")

    def send_message(self, phone_number, message):
        try:
            url = f'https://web.whatsapp.com/send?phone={phone_number}&text={message}'
            self.driver.get(url)
            message_box = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@title="Type a message"]'))
            )
            message_box.send_keys(Keys.ENTER)
            time.sleep(3)  # Increased wait for reliability
            logger.info(f"Message sent to {phone_number}")
        except Exception as e:
            logger.error(f"Error sending message to {phone_number}: {str(e)}")  # Fixed f-string
            raise

    def close(self):
        self.driver.quit()
        logger.info("WhatsApp bot closed")

def send_whatsapp_message(phone_number, message):
    bot = current_app.whatsapp_bot
    try:
        bot.send_message(phone_number, message)
        time.sleep(5)  # Rate limit to avoid WhatsApp bans
    except Exception as e:
        logger.warning(f"Failed to send message to {phone_number}, added to queue: {str(e)}")
        bot.message_queue.put((phone_number, message))
        # Note: Queue processing would need a separate worker/thread (not implemented here)