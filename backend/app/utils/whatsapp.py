from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from flask import current_app
import time

class WhatsAppBot:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get('https://web.whatsapp.com/')
        # Manual QR code scan required for initial setup
        print("Please scan the QR code within 20 seconds")
        time.sleep(20)  # Adjust based on login time

    def send_message(self, phone_number, message):
        try:
            # Navigate to chat
            url = f'https://web.whatsapp.com/send?phone={phone_number}&text={message}'
            self.driver.get(url)
            time.sleep(5)  # Wait for chat to load

            # Send message
            message_box = self.driver.find_element(By.XPATH, '//div[@title="Type a message"]')
            message_box.send_keys(Keys.ENTER)
            time.sleep(2)  # Wait for message to send

        except Exception as e:
            print(f"Error sending message: {e}")
            raise

def send_whatsapp_message(phone_number, message):
    bot = current_app.whatsapp_bot
    bot.send_message(phone_number, message)