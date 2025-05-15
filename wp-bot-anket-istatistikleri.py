"""
Bu Python scripti, WhatsApp Web üzerinde belirli bir gruptaki anketin sonuçlarını otomatik olarak toplamak için Selenium kullanır.
Grup adı ve anket başlığı kodda tanımlıdır. WhatsApp Web'e giriş yaptıktan sonra bot, ilgili sohbet ve anketi bulur, ardından anket seçeneklerine oy veren kullanıcıları listeler.
Her seçenek için, oy verenlerin isimleri veya numaraları virgül ile ayrılmış şekilde terminale yazdırılır.
Sohbet otomatik bulunamazsa kullanıcıdan sohbeti manuel olarak açması istenir.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logout_whatsapp import logout_whatsapp
import time
import sys

def main():
    group_name = "Okuma Takip Grubu"  # Aranacak sohbetin adını buraya girin
    poll_topic = "13 Mayıs"  # Aranacak anket başlığını buraya girin

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
        search_xpath = '//div[@contenteditable="true"][@data-tab="3"]'
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, search_xpath)))
    except Exception:
        print("WhatsApp Web yüklenemedi.")
        driver.quit()
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
        # Arama sonrası grupların yüklenmesini bekle
        pane_side_xpath = '//div[@id="pane-side"]'
        WebDriverWait(driver, 20, poll_frequency=1).until(EC.presence_of_element_located((By.XPATH, pane_side_xpath)))
        # Grup kutularını bul
        group_divs = WebDriverWait(driver, 20, poll_frequency=1).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="pane-side"]//div[contains(@class,"x10l6tqk") and contains(@class,"xh8yej3") and contains(@class,"x1g42fcv")]'))
        )
        for div in group_divs:
            try:
                # Grup adını içeren span'ı bul
                span = div.find_element(By.XPATH, './/span[@title]')
                if span.get_attribute("title") == group_name:
                    # Tıklanabilir olana kadar bekle
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

    # Anketi bul ve "Oyları görüntüle" butonuna bas
    try:
        messages = driver.find_elements(By.XPATH, '//div[contains(@class,"message-out") or contains(@class,"message-in")]')
        found_poll = False
        for msg in messages:
            try:
                spans = msg.find_elements(By.XPATH, './/span')
                for span in spans:
                    if span.text.strip() == poll_topic:
                        found_poll = True
                        try:
                            view_votes_btn = msg.find_element(By.XPATH, './/button[.//div[contains(text(),"Oyları görüntüle")]]')
                            driver.execute_script("arguments[0].click();", view_votes_btn)
                            time.sleep(2)
                        except Exception:
                            continue
                        break
                if found_poll:
                    break
            except Exception:
                continue
        if not found_poll:
            print("Belirtilen başlıkta anket bulunamadı.")
            driver.quit()
            return
    except Exception:
        print("Mesajlar taranırken hata oluştu.")
        driver.quit()
        return

    # Anket sonuçlarını çek
    try:
        panel_xpath = '//div[contains(@class, "_aig-") and contains(@class, "x9f619")]'
        panel = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, panel_xpath)))
        option_blocks = panel.find_elements(By.XPATH, './/div[contains(@class,"x13mwh8y")]')

        i = 0
        while i < len(option_blocks):
            opt_block = option_blocks[i]
            try:
                user_info = opt_block.find_elements(By.XPATH, './/div[contains(@class,"x178xt8z") and contains(@class,"x13fuv20") and contains(@class,"xyj1x25")]')
                if not user_info:
                    i += 1
                    continue

                option_name = opt_block.find_element(By.XPATH, './/span[contains(@class,"xo1l8bm")]').text

                # "Tümünü gör" butonu varsa tıkla ve kullanıcı listesini güncelle
                try:
                    show_all_btn = opt_block.find_element(By.XPATH, './/button[.//div[contains(text(),"Tümünü gör")]]')
                    driver.execute_script("arguments[0].click();", show_all_btn)
                    time.sleep(1)
                    panel = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, panel_xpath)))
                    option_blocks_new = panel.find_elements(By.XPATH, './/div[contains(@class,"x13mwh8y")]')
                    for new_block in option_blocks_new:
                        try:
                            new_option_name = new_block.find_element(By.XPATH, './/span[contains(@class,"xo1l8bm")]').text
                            if new_option_name == option_name:
                                opt_block = new_block
                                break
                        except Exception:
                            continue
                    user_info = opt_block.find_elements(By.XPATH, './/div[contains(@class,"x178xt8z") and contains(@class,"x13fuv20") and contains(@class,"xyj1x25")]')
                except Exception:
                    pass

                user_names = []
                for user in user_info:
                    try:
                        name_spans = user.find_elements(By.XPATH, './/span[@dir="auto"]')
                        for name_span in name_spans:
                            user_name = name_span.text.strip()
                            if user_name and not any(x in user_name for x in ["Bugün", ":"]):
                                user_names.append(user_name)
                    except Exception:
                        continue

                print(f"{option_name}: {', '.join(user_names)}" if user_names else f"{option_name}: ")

                # Eğer "Tümünü gör" açıldıysa geri dön
                try:
                    back_btn = panel.find_element(By.XPATH, './/div[@role="button" and @aria-label="Geri"]')
                    driver.execute_script("arguments[0].click();", back_btn)
                    time.sleep(1)
                    panel = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, panel_xpath)))
                    option_blocks = panel.find_elements(By.XPATH, './/div[contains(@class,"x13mwh8y")]')
                except Exception:
                    pass
                i += 1
            except Exception:
                i += 1
    except Exception:
        print("Anket sonuçları paneli bulunamadı veya işlenemedi.")

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
