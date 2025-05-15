"""
WhatsApp sohbetlerinden kopyalanan mesajlar üzerinden belirli bir tarih aralığında yapılan anketin sonuçlarını analiz eder.
Kullanıcıdan belirli bir tarih aralığında gelen mesajlar (değişkenleri kodda özelleştiriniz) alınır, mesajlardaki cevaplar önceden tanımlanmış seçeneklerle eşleştirilir ve her seçeneğe oy veren kullanıcılar listelenir.
Her seçenek için, oy verenlerin isimleri virgül ile ayrılmış şekilde terminale yazdırılır.
"""

import time
import datetime
import re
import sys
import subprocess
import clipboard
import platform
import webbrowser

def normalize_date_format(date_str):
    parts = date_str.split()
    if len(parts) == 2:
        time_part, date_part = parts
        date_segments = date_part.split('/')
        if len(date_segments) == 3:
            month = date_segments[0].lstrip('0') or '0'
            day = date_segments[1].lstrip('0') or '0'
            year = date_segments[2]
            return f"{time_part} {month}/{day}/{year}"
    return date_str

def open_whatsapp():
    system = platform.system()
    machine = getattr(platform, 'machine', lambda: "")().lower()
    is_mobile = any(x in machine for x in ['iphone', 'ipad', 'android'])

    try:
        if is_mobile:
            if 'iphone' in machine or 'ipad' in machine:
                webbrowser.open('https://apps.apple.com/app/whatsapp-messenger/id310633997')
            elif 'android' in machine:
                webbrowser.open('https://play.google.com/store/apps/details?id=com.whatsapp')
        else:
            if system == "Windows":
                try:
                    subprocess.Popen("start whatsapp:", shell=True)
                except Exception:
                    webbrowser.open('https://web.whatsapp.com/')
            elif system == "Darwin":
                try:
                    subprocess.Popen(["open", "-a", "WhatsApp"])
                except Exception:
                    webbrowser.open('https://web.whatsapp.com/')
            else:
                webbrowser.open('https://web.whatsapp.com/')
        return True
    except Exception:
        return False

def main():
    options = {
        "okudum": ["Okudum", "okuDum", "okudum", "ben okudum"],  # Aranacak kelimeleri girin
        "okumadım": ["Okumadim", "okumadım", "okumadımm"]
    }

    start_datetime_str = "00:00 3/5/2025"  # Başlangıç tarihi ve saatini sçein
    end_datetime_str = "23:59 30/12/2026"  # Bitiş tarihi ve saati seçin

    try:
        start_datetime_str = normalize_date_format(start_datetime_str)
        end_datetime_str = normalize_date_format(end_datetime_str)
        start_datetime = datetime.datetime.strptime(start_datetime_str, "%H:%M %d/%m/%Y")
        end_datetime = datetime.datetime.strptime(end_datetime_str, "%H:%M %d/%m/%Y")
    except Exception:
        print("Tarih formatı hatalı.")
        sys.exit(1)

    if not open_whatsapp():
        print("WhatsApp açılamadı.")

    input("Mesajları kopyaladıktan sonra ENTER tuşuna basın...\n")

    try:
        chat_text = clipboard.paste()
        if not chat_text:
            input("Mesajları tekrar kopyalayıp ENTER'a basın...\n")
            chat_text = clipboard.paste()
    except Exception:
        print("Panodan veri okunamadı.")
        sys.exit(1)

    lines = chat_text.split('\n')
    user_votes = {key: [] for key in options.keys()}

    date_pattern = r'\[(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}:\d{2})\]'
    user_pattern = r'\]([^:]+):'

    for line in lines:
        if not line.strip():
            continue

        date_match = re.search(date_pattern, line)
        if not date_match:
            continue

        day, month, year = map(int, date_match.groups()[:3])
        time_str = date_match.group(4)

        user_match = re.search(user_pattern, line)
        if not user_match:
            continue

        current_user = user_match.group(1).strip()

        user_end_pos = line.find(current_user) + len(current_user)
        colon_pos = line.find(":", user_end_pos)
        if colon_pos == -1:
            continue
        message_content = line[colon_pos + 1:].strip()

        try:
            hour, minute = map(int, time_str.split(':'))
            msg_datetime = datetime.datetime(year, month, day, hour, minute)
            if start_datetime <= msg_datetime <= end_datetime:
                for option_key, option_variants in options.items():
                    for variant in option_variants:
                        if message_content.lower() == variant.lower():
                            if current_user not in user_votes[option_key]:
                                user_votes[option_key].append(current_user)
                            break
        except Exception:
            continue

    for option, users in user_votes.items():
        print(f"{option}: {', '.join(users)}" if users else f"{option}: ")

if __name__ == "__main__":
    main()
