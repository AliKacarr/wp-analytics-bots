"""
Bu Python scripti, WhatsApp Web üzerinde belirli bir gruptaki mesajları otomatik olarak analiz ederek, belirli bir tarih aralığında yapılan anketin sonuçlarını toplar.
Kullanıcıdan grup adı ve anket seçenekleri (değişkenleri kodda özelleştiriniz) alınır, ilgili sohbet bulunur ve mesajlar taranır.
Her seçenek için, oy verenlerin isimleri virgül ile ayrılmış şekilde terminale yazdırılır.
Script, platforma göre WhatsApp Web arayüzünü otomatik açar ve sohbeti bulur.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logout_whatsapp import logout_whatsapp
import time
import datetime
import sys
import os
import re
import platform

def main():
    # Selenium ve Chrome loglarını devre dışı bırak
    os.environ['WDM_LOG_LEVEL'] = '0'
    os.environ['WDM_PRINT_FIRST_LINE'] = 'False'

    # Chrome ayarlarını yapılandır
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--log-level=3")  # Sadece kritik hataları göster
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # DevTools mesajını gizle
    options.add_argument("--new-window")

    # İşletim sistemini kontrol et
    is_mobile = platform.system() == "Android" or platform.system() == "iOS"
    if is_mobile:
            sys.exit(0)

    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://web.whatsapp.com/")
    except Exception as e:
        sys.exit(1)

    try:
        search_xpath = '//div[@contenteditable="true"][@data-tab="3"]'
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, search_xpath)))
    except Exception as e:
        driver.quit()
        sys.exit(1)

    group_name = "Okuma Takip Grubu"  # Sohbetin adını buraya girin
    options = {
        "okudum": ["okudum", "okuDum", "Okudum", "ben okudum"], # Aranacak kelimeleri girin
        "okumadım": ["Okumadım", "okumadım", "ben okumadım"]
    }
    user_votes = {key: [] for key in options.keys()}
    start_datetime_str = "21:00 4/5/2025" # Başlangıç tarih ve saatini seçin
    start_datetime_str = "21:00 4/12/2026" # Başlangıç tarih ve saati seçin

    def convert_to_wp_date_format(date_str):
        parts = date_str.split()
        if len(parts) == 2:
            time_part, date_part = parts
            date_segments = date_part.split('/')
            if len(date_segments) == 3:  # gün/ay/yıl -> ay/gün/yıl
                day = date_segments[0].lstrip('0') or '0' # baştaki sıfırları sil
                month = date_segments[1].lstrip('0') or '0'
                year = date_segments[2]
                return f"{time_part} {month}/{day}/{year}"
        return date_str

    start_datetime_str = convert_to_wp_date_format(start_datetime_str)
    end_datetime_str = convert_to_wp_date_format(end_datetime_str)
    start_datetime = datetime.datetime.strptime(start_datetime_str, "%H:%M %m/%d/%Y")
    end_datetime = datetime.datetime.strptime(end_datetime_str, "%H:%M %m/%d/%Y")

    try:
            search_box = driver.find_element(By.XPATH, search_xpath)
            search_box.click()
            search_box.send_keys(group_name)
            group_xpath = f'//span[@title="{group_name}"]'
            group = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, group_xpath)))
            group.click()
    except Exception as e:
        print("Sohbet bulunamadı. Lütfen istediğiniz sohbeti manuel olarak açın ve Enter'a basın.")
        search_box.send_keys(" Sohbet bulunamadı. Lütfen sohbeti seçiniz.")
        input()

    try:
        messages = driver.find_elements(By.XPATH, '//div[contains(@class,"message-in") or contains(@class,"message-out")]')
        for msg in messages:
            try:
                text = msg.text
                try:
                    selectors = [
                        './/div[contains(@class,"copyable-text")]',
                        './/span[contains(@class,"copyable-text")]',
                        './/div[contains(@data-pre-plain-text,"")]'
                    ]
                    user_info = None
                    for selector in selectors:
                        try:
                            elements = msg.find_elements(By.XPATH, selector)
                            for element in elements:
                                attr = element.get_attribute("data-pre-plain-text")
                                if attr and "[" in attr:
                                    user_info = attr
                                    break
                            if user_info:
                                break
                        except:
                            continue
                    if not user_info:
                        continue
                    if "[" in user_info:
                        try:
                            saat_tarih = user_info.split("[")[1].split("]")[0]
                            time_str, date_str = [x.strip() for x in saat_tarih.split(",")]
                            user = user_info.split("]")[1].split(":")[0].strip()
                            msg_datetime_str = f"{time_str} {date_str}"
                            msg_datetime = datetime.datetime.strptime(msg_datetime_str, "%H:%M %m/%d/%Y")
                        except Exception:
                            print(f"Tarih ayrıştırılamadı: {user_info}")
                            continue
                        print(f"Mesaj tarihi: {msg_datetime}")
                        if not (start_datetime <= msg_datetime <= end_datetime):
                            print("Mesaj tarih aralığın dışında.")
                            continue
                        else:
                            print("Mesaj tarih aralığın içinde.")
                    else:
                        continue
                except Exception:
                    continue
                option_found = False
                clean_text = text.strip()
                clean_text = re.sub(r'\s\d{1,2}:\d{2}$', '', clean_text)
                clean_text = re.sub(r'Düzenlendi\d{1,2}:\d{2}$', '', clean_text)
                if user in clean_text and clean_text.startswith(user):
                    clean_text = clean_text[len(user):].strip()
                print(f"\nKullanıcı: {user}")
                print(f"Orijinal mesaj: '{text}'")
                print(f"Temizlenmiş mesaj: '{clean_text}'")
                for option_key, option_variants in options.items():
                    for variant in option_variants:
                        if clean_text.strip() == variant:  # Tam eşleşme kontrolü
                            if user not in user_votes[option_key]:
                                user_votes[option_key].append(user)
                                print(f"✓ Eşleşme bulundu: '{variant}' -> '{option_key}' seçeneğine eklendi")
                                option_found = True
                            else:
                                print(f"! Kullanıcı zaten '{option_key}' seçeneğinde mevcut")
                            break
                    if option_found:
                        break
            except Exception:
                continue
    except Exception:
        pass

    print("\nSonuçlar:")
    for option, users in user_votes.items():
        if users:
            print(f"{option}: {', '.join(users)}")
        else:
            print(f"{option}: ")

    safe_logout_whatsapp(driver)
    driver.quit()

def safe_logout_whatsapp(driver):
    """
    Eğer WhatsApp Web sekmesi açıksa oturumu kapatır.
    """
    try:
        if "web.whatsapp.com" in driver.current_url:
            logout_whatsapp(driver)
    except Exception:
        pass

if __name__ == "__main__":
    main()