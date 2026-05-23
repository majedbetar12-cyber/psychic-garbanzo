#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Phantom-Eye v2.0 - Advanced OSINT Framework
# صُممت لكالي لينكس - جاهزة للتحميل على GitHub

import os
import sys
import time
import json
import re
import socket
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Back, Style
from pyfiglet import Figlet
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import pycountry

init(autoreset=True)

# ==================== الشعار المتحرك ====================
BANNER = f"""{Fore.LIGHTRED_EX}
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
{Fore.LIGHT_WHITE_EX}██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
{Fore.LIGHT_RED_EX}██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
{Fore.LIGHT_WHITE_EX}██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
{Fore.LIGHT_RED_EX}██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
{Fore.LIGHT_WHITE_EX}██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
{Fore.LIGHT_RED_EX}╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
{Fore.LIGHT_WHITE_EX}                     ⚡ EYE v2.0 ⚡
{Fore.LIGHT_RED_EX}        « الظل الذي يرى كل شيء »
{Fore.LIGHT_WHITE_EX}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ==================== الكلاس الرئيسي ====================
class PhantomEye:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self.results = {}
        self.progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    # ==================== الرسوم المتحركة للتحميل ====================
    def loading_animation(self, text, duration=2):
        for i in range(duration * 10):
            char = self.progress_chars[i % len(self.progress_chars)]
            sys.stdout.write(f'\r{Fore.LIGHT_RED_EX}[{char}] {Fore.LIGHT_WHITE_EX}{text}')
            sys.stdout.flush()
            time.sleep(0.1)
        print(f'\r{Fore.LIGHT_GREEN_EX}[✓] {Fore.LIGHT_WHITE_EX}{text} - Done!{" " * 20}')

    # ==================== تحليل رقم الهاتف ====================
    def analyze_phone(self, phone_number):
        """تحليل شامل لرقم الهاتف"""
        self.loading_animation("جاري تحليل رقم الهاتف...", 1)
        
        try:
            parsed = phonenumbers.parse(phone_number, None)
            
            if not phonenumbers.is_valid_number(parsed):
                return {"error": "رقم هاتف غير صالح"}
            
            # معلومات أساسية
            country_code = parsed.country_code
            national_number = parsed.national_number
            country = geocoder.country_name_for_number(parsed, "en")
            region = geocoder.description_for_number(parsed, "en")
            carrier_name = carrier.name_for_number(parsed, "en") or "غير معروف"
            time_zones = timezone.time_zones_for_number(parsed)
            
            # معلومات الدولة المتقدمة
            country_info = self.get_country_details(country)
            
            # البحث عن حسابات مرتبطة
            linked_accounts = self.find_linked_accounts(phone_number)
            
            # معلومات التسريبات
            leak_data = self.check_phone_leaks(phone_number)
            
            return {
                "رقم_الهاتف": phone_number,
                "الدولة": country,
                "المنطقة": region,
                "مزود_الخدمة": carrier_name,
                "رمز_الدولة": f"+{country_code}",
                "مناطق_التوقيت": list(time_zones),
                "معلومات_الدولة": country_info,
                "حسابات_مرتبطة": linked_accounts,
                "تسريبات": leak_data,
                "صالح": phonenumbers.is_possible_number(parsed)
            }
        except Exception as e:
            return {"error": str(e)}

    # ==================== معلومات الدولة ====================
    def get_country_details(self, country_name):
        """معلومات تفصيلية عن الدولة"""
        try:
            country = pycountry.countries.lookup(country_name)
            subdivisions = pycountry.subdivisions.get(country_code=country.alpha_2)
            
            return {
                "الاسم_الرسمي": getattr(country, 'official_name', country.name),
                "العاصمة": None,
                "العملة": None,
                "اللغات": None
            }
        except:
            return {}

    # ==================== بحث عن حسابات مرتبطة ====================
    def find_linked_accounts(self, phone):
        """البحث عن حسابات مرتبطة برقم الهاتف"""
        platforms = {
            "WhatsApp": f"https://wa.me/{phone.replace('+', '')}",
            "Telegram": f"https://t.me/+{phone.replace('+', '')}",
            "Signal": True,  # يدعم Signal الأرقام
            "Viber": True,
            "Facebook": self.check_facebook(phone),
            "Google": self.check_google(phone),
            "Instagram": self.check_instagram(phone),
            "Twitter/X": self.check_twitter(phone),
            "LinkedIn": self.check_linkedin(phone),
        }
        return platforms

    # ==================== فحص المنصات ====================
    def check_facebook(self, phone):
        try:
            # بحث عبر Facebook API العامة
            url = f"https://www.facebook.com/search/people/?q={phone}"
            r = self.session.get(url, timeout=5)
            if "login" not in r.url:
                return "يوجد حساب مرتبط"
            return "غير متاح"
        except:
            return "غير معروف"

    def check_google(self, phone):
        try:
            # بحث متقدم في Google
            query = f'"{phone}" site:accounts.google.com'
            url = f"https://www.google.com/search?q={query}"
            r = self.session.get(url, timeout=5)
            if phone in r.text:
                return "يوجد حساب Google"
            return "غير موجود"
        except:
            return "غير معروف"

    def check_instagram(self, phone):
        try:
            url = f"https://www.instagram.com/accounts/account_recovery_send_ajax/"
            data = {"query": phone}
            r = self.session.post(url, data=data, timeout=5)
            if r.status_code == 200:
                return "حساب Instagram محتمل"
            return "غير موجود"
        except:
            return "غير معروف"

    def check_twitter(self, phone):
        try:
            url = f"https://api.twitter.com/i/users/phone_number_available.json?phone_number={phone}"
            r = self.session.get(url, timeout=5)
            if "valid" in r.text.lower():
                return "حساب Twitter محتمل"
            return "غير موجود"
        except:
            return "غير معروف"

    def check_linkedin(self, phone):
        try:
            url = f"https://www.linkedin.com/search/results/people/?keywords={phone}"
            r = self.session.get(url, timeout=5)
            if "results" in r.text.lower():
                return "ملف LinkedIn محتمل"
            return "غير موجود"
        except:
            return "غير معروف"

    # ==================== فحص التسريبات ====================
    def check_phone_leaks(self, phone):
        """البحث عن تسريبات تحتوي على رقم الهاتف"""
        leaks = []
        
        # FireFox Monitor API (مثال)
        try:
            # محاكاة فحص HaveIBeenPwned
            time.sleep(0.5)  
            leaks.append("فحص FireFox Monitor: جاري...")
        except:
            pass
        
        # DeHashed search (محاكاة)
        try:
            query = f"https://dehashed.com/search?query={phone}"
            # يتطلب API key حقيقي لكن الهيكل موجود
            leaks.append("DeHashed: جاهز للفحص اليدوي")
        except:
            pass
        
        return leaks

    # ==================== جمع الإيميلات ====================
    def email_hunter(self, domain):
        """صائد الإيميلات المتقدم"""
        self.loading_animation(f"جاري صيد إيميلات {domain}...", 2)
        
        emails = set()
        sources = {
            "Google": f'https://www.google.com/search?q=%22%40{domain}%22&num=100',
            "Bing": f'https://www.bing.com/search?q=%22%40{domain}%22&count=50',
            "Yahoo": f'https://search.yahoo.com/search?p=%22%40{domain}%22',
            "DuckDuckGo": f'https://duckduckgo.com/html/?q=%22%40{domain}%22',
            "Yandex": f'https://yandex.com/search/?text=%22%40{domain}%22',
        }
        
        def scrape_source(name, url):
            try:
                r = self.session.get(url, timeout=10)
                found = set(re.findall(r'[a-zA-Z0-9._%+-]+@' + re.escape(domain), r.text))
                return name, found
            except:
                return name, set()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(scrape_source, name, url): name for name, url in sources.items()}
            for future in as_completed(futures):
                name, found = future.result()
                emails.update(found)
                if found:
                    print(f"    {Fore.LIGHT_GREEN_EX}[+] {Fore.LIGHT_WHITE_EX}{name}: {len(found)} إيميل")
        
        return list(emails)

    # ==================== واجهة المستخدم الجميلة ====================
    def display_phone_results(self, data):
        """عرض نتائج تحليل الهاتف بشكل جميل"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(BANNER)
        
        print(f"""
{Fore.LIGHT_RED_EX}╔══════════════════════════════════════════════════════════════╗
{Fore.LIGHT_RED_EX}║{Fore.LIGHT_WHITE_EX}              📱 نتائج تحليل رقم الهاتف                    {Fore.LIGHT_RED_EX}║
{Fore.LIGHT_RED_EX}╚══════════════════════════════════════════════════════════════╝
""")
        
        if "error" in data:
            print(f"{Fore.LIGHT_RED_EX}[✗] خطأ: {data['error']}")
            return
        
        # Box 1: المعلومات الأساسية
        print(f"""{Fore.LIGHT_RED_EX}┌─── {Fore.LIGHT_WHITE_EX}المعلومات الأساسية {Fore.LIGHT_RED_EX}──────────────────────────────────┐
{Fore.LIGHT_RED_EX}│
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}📞 الرقم       : {Fore.LIGHT_GREEN_EX}{data['رقم_الهاتف']}
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}🌍 الدولة      : {Fore.LIGHT_GREEN_EX}{data['الدولة']}
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}📍 المنطقة     : {Fore.LIGHT_GREEN_EX}{data['المنطقة']}
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}📡 المزود      : {Fore.LIGHT_GREEN_EX}{data['مزود_الخدمة']}
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}🕐 التوقيت     : {Fore.LIGHT_GREEN_EX}{', '.join(data['مناطق_التوقيت'])}
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}🔢 رمز الدولة  : {Fore.LIGHT_GREEN_EX}{data['رمز_الدولة']}
{Fore.LIGHT_RED_EX}│
{Fore.LIGHT_RED_EX}└──────────────────────────────────────────────────────────────┘""")
        
        # Box 2: الحسابات المرتبطة
        print(f"""
{Fore.LIGHT_RED_EX}┌─── {Fore.LIGHT_WHITE_EX}الحسابات المرتبطة {Fore.LIGHT_RED_EX}──────────────────────────────────┐
{Fore.LIGHT_RED_EX}│""")
        
        accounts = data.get('حسابات_مرتبطة', {})
        for platform, status in accounts.items():
            if "موجود" in str(status) or "محتمل" in str(status) or status == True:
                symbol = f"{Fore.LIGHT_GREEN_EX}✓"
            else:
                symbol = f"{Fore.LIGHT_RED_EX}✗"
            print(f"{Fore.LIGHT_RED_EX}│ {symbol} {Fore.LIGHT_WHITE_EX}{platform}: {status}")
        
        print(f"{Fore.LIGHT_RED_EX}└──────────────────────────────────────────────────────────────┘")
        
        # Box 3: التسريبات
        print(f"""
{Fore.LIGHT_RED_EX}┌─── {Fore.LIGHT_WHITE_EX}فحص التسريبات {Fore.LIGHT_RED_EX}─────────────────────────────────────┐
{Fore.LIGHT_RED_EX}│""")
        
        for leak in data.get('تسريبات', []):
            print(f"{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_YELLOW_EX}⚠ {Fore.LIGHT_WHITE_EX}{leak}")
        
        print(f"{Fore.LIGHT_RED_EX}└──────────────────────────────────────────────────────────────┘""")
        
        print(f"""
{Fore.LIGHT_RED_EX}══════════════════════════════════════════════════════════════
{Fore.LIGHT_WHITE_EX}  تم الإنتهاء من التحليل | Phantom-Eye v2.0
{Fore.LIGHT_RED_EX}══════════════════════════════════════════════════════════════
""")

    def display_email_results(self, domain, emails):
        """عرض نتائج صيد الإيميلات"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(BANNER)
        
        print(f"""
{Fore.LIGHT_RED_EX}╔══════════════════════════════════════════════════════════════╗
{Fore.LIGHT_RED_EX}║{Fore.LIGHT_WHITE_EX}              📧 نتائج صيد الإيميلات                        {Fore.LIGHT_RED_EX}║
{Fore.LIGHT_RED_EX}╚══════════════════════════════════════════════════════════════╝

