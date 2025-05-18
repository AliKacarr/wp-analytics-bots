from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def logout_whatsapp(driver, timeout=10):
    try:
        # Üç nokta menüsüne tıkla
        menu_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[3]/div/div[3]/header/header/div/span/div/div[2]/button/span'))
        )
        menu_button.click()
        # "Çıkış yap" seçeneğine tıkla
        logout_option = WebDriverWait(driver, timeout, poll_frequency=1).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/span[6]/div/ul/div/li[4]'))
        )
        logout_option.click()
        # "Çıkış yap" butonuna tıkla
        logout_button = WebDriverWait(driver, timeout, poll_frequency=1).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div[2]/div/button[2]'))
        )
        logout_button.click()

        # Çıkış sonrası ana ekranı bekle
        try:
            WebDriverWait(driver, timeout, poll_frequency=2).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[contains(@class,"_aiwn") and contains(@class,"_aiwl") and contains(@class,"app-wrapper-web") and contains(@class,"font-fix") and contains(@class,"os-win") and contains(@class,"_ap4q")]'))
            )
        except Exception:
            pass

        print("\nWhatsApp oturumu kapatıldı.")
    except Exception as e:
        print("Oturum kapatılamadı veya zaten kapalı:", e)
