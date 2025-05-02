import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading

def run_bot(email, password, all_courses):
    try:
        service = Service(executable_path="chromedriver.exe")
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        driver.get("https://helsinki.inschool.fi/!02716814/selection/view?")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-frontdoor")))
        driver.find_element(By.ID, "login-frontdoor").send_keys(email + Keys.ENTER)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        driver.find_element(By.ID, "password").send_keys(password + Keys.ENTER)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "tray-selection-on-first-click")))
        checkbox = driver.find_element(By.ID, "tray-selection-on-first-click")
        if not checkbox.is_selected():
            checkbox.click()
        time.sleep(0.5)

        for period, course_text in all_courses.items():
            courses = [c.strip() for c in course_text.get().split(',') if c.strip()]
            if not courses:
                continue

            try:
                # Sulje avoin tarjotin ennen uuden avaamista
                try:
                    close_button = driver.find_element(By.CSS_SELECTOR, ".close-tray-button")
                    if close_button.is_displayed():
                        close_button.click()
                        time.sleep(1)
                except Exception as close_error:
                    print(f"Edellisen tarjottimen sulkeminen epäonnistui: {close_error}")

                # Avaa uusi periodi
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.LINK_TEXT, period))
                )
                driver.find_element(By.LINK_TEXT, period).click()
                time.sleep(1)

                for course in courses:
                    try:
                        # Hae elementti ja varmista, että se on näkyvissä ja klikattavissa
                        element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.LINK_TEXT, course))
                        )
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(0.2)  # Anna aikaa vieritykselle

                        # Varmista, että elementti on näkyvissä
                        if not element.is_displayed():
                            print(f"Elementti {course} ei ole näkyvissä, yritetään vierittää uudelleen.")
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                            time.sleep(0.2)

                        # Sulje mahdolliset häiritsevät elementit
                        try:
                            search_field = driver.find_element(By.ID, "search-term")
                            if search_field.is_displayed():
                                driver.execute_script("arguments[0].blur();", search_field)
                                time.sleep(0.2)
                        except Exception as e:
                            print(f"Häiritsevän elementin sulkeminen epäonnistui: {e}")

                        # Varmista, että elementti on klikattavissa
                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.LINK_TEXT, course))
                        )

                        # Yritä klikata elementtiä
                        try:
                            element.click()
                        except Exception as click_error:
                            print(f"Klikkaus epäonnistui kurssille {course}: {click_error}")
                            time.sleep(0.2)
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                            element.click()

                        print(f"Valittu: {course}")
                        time.sleep(0.2)

                    except Exception as e:
                        print(f"Kurssin {course} valinta epäonnistui: {e}")
                        driver.save_screenshot(f"{course}_error_screenshot.png")
                        # Yritä uudelleen kerran
                        try:
                            element = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.LINK_TEXT, course))
                            )
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                            element.click()
                            print(f"Uudelleenyritys onnistui: {course}")
                        except Exception as retry_error:
                            print(f"Uudelleenyritys epäonnistui kurssille {course}: {retry_error}")

            except Exception as period_error:
                print(f"{period} ei löytynyt tai ei avautunut: {period_error}")

        time.sleep(5)
        driver.quit()
        messagebox.showinfo("Valmis", "Kurssien valinta valmis!")
    except Exception as e:
        messagebox.showerror("Virhe", f"Virhe tapahtui: {e}")

def start_bot():
    email = email_entry.get()
    password = password_entry.get()
    if not email or not password:
        messagebox.showwarning("Puuttuva tieto", "Syötä sekä sähköposti että salasana.")
        return
    threading.Thread(target=run_bot, args=(email, password, course_entries), daemon=True).start()

# GUI
root = tk.Tk()
root.title("Wilma-kurssivalitsija (korjattu versio)")

tk.Label(root, text="Sähköposti:").grid(row=0, column=0, sticky="e")
email_entry = tk.Entry(root, width=40)
email_entry.grid(row=0, column=1, padx=5, pady=2)

tk.Label(root, text="Salasana:").grid(row=1, column=0, sticky="e")
password_entry = tk.Entry(root, show="*", width=40)
password_entry.grid(row=1, column=1, padx=5, pady=2)

# Kurssien syöttöalueet
periods = ["1. periodi", "2. periodi", "3. periodi", "4. periodi", "5. periodi"]
course_entries = {}

row = 2
for period in periods:
    tk.Label(root, text=f"{period} kurssit (pilkulla erotettuna):").grid(row=row, column=0, sticky="e", pady=2)
    entry = tk.Entry(root, width=60)
    entry.grid(row=row, column=1, padx=5)
    course_entries[period] = entry
    row += 1

start_button = tk.Button(root, text="Aloita kurssivalinta", command=start_bot)
start_button.grid(row=row, column=0, columnspan=2, pady=10)

root.mainloop()