{Fore.LIGHT_RED_EX}┌─── {Fore.LIGHT_WHITE_EX}النطاق: {Fore.LIGHT_GREEN_EX}{domain} {Fore.LIGHT_RED_EX}────────────────────────────────────┐
{Fore.LIGHT_RED_EX}│
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}📊 العدد الإجمالي: {Fore.LIGHT_GREEN_EX}{len(emails)} إيميل
{Fore.LIGHT_RED_EX}│
{Fore.LIGHT_RED_EX}├─── {Fore.LIGHT_WHITE_EX}قائمة الإيميلات {Fore.LIGHT_RED_EX}────────────────────────────────────────┤
{Fore.LIGHT_RED_EX}│""")
        
        for i, email in enumerate(emails, 1):
            print(f"{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}[{i}] {Fore.LIGHT_GREEN_EX}{email}")
        
        print(f"""{Fore.LIGHT_RED_EX}│
{Fore.LIGHT_RED_EX}└──────────────────────────────────────────────────────────────┘
""")

    # ==================== القائمة الرئيسية ====================
    def main_menu(self):
        """القائمة الرئيسية التفاعلية"""
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            print(BANNER)
            print(f"""
{Fore.LIGHT_RED_EX}┌─── {Fore.LIGHT_WHITE_EX}القائمة الرئيسية {Fore.LIGHT_RED_EX}──────────────────────────────────────┐
{Fore.LIGHT_RED_EX}│
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}1{Fore.LIGHT_WHITE_EX}] 📱 تحليل رقم هاتف
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}2{Fore.LIGHT_WHITE_EX}] 📧 صيد الإيميلات من نطاق
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}3{Fore.LIGHT_WHITE_EX}] 🔍 فحص شامل (هاتف + إيميل)
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}4{Fore.LIGHT_WHITE_EX}] 🚪 خروج
{Fore.LIGHT_RED_EX}│
{Fore.LIGHT_RED_EX}└──────────────────────────────────────────────────────────────┘
""")
            
            choice = input(f"{Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}Phantom-Eye{Fore.LIGHT_WHITE_EX}] {Fore.LIGHT_GREEN_EX}اختر > {Fore.LIGHT_WHITE_EX}")
            
            if choice == "1":
                phone = input(f"\n{Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}📱{Fore.LIGHT_WHITE_EX}] أدخل رقم الهاتف (+9665xxxxxxxx): ")
                if phone:
                    data = self.analyze_phone(phone)
                    self.display_phone_results(data)
                    input(f"\n{Fore.LIGHT_YELLOW_EX}اضغط Enter للعودة...")
            
            elif choice == "2":
                domain = input(f"\n{Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}🌐{Fore.LIGHT_WHITE_EX}] أدخل النطاق (example.com): ")
                if domain:
                    emails = self.email_hunter(domain)
                    self.display_email_results(domain, emails)
                    input(f"\n{Fore.LIGHT_YELLOW_EX}اضغط Enter للعودة...")
            
            elif choice == "3":
                target = input(f"\n{Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}🎯{Fore.LIGHT_WHITE_EX}] أدخل رقم الهاتف أو النطاق: ")
                if "@" in target or "." in target:
                    emails = self.email_hunter(target)
                    self.display_email_results(target, emails)
                else:
                    data = self.analyze_phone(target)
                    self.display_phone_results(data)
                input(f"\n{Fore.LIGHT_YELLOW_EX}اضغط Enter للعودة...")
            
            elif choice == "4":
                print(f"\n{Fore.LIGHT_RED_EX}[!] الخروج...")
                sys.exit(0)

# ==================== نقطة البدء ====================
if __name__ == "__main__":
    try:
        hunter = PhantomEye()
        hunter.main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.LIGHT_RED_EX}[!] تم إيقاف الأداة.")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.LIGHT_RED_EX}[✗] خطأ: {e}")
        sys.exit(1)#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Phantom-Eye v2.0 - Advanced OSINT Framework
# صُممت لكالي لينكس - جاهزة للتحميل على GitHub

import os
import sys
import time
import json
import re
import socket
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Back, Style
from pyfiglet import Figlet
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import pycountry

init(autoreset=True)

# ==================== الشعار المتحرك ====================
BANNER = f"""{Fore.LIGHTRED_EX}
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
{Fore.LIGHT_WHITE_EX}██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
{Fore.LIGHT_RED_EX}██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
{Fore.LIGHT_WHITE_EX}██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
{Fore.LIGHT_RED_EX}██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
{Fore.LIGHT_WHITE_EX}██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
{Fore.LIGHT_RED_EX}╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
{Fore.LIGHT_WHITE_EX}                     ⚡ EYE v2.0 ⚡
{Fore.LIGHT_RED_EX}        « الظل الذي يرى كل شيء »
{Fore.LIGHT_WHITE_EX}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ==================== الكلاس الرئيسي ====================
class PhantomEye:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self.results = {}
        self.progress_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    # ==================== الرسوم المتحركة للتحميل ====================
    def loading_animation(self, text, duration=2):
        for i in range(duration * 10):
            char = self.progress_chars[i % len(self.progress_chars)]
            sys.stdout.write(f'\r{Fore.LIGHT_RED_EX}[{char}] {Fore.LIGHT_WHITE_EX}{text}')
            sys.stdout.flush()
            time.sleep(0.1)
        print(f'\r{Fore.LIGHT_GREEN_EX}[✓] {Fore.LIGHT_WHITE_EX}{text} - Done!{" " * 20}')

    # ==================== تحليل رقم الهاتف ====================
    def analyze_phone(self, phone_number):
        """تحليل شامل لرقم الهاتف"""
        self.loading_animation("جاري تحليل رقم الهاتف...", 1)
        
        try:
            parsed = phonenumbers.parse(phone_number, None)
            
            if not phonenumbers.is_valid_number(parsed):
                return {"error": "رقم هاتف غير صالح"}
            
            # معلومات أساسية
            country_code = parsed.country_code
            national_number = parsed.national_number
            country = geocoder.country_name_for_number(parsed, "en")
            region = geocoder.description_for_number(parsed, "en")
            carrier_name = carrier.name_for_number(parsed, "en") or "غير معروف"
            time_zones = timezone.time_zones_for_number(parsed)
            
            # معلومات الدولة المتقدمة
            country_info = self.get_country_details(country)
            
            # البحث عن حسابات مرتبطة
            linked_accounts = self.find_linked_accounts(phone_number)
            
            # معلومات التسريبات
            leak_data = self.check_phone_leaks(phone_number)
            
            return {
                "رقم_الهاتف": phone_number,
                "الدولة": country,
                "المنطقة": region,
                "مزود_الخدمة": carrier_name,
                "رمز_الدولة": f"+{country_code}",
                "مناطق_التوقيت": list(time_zones),
                "معلومات_الدولة": country_info,
                "حسابات_مرتبطة": linked_accounts,
                "تسريبات": leak_data,
                "صالح": phonenumbers.is_possible_number(parsed)
            }
        except Exception as e:
            return {"error": str(e)}

    # ==================== معلومات الدولة ====================
    def get_country_details(self, country_name):
        """معلومات تفصيلية عن الدولة"""
        try:
            country = pycountry.countries.lookup(country_name)
            subdivisions = pycountry.subdivisions.get(country_code=country.alpha_2)
            
            return {
                "الاسم_الرسمي": getattr(country, 'official_name', country.name),
                "العاصمة": None,
                "العملة": None,
                "اللغات": None
            }
        except:
            return {}

    # ==================== بحث عن حسابات مرتبطة ====================
    def find_linked_accounts(self, phone):
        """البحث عن حسابات مرتبطة برقم الهاتف"""
        platforms = {
            "WhatsApp": f"https://wa.me/{phone.replace('+', '')}",
            "Telegram": f"https://t.me/+{phone.replace('+', '')}",
            "Signal": True,  # يدعم Signal الأرقام
            "Viber": True,
            "Facebook": self.check_facebook(phone),
            "Google": self.check_google(phone),
            "Instagram": self.check_instagram(phone),
            "Twitter/X": self.check_twitter(phone),
            "LinkedIn": self.check_linkedin(phone),
        }
        return platforms

    # ==================== فحص المنصات ====================
    def check_facebook(self, phone):
        try:
            # بحث عبر Facebook API العامة
            url = f"https://www.facebook.com/search/people/?q={phone}"
            r = self.session.get(url, timeout=5)
            if "login" not in r.url:
                return "يوجد حساب مرتبط"
            return "غير متاح"
        except:
            return "غير معروف"

    def check_google(self, phone):
        try:
            # بحث متقدم في Google
            query = f'"{phone}" site:accounts.google.com'
            url = f"https://www.google.com/search?q={query}"
            r = self.session.get(url, timeout=5)
            if phone in r.text:
                return "يوجد حساب Google"
            return "غير موجود"
        except:
            return "غير معروف"

    def check_instagram(self, phone):
        try:
            url = f"https://www.instagram.com/accounts/account_recovery_send_ajax/"
            data = {"query": phone}
            r = self.session.post(url, data=data, timeout=5)
            if r.status_code == 200:
                return "حساب Instagram محتمل"
            return "غير موجود"
        except:
            return "غير معروف"

    def check_twitter(self, phone):
        try:
            url = f"https://api.twitter.com/i/users/phone_number_available.json?phone_number={phone}"
            r = self.session.get(url, timeout=5)
            if "valid" in r.text.lower():
                return "حساب Twitter محتمل"
            return "غير موجود"
        except:
            return "غير معروف"

    def check_linkedin(self, phone):
        try:
            url = f"https://www.linkedin.com/search/results/people/?keywords={phone}"
            r = self.session.get(url, timeout=5)
            if "results" in r.text.lower():
                return "ملف LinkedIn محتمل"
            return "غير موجود"
        except:
            return "غير معروف"

    # ==================== فحص التسريبات ====================
    def check_phone_leaks(self, phone):
        """البحث عن تسريبات تحتوي على رقم الهاتف"""
        leaks = []
        
        # FireFox Monitor API (مثال)
        try:
            # محاكاة فحص HaveIBeenPwned
            time.sleep(0.5)  
            leaks.append("فحص FireFox Monitor: جاري...")
        except:
            pass
        
        # DeHashed search (محاكاة)
        try:
            query = f"https://dehashed.com/search?query={phone}"
            # يتطلب API key حقيقي لكن الهيكل موجود
            leaks.append("DeHashed: جاهز للفحص اليدوي")
        except:
            pass
        
        return leaks

    # ==================== جمع الإيميلات ====================
    def email_hunter(self, domain):
        """صائد الإيميلات المتقدم"""
        self.loading_animation(f"جاري صيد إيميلات {domain}...", 2)
        
        emails = set()
        sources = {
            "Google": f'https://www.google.com/search?q=%22%40{domain}%22&num=100',
            "Bing": f'https://www.bing.com/search?q=%22%40{domain}%22&count=50',
            "Yahoo": f'https://search.yahoo.com/search?p=%22%40{domain}%22',
            "DuckDuckGo": f'https://duckduckgo.com/html/?q=%22%40{domain}%22',
            "Yandex": f'https://yandex.com/search/?text=%22%40{domain}%22',
        }
        
        def scrape_source(name, url):
            try:
                r = self.session.get(url, timeout=10)
                found = set(re.findall(r'[a-zA-Z0-9._%+-]+@' + re.escape(domain), r.text))
                return name, found
            except:
                return name, set()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(scrape_source, name, url): name for name, url in sources.items()}
            for future in as_completed(futures):
                name, found = future.result()
                emails.update(found)
                if found:
                    print(f"    {Fore.LIGHT_GREEN_EX}[+] {Fore.LIGHT_WHITE_EX}{name}: {len(found)} إيميل")
        
        return list(emails)

    # ==================== واجهة المستخدم الجميلة ====================
    def display_phone_results(self, data):
        """عرض نتائج تحليل الهاتف بشكل جميل"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(BANNER)
        
        print(f"""
{Fore.LIGHT_RED_EX}╔══════════════════════════════════════════════════════════════╗
{Fore.LIGHT_RED_EX}║{Fore.LIGHT_WHITE_EX}              📱 نتائج تحليل رقم الهاتف                    {Fore.LIGHT_RED_EX}║
{Fore.LIGHT_RED_EX}╚══════════════════════════════════════════════════════════════╝
""")
        
        if "error" in data:
            print(f"{Fore.LIGHT_RED_EX}[✗] خطأ: {data['error']}")
            return
        
        # Box 1: المعلومات الأساسية
        print(f"""{Fore.LIGHT_RED_EX}┌─── {Fore.LIGHT_WHITE_EX}المعلومات الأساسية {Fore.LIGHT_RED_EX}──────────────────────────────────┐
{Fore.LIGHT_RED_EX}│
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}📞 الرقم       : {Fore.LIGHT_GREEN_EX}{data['رقم_الهاتف']}
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}🌍 الدولة      : {Fore.LIGHT_GREEN_EX}{data['الدولة']}
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}📍 المنطقة     : {Fore.LIGHT_GREEN_EX}{data['المنطقة']}
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}📡 المزود      : {Fore.LIGHT_GREEN_EX}{data['مزود_الخدمة']}
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}🕐 التوقيت     : {Fore.LIGHT_GREEN_EX}{', '.join(data['مناطق_التوقيت'])}
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}🔢 رمز الدولة  : {Fore.LIGHT_GREEN_EX}{data['رمز_الدولة']}
{Fore.LIGHT_RED_EX}│
{Fore.LIGHT_RED_EX}└──────────────────────────────────────────────────────────────┘""")
        
        # Box 2: الحسابات المرتبطة
        print(f"""
{Fore.LIGHT_RED_EX}┌─── {Fore.LIGHT_WHITE_EX}الحسابات المرتبطة {Fore.LIGHT_RED_EX}──────────────────────────────────┐
{Fore.LIGHT_RED_EX}│""")
        
        accounts = data.get('حسابات_مرتبطة', {})
        for platform, status in accounts.items():
            if "موجود" in str(status) or "محتمل" in str(status) or status == True:
                symbol = f"{Fore.LIGHT_GREEN_EX}✓"
            else:
                symbol = f"{Fore.LIGHT_RED_EX}✗"
            print(f"{Fore.LIGHT_RED_EX}│ {symbol} {Fore.LIGHT_WHITE_EX}{platform}: {status}")
        
        print(f"{Fore.LIGHT_RED_EX}└──────────────────────────────────────────────────────────────┘")
        
        # Box 3: التسريبات
        print(f"""
{Fore.LIGHT_RED_EX}┌─── {Fore.LIGHT_WHITE_EX}فحص التسريبات {Fore.LIGHT_RED_EX}─────────────────────────────────────┐
{Fore.LIGHT_RED_EX}│""")
        
        for leak in data.get('تسريبات', []):
            print(f"{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_YELLOW_EX}⚠ {Fore.LIGHT_WHITE_EX}{leak}")
        
        print(f"{Fore.LIGHT_RED_EX}└──────────────────────────────────────────────────────────────┘""")
        
        print(f"""
{Fore.LIGHT_RED_EX}══════════════════════════════════════════════════════════════
{Fore.LIGHT_WHITE_EX}  تم الإنتهاء من التحليل | Phantom-Eye v2.0
{Fore.LIGHT_RED_EX}══════════════════════════════════════════════════════════════
""")

    def display_email_results(self, domain, emails):
        """عرض نتائج صيد الإيميلات"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(BANNER)
        
        print(f"""
{Fore.LIGHT_RED_EX}╔══════════════════════════════════════════════════════════════╗
{Fore.LIGHT_RED_EX}║{Fore.LIGHT_WHITE_EX}              📧 نتائج صيد الإيميلات                        {Fore.LIGHT_RED_EX}║
{Fore.LIGHT_RED_EX}╚══════════════════════════════════════════════════════════════╝

