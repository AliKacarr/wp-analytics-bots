"""
Bu Python scripti, WhatsApp Web üzerinde belirli bir gruba otomatik mesaj gönderebilmek için Selenium kullanır.
Sohbet adı ve göndermek istediğiniz mesaj kodda (değişkenleri kodda özelleştiriniz) tanımlanmıştır.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
from logout_whatsapp import logout_whatsapp

def main():
    group_name = "Okuma Takip Grubu"  # Sohbet/grup adı
    message_text = "Merhaba, bu bir test mesajıdır."  # Gönderilecek mesaj

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--new-window")

    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://web.whatsapp.com/")
    except Exception as e:
        print("Chrome başlatılamadı:", e)
        sys.exit(1)

    try:
        search_xpath = '//div[@role="textbox" and @aria-label="Arama metni giriş alanı" and @contenteditable="true"]'
        WebDriverWait(driver, 100, poll_frequency=2).until(EC.presence_of_element_located((By.XPATH, search_xpath)))
    except Exception:
        print("WhatsApp Web yüklenemedi.")
        driver.quit()
        sys.exit(1)

    # Sohbeti bul ve aç
    try:
        search_box = driver.find_element(By.XPATH, search_xpath)
        search_box.click()
        search_box.send_keys(group_name)
        pane_side_xpath = '//div[@id="pane-side"]'
        WebDriverWait(driver, 20, poll_frequency=1).until(EC.presence_of_element_located((By.XPATH, pane_side_xpath)))
        group_divs = WebDriverWait(driver, 20, poll_frequency=1).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="pane-side"]//div[contains(@class,"x10l6tqk") and contains(@class,"xh8yej3") and contains(@class,"x1g42fcv")]'))
        )
        for div in group_divs:
            try:
                span = div.find_element(By.XPATH, './/span[@title]')
                if span.get_attribute("title") == group_name:
                    clickable_span = WebDriverWait(driver, 20, poll_frequency=1).until(
                        EC.element_to_be_clickable(span)
                    )
                    clickable_span.click()
                    break
            except Exception:
                continue
    except Exception:
        print("Sohbet bulunamadı. Lütfen sohbeti manuel olarak açın ve Enter'a basın.")
        search_box.send_keys(" Sohbet bulunamadı. Lütfen sohbeti seçiniz.")
        input()


    # Mesaj kutusunu bul ve mesajı gönder
    try:
        # Doğru mesaj kutusu XPath'i (mesaj-alanı.html'den)
        message_box_xpath = '//div[contains(@class,"_ak1r")]//div[contains(@class,"x1n2onr6") and contains(@class,"xh8yej3") and contains(@class,"lexical-rich-text-input")]/div[@contenteditable="true"]'
        message_box = WebDriverWait(driver, 20, poll_frequency=1).until(
            EC.element_to_be_clickable((By.XPATH, message_box_xpath))
        )
        message_box.click()
        message_box.send_keys(message_text)
    
        # Gönder butonunun aktif olmasını bekle (gonder-buton.html'den)
        send_button_xpath = '//button[@aria-label="Gönder" and @data-tab="11"]'
        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, send_button_xpath))
        )
        send_button.click()
        print("Mesaj gönderildi.")
    except Exception as e:
        print("Mesaj gönderilemedi:", e)
        safe_logout_whatsapp(driver)
        driver.quit()
        sys.exit(1)

    # Mesajın gönderildiğini kontrol et
    try:
        print("Mesajın gönderildiğini kontrol ediyorum...")
        message_found = False
        msg_div = None

        def find_message(driver):
            nonlocal message_found, msg_div
            messages_container_xpath = '//*[@id="main"]/div[3]/div/div[2]/div[3]'
            try:
                messages_container = driver.find_element(By.XPATH, messages_container_xpath)
                msg_divs = messages_container.find_elements(By.XPATH, './div')
                if msg_divs:
                    for div in reversed(msg_divs[-20:]):
                        try:
                            spans = div.find_elements(By.XPATH, f'.//span[text()="{message_text}"]')
                            if spans:
                                message_found = True
                                msg_div = div
                                return True
                        except Exception:
                            continue
            except Exception:
                pass
            return False

        try:
            WebDriverWait(driver, 30, poll_frequency=2).until(find_message)
        except Exception:
            pass

        if not message_found:
            print(f"'{message_text}' mesajı 30 saniye içinde bulunamadı.")
        else:
            print(f"'{message_text}' mesajı bulundu, gönderim durumu kontrol ediliyor...")

            def check_sent(driver):
                try:
                    check_icon = msg_div.find_elements(By.XPATH, './/span[@data-icon="msg-check"]')
                    dblcheck_icon = msg_div.find_elements(By.XPATH, './/span[@data-icon="msg-dblcheck"]')
                    return bool(check_icon or dblcheck_icon)
                except Exception:
                    return False

            try:
                WebDriverWait(driver, 20, poll_frequency=5).until(check_sent)
                print(f"'{message_text}' mesajı başarıyla gönderildi ve grupta görünüyor.")
            except Exception:
                # If not found, continue checking with 20 second intervals for 80 seconds
                WebDriverWait(driver, 80, poll_frequency=20).until(check_sent)
                print(f"'{message_text}' mesajı bulundu ancak gönderildiği onaylanamadı.")
    except Exception as e:
        print("Mesaj ve gönderim durumu kontrolünde hata:", e)

    safe_logout_whatsapp(driver)
    driver.quit()

def safe_logout_whatsapp(driver):
    try:
        if "web.whatsapp.com" in driver.current_url:
            logout_whatsapp(driver)
    except Exception:
        pass

if __name__ == "__main__":
    main()