
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Käynnistetään ChromeDriver
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.maximize_window()

# Avaa Wilma ja kirjaudu sisään
driver.get("https://helsinki.inschool.fi/!02716814/selection/view?")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-frontdoor")))
driver.find_element(By.ID, "login-frontdoor").send_keys("mika.dernov@gmail.com" + Keys.ENTER)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
driver.find_element(By.ID, "password").send_keys("Mika5200!" + Keys.ENTER)

# Odota ja klikkaa "Käytä pikavalintaa" -valintaruutua
try:
    quick_select = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "tray-selection-on-first-click"))
    )
    if not quick_select.is_selected():
        quick_select.click()
        time.sleep(0.5)
except Exception as e:
    print(f"Pikavalinta ei onnistunut: {e}")


# Periodien nimet ja niihin liittyvät kurssit
periods = {
    "1. periodi": [
        "ENA04.verkko.1", "LI02.verkko.1", "UE02.verkko.1",
        "YH03.verkko.1", "FI02.1", "FY05.1", "MAA05.1"
    ],
    "2. periodi": [
        "HI03.3", "FI01.3", "RUB104.5",
        "MAA06.3", "YH03.4", "GE01.3", "YH03.1"
    ],
    "3. periodi": [
        "ENA04.1", "LI02.1", "MAA05.3",
        "RUA04.1", "RUB104.2", "YH02.2", "ÄI05.4"
    ],
    "4. periodi": [
        "FY01.+FY02.b", "KU01.a", "MAY01.f",
        "OP01.c", "RUB101.+RUB02.d", "ÄI01.g", "ÄI01.i"
    ],
    "5. periodi": [
        "ENA10.1", "PS07.1", "HI08.1",
        "KU08.1", "MAA10.1", "ET06.1", "YH02.1"
    ]
}

# Käydään kaikki periodit läpi
for period_name, course_list in periods.items():
    try:
        # Odotetaan ja klikataan periodin linkkiä
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, period_name))
        )
        driver.find_element(By.LINK_TEXT, period_name).click()
        time.sleep(1)

        # Käydään läpi kurssit ja klikataan ne
        for course in course_list:
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, course))
                )
                element.click()
                time.sleep(0.5)
            except Exception as e:
                print(f"Kurssin {course} valinta epäonnistui: {e}")

        # Suljetaan periodin näkymä (jos sulkunappi löytyy)
        try:
            close_button = driver.find_element(By.CSS_SELECTOR, ".close-tray-button")
            close_button.click()
        except:
            pass

        time.sleep(1)
    except Exception as e:
        print(f"Periodin {period_name} avaus epäonnistui: {e}")

time.sleep(5)
driver.quit()