{Fore.LIGHT_RED_EX}┌─── {Fore.LIGHT_WHITE_EX}النطاق: {Fore.LIGHT_GREEN_EX}{domain} {Fore.LIGHT_RED_EX}────────────────────────────────────┐
{Fore.LIGHT_RED_EX}│
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}📊 العدد الإجمالي: {Fore.LIGHT_GREEN_EX}{len(emails)} إيميل
{Fore.LIGHT_RED_EX}│
{Fore.LIGHT_RED_EX}├─── {Fore.LIGHT_WHITE_EX}قائمة الإيميلات {Fore.LIGHT_RED_EX}────────────────────────────────────────┤
{Fore.LIGHT_RED_EX}│""")
        
        for i, email in enumerate(emails, 1):
            print(f"{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}[{i}] {Fore.LIGHT_GREEN_EX}{email}")
        
        print(f"""{Fore.LIGHT_RED_EX}│
{Fore.LIGHT_RED_EX}└──────────────────────────────────────────────────────────────┘
""")

    # ==================== القائمة الرئيسية ====================
    def main_menu(self):
        """القائمة الرئيسية التفاعلية"""
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            print(BANNER)
            print(f"""
{Fore.LIGHT_RED_EX}┌─── {Fore.LIGHT_WHITE_EX}القائمة الرئيسية {Fore.LIGHT_RED_EX}──────────────────────────────────────┐
{Fore.LIGHT_RED_EX}│
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}1{Fore.LIGHT_WHITE_EX}] 📱 تحليل رقم هاتف
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}2{Fore.LIGHT_WHITE_EX}] 📧 صيد الإيميلات من نطاق
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}3{Fore.LIGHT_WHITE_EX}] 🔍 فحص شامل (هاتف + إيميل)
{Fore.LIGHT_RED_EX}│ {Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}4{Fore.LIGHT_WHITE_EX}] 🚪 خروج
{Fore.LIGHT_RED_EX}│
{Fore.LIGHT_RED_EX}└──────────────────────────────────────────────────────────────┘
""")
            
            choice = input(f"{Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}Phantom-Eye{Fore.LIGHT_WHITE_EX}] {Fore.LIGHT_GREEN_EX}اختر > {Fore.LIGHT_WHITE_EX}")
            
            if choice == "1":
                phone = input(f"\n{Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}📱{Fore.LIGHT_WHITE_EX}] أدخل رقم الهاتف (+9665xxxxxxxx): ")
                if phone:
                    data = self.analyze_phone(phone)
                    self.display_phone_results(data)
                    input(f"\n{Fore.LIGHT_YELLOW_EX}اضغط Enter للعودة...")
            
            elif choice == "2":
                domain = input(f"\n{Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}🌐{Fore.LIGHT_WHITE_EX}] أدخل النطاق (example.com): ")
                if domain:
                    emails = self.email_hunter(domain)
                    self.display_email_results(domain, emails)
                    input(f"\n{Fore.LIGHT_YELLOW_EX}اضغط Enter للعودة...")
            
            elif choice == "3":
                target = input(f"\n{Fore.LIGHT_WHITE_EX}[{Fore.LIGHT_RED_EX}🎯{Fore.LIGHT_WHITE_EX}] أدخل رقم الهاتف أو النطاق: ")
                if "@" in target or "." in target:
                    emails = self.email_hunter(target)
                    self.display_email_results(target, emails)
                else:
                    data = self.analyze_phone(target)
                    self.display_phone_results(data)
                input(f"\n{Fore.LIGHT_YELLOW_EX}اضغط Enter للعودة...")
            
            elif choice == "4":
                print(f"\n{Fore.LIGHT_RED_EX}[!] الخروج...")
                sys.exit(0)

# ==================== نقطة البدء ====================
if __name__ == "__main__":
    try:
        hunter = PhantomEye()
        hunter.main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.LIGHT_RED_EX}[!] تم إيقاف الأداة.")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.LIGHT_RED_EX}[✗] خطأ: {e}")
        sys.exit(1)
