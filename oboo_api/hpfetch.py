import base64
import os
import time
from datetime import date, datetime
from tempfile import gettempdir

import icalendar
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

load_dotenv()
HP_USERNAME = os.getenv("HP_USERNAME")
HP_PASSWORD = base64.b64decode(os.getenv("HP_PASSWORD")).decode()
HP_URL = os.getenv("HP_URL", "https://planning.isep.fr/etudiant")
GECKODRIVER_URL = "https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz"
TEMP_DIRECTORY = gettempdir()
GECKODRIVER_PATH = f"{TEMP_DIRECTORY}/geckodriver"
CALENDARS_DIRECTORY = f"{TEMP_DIRECTORY}/calendars"


def download_geckodriver() -> None:
    """
    Downloads the geckodriver required by Selenium from the Mozilla GitHub and stores it in the current directory.
    """
    print("[hpfetch] Downloading the Gecko driver from GitHub...")
    r = requests.get(GECKODRIVER_URL)
    with open(f"{GECKODRIVER_PATH}.tar.gz", "wb") as file:
        file.write(r.content)
    os.system(f"tar -xzvf {GECKODRIVER_PATH}.tar.gz -C {TEMP_DIRECTORY}")
    os.remove(f"{GECKODRIVER_PATH}.tar.gz")
    print("[hpfetch] Done !")


# For each room, download its calendar on HP using Selenium
def download_calendars(rooms_list: list[str]) -> None:
    """
    Downloads the calendar of each room indicated in the rooms_list parameter.

    Each calendar is placed in the CALENDARS_DIRECTORY.

    :param rooms_list: A list of strings representing the numbers of the rooms.
    """
    if len(rooms_list) == 0:
        return

    # Download the Gecko driver if it does not exist in the current directory
    if not os.path.exists(GECKODRIVER_PATH):
        download_geckodriver()

    # Create the calendars directory if it does not exist
    if not os.path.exists(CALENDARS_DIRECTORY):
        print(f"[hpfetch] Creating the {CALENDARS_DIRECTORY} directory.")
        os.mkdir(CALENDARS_DIRECTORY)

    options = Options()
    options.add_argument("--headless")
    ser = Service(GECKODRIVER_PATH)
    driver = webdriver.Firefox(options=options, service=ser)

    # Login sequence
    driver.get(HP_URL)
    time.sleep(2)
    driver.find_element(By.ID, "id_35").click()
    driver.find_element(By.ID, "id_35").send_keys(HP_USERNAME)
    driver.find_element(By.ID, "id_36").click()
    driver.find_element(By.ID, "id_36").send_keys(HP_PASSWORD)
    driver.find_element(By.ID, "id_24").click()

    time.sleep(2)
    driver.find_element(By.ID, "GInterface.Instances[0].Instances[1]_Combo7").click()
    # Let the page load
    time.sleep(1)

    download_failed = False
    for room in rooms_list:
        print(f"[hpfetch] Downloading calendar of room {room}...", end="", flush=True)
        try:
            # click on search bar
            driver.find_element(By.ID, "GInterface.Instances[1].Instances[1].bouton_Edit").click()
            # clear value
            driver.find_element(By.ID, "GInterface.Instances[1].Instances[1].bouton_Edit").clear()
            # set value to current room and valid
            driver.find_element(By.ID, "GInterface.Instances[1].Instances[1].bouton_Edit").send_keys(room)
            driver.find_element(By.ID, "GInterface.Instances[1].Instances[1].bouton_Edit").send_keys(Keys.ENTER)
            time.sleep(1)
            # click on ICAL export button
            driver.find_element(By.ID, "GInterface.Instances[0].Instances[4]_ical").click()
            time.sleep(1)
            # get link
            link_element = driver.find_element(By.CSS_SELECTOR, '[aria-label="L\'emploi du temps est récupéré tel qu\'il est et ne sera pas mis à jour automatiquement. Cliquez sur le lien ci-dessous : Exporter l\'emploi du temps au format iCal"]')
            ical_link = str(link_element.get_attribute("href"))
            r = requests.get(ical_link)
            with open(f"{CALENDARS_DIRECTORY}/{room}.ics", "wb") as file:
                file.write(r.content)
            # close ical export menu
            link_element.send_keys(Keys.ESCAPE)
        except Exception as e:
            # If a popup is blocking the view (when the room schedule has not been found for example),
            # press ESCAPE and move on to the next room
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            download_failed = True
            print(e)
            print("\t[FAILED]")
        else:
            print("\t[OK]")

    if download_failed:
        print("[hpfetch] [WARN] Some calendars could not be downloaded. Ensure that the schedules for the rooms in question are available on Hyperplanning.")

    driver.close()


def get_events_of_day(room: str, day: date) -> list[tuple[datetime, datetime, str]]:
    """
    Parses the calendar of the given room and returns the events of the given day.

    Each event is represented as a tuple of three values:

    - A datetime object representing the starting time of the event
    - A datetime object representing the end time of the event
    - A string representing the name of the event

    :param room: A string representing the number of the room.
    :param day: A date object of the day to get the events of.
    :return: A list containing the events of the given day.
    """
    filename = f"{CALENDARS_DIRECTORY}/{room}.ics"
    file = open(filename, 'r')
    calendar = icalendar.Calendar.from_ical(file.read())
    events = []

    for component in calendar.walk():
        if component.name == "VEVENT":
            summary = component.get('summary')

            start_datetime = component.get('dtstart').dt
            end_datetime = component.get('dtend').dt

            # Skip the slots that use a date instead of a datetime
            if type(start_datetime) is not datetime or type(end_datetime) is not datetime:
                continue

            start_date = start_datetime.date()
            if start_date == day:
                events.append((start_datetime, end_datetime, summary))
    return events
