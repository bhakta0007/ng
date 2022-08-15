#!/usr/bin/env python

# Author: bhakta0007@gmail.com

import os
import base64
from bs4 import BeautifulSoup
import prettytable
from selenium.webdriver import Firefox
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import time


def saveHtml(src, fname):
    fpw = open(fname, "w")
    fpw.write(src)
    fpw.close()


def dumpPfTable(source):
    soup = BeautifulSoup(source)
    td = soup.find("td", text="Service Name")
    ptable = td.find_parent("table")
    table = ptable.find("table")
    rows = table.findAll('tr')[1:]
    titles = ["id", "name", "Ext-Port", "Int-Port", "Int-Ip"]
    pt = prettytable.PrettyTable(titles)
    pt.align["Ext-Port"] = "l"
    pt.align["Int-Port"] = "l"
    pt.align["Int-Ip"] = "l"
    for row in rows:
        cols = row.findAll('td')
        id = cols[1].text
        name = cols[2].text
        extPort = cols[3].text
        intPort = cols[4].text
        intIp = cols[5].text
        pt.add_row([id, name, extPort, intPort, intIp])
    print(pt.get_string())


def addPfRule(browser):
    buttons = browser.find_elements_by_xpath(
        "//*[contains(text(), 'Add Custom Service')]")
    button = buttons[0]
    button.click()
    time.sleep(0.5)

    proceed = False
    while not proceed:
        print("\n")
        name = input("Enter Service name : ")
        extRange = input("Enter ext Port range :")
        intRange = input("Enter int Port range: ")
        ipAddress = input("Enter Local IP address: ")
        print("\nYou entered service {}, ext {} int {}, ip {}".format(
            name, extRange, intRange, ipAddress))
        x = input("Enter Y to continue, Q to exit or any other key to re-enter :")
        if x.lower() == 'y':
            proceed = True
        elif x.lower() == 'Q':
            return

    portnameInput = browser.find_element_by_name("portname")
    extrangeInput = browser.find_element_by_name("port_start")

    checkBox = browser.find_element_by_name("same_range")
    checkBox.click()

    # checkBox = browser.find_element_by_name("same_range").get_attribute("type") == "checkbox":
    intrangeInput = browser.find_element_by_name("internal_port_start")
    ip1, ip2, ip3, ip4 = ipAddress.split(".")
    ip1Input = browser.find_element_by_name("server_ip1")
    ip2Input = browser.find_element_by_name("server_ip2")
    ip3Input = browser.find_element_by_name("server_ip3")
    ip4Input = browser.find_element_by_name("server_ip4")

    portnameInput.send_keys(name)
    extrangeInput.send_keys(extRange)
    intrangeInput.send_keys(intRange)
    ip1Input.send_keys(ip1)
    ip2Input.send_keys(ip2)
    ip3Input.send_keys(ip3)
    ip4Input.send_keys(ip4)

    print("Adding service {}, ext {} int {}, ip {}".format(
        name, extRange, intRange, ipAddress))
    buttons = browser.find_elements_by_xpath("//*[contains(text(), 'Apply')]")
    button = buttons[0]
    button.click()
    time.sleep(0.5)
    if 'Failure' in browser.page_source:
        print("Rule conflict or error - please check existing rule or this rule")
        return False
    return True


def delPfRule(browser):

    proceed = False
    ruleId = None
    while not proceed:
        print("\n")
        ruleId = input("Enter Rule Id to delete: ")
        try:
            ruleId = int(ruleId)
        except Exception:
            print("Error - Enter a valid integer. You entered {}".format(ruleId))
            continue
        print("\nYou entered Rule Id {}".format(ruleId))
        x = input("Enter Y to continue, Q to exit or any other key to re-enter: ")
        if x.lower() == 'y':
            proceed = True
        elif x.lower() == 'Q':
            return

    radios = browser.find_elements_by_name("RouteSelect")
    match = [x for x in radios if int(x.get_property("value")) == ruleId]
    if not match:
        print("Error - rule id {} does not exist")
        return False
    radio = match[0]
    radio.click()

    # Now hit delete button
    buttons = browser.find_elements_by_xpath(
        "//*[contains(text(), 'Delete Service')]")
    button = buttons[0]
    button.click()
    time.sleep(0.5)
    print("Deleted rule with id {}".format(ruleId))
    print("Check once to confirm if its gone")
    return True


def pfMenu():
    url = "http://192.168.31.1/FW_forward3.htm"
    browser.get(url)
    time.sleep(0.5)
    exit = False
    while not exit:
        saveHtml(browser.page_source, "pf.html")
        dumpPfTable(browser.page_source)

        print("\n Menu")
        print(" A - Add rule")
        print(" D - Del rule")
        print(" L - List rules")
        print(" Q - exit")
        resp = input("#####> Enter choice A / D / L / Q: ")

        if resp.lower() == 'a':
            addPfRule(browser)
        elif resp.lower() == 'd':
            delPfRule(browser)
        elif resp.lower() == 'l':
            continue
        elif resp.lower() == 'q':
            exit = True
        else:
            print("Invalid choice {}".format(resp))
        if not exit:
            browser.get(url)
            time.sleep(0.5)


def dumpLanTable(source):
    soup = BeautifulSoup(source)
    td = soup.find("td", text="Device Name")
    ptable = td.find_parent("table")
    table = ptable.find("table")
    rows = table.findAll('tr')[1:]
    titles = ["id", "IP Address", "Device Name", "MAC Address"]
    pt = prettytable.PrettyTable(titles)
    pt.align["IP Address"] = "l"
    pt.align["Device Name"] = "l"
    pt.align["MAC Address"] = "l"
    for row in rows:
        cols = row.findAll('td')
        id = cols[1].text
        ip = cols[2].text
        name = cols[3].text
        mac = cols[4].text
        pt.add_row([id, ip, name, mac])
    print(pt.get_string())


def addLanPin(browser):
    url = "http://192.168.31.1/LAN_reserv_add.htm"
    browser.get(url)
    time.sleep(0.5)

    proceed = False
    while not proceed:
        print("\n")
        ip = input("Enter IPv4 address (last number only): 192.168.31.")
        mac = input("Enter Mac Address:")
        name = input("Enter device name : ")
        print("\nYou entered ip {}, mac {} name {}".format(ip, mac, name))
        x = input("Enter Y to continue, Q to exit or any other key to re-enter :")
        if x.lower() == 'y':
            proceed = True
        elif x.lower() == 'Q':
            return

    saveHtml(browser.page_source, "add.html")
    ip4Input = browser.find_element_by_name("rsv_ip4")
    macInput = browser.find_element_by_name("rsv_mac")
    nameInput = browser.find_element_by_name("dv_name")

    browser.save_screenshot("/tmp/x.png")
    ip4Input.send_keys(ip)
    macInput.send_keys(mac)
    nameInput.send_keys(name)

    browser.save_screenshot("/tmp/x.png")

    print("Adding ip {}, mac {} name {}".format(ip, mac, name))
    buttons = browser.find_elements_by_xpath("//*[contains(text(), 'Add')]")
    buttons = [x for x in buttons if '  Add' in x.text]
    button = buttons[0]
    button.click()
    time.sleep(0.5)
    try:
        alert = Alert(browser)
        try:
            _ = alert.text
        except Exception as ec:
            if 'NoSuchAlert' not in str(ec):
                print("Error adding pinning. Check your inputs..")
                try:
                    alert.dismiss()
                except Exception:
                    print("could not dismiss alert")
                    pass
                return False
    except Exception:
        # No alert
        pass
    if 'Failure' in browser.page_source:
        print("Error in input - pls provide valid inputs")
        return False
    return True


def delLanPin(browser):

    proceed = False
    ruleId = None
    while not proceed:
        print("\n")
        ruleId = input("Enter Id to delete: ")
        try:
            ruleId = int(ruleId)
        except Exception:
            print("Error - Enter a valid integer. You entered {}".format(ruleId))
            continue
        print("\nYou entered Rule Id {}".format(ruleId))
        x = input("Enter Y to continue, Q to exit or any other key to re-enter: ")
        if x.lower() == 'y':
            proceed = True
        elif x.lower() == 'Q':
            return

    ruleId -= 1
    # saveHtml(browser.page_source, "del.html")
    radios = browser.find_elements_by_name("ruleSelect")
    match = [x for x in radios if int(x.get_property("value")) == ruleId]
    if not match:
        print("Error - rule id {} does not exist")
        return False
    radio = match[0]
    radio.click()

    # Now hit delete button. Need to use WebDriverWait as this is JS code running..
    element = WebDriverWait(browser, 40).until(
        expected_conditions.element_to_be_clickable((By.NAME, 'Delete')))
    element.click()
    time.sleep(0.5)
    print("Deleted rule with id {}".format(ruleId))
    print("Check once to confirm if its gone")
    return True


def lanMenu():
    url = "http://192.168.31.1/LAN_lan.htm"
    browser.get(url)
    time.sleep(0.5)
    exit = False
    while not exit:
        saveHtml(browser.page_source, "advanced.html")
        dumpLanTable(browser.page_source)

        print("\n Menu")
        print(" A - Add pinning")
        print(" D - Del pinning")
        print(" L - List pinning")
        print(" Q - exit")
        resp = input("#####> Enter choice A / D / L / Q: ")

        if resp.lower() == 'a':
            addLanPin(browser)
        elif resp.lower() == 'd':
            delLanPin(browser)
        elif resp.lower() == 'l':
            continue
        elif resp.lower() == 'q':
            exit = True
        else:
            print("Invalid choice {}".format(resp))
        if not exit:
            browser.get(url)
            time.sleep(0.5)


def mainMenu():
    exit = False
    while not exit:
        print("\n Main Menu")
        print(" P - Port Forwarding")
        print(" D - DHCP Pinning")
        print(" Q - exit")
        resp = input("#####> Enter choice P / D / Q: ")

        if resp.lower() == 'p':
            pfMenu()
        elif resp.lower() == 'd':
            lanMenu()
        elif resp.lower() == 'q':
            exit = True
        else:
            print("Invalid choice {}".format(resp))
        if not exit:
            time.sleep(0.5)


# To run this, you need to modify couple of thigns
# 1. Setup the path to firefox (replace what I have with your path)
# 2. Replace 192.168.31.1 with ip address of your netgear router
# 3. replace password with the base64 (echo "myRouterAdminPassword" | base64). Set this in password variable

path = os.getenv("PATH", "")
os.environ["PATH"] = f"/home/utils/bin/firefox/64:{path}"       # CHANGE

print("Initializing connection to Netgear router.. pls wait (up to 30 seconds)")
opts = Options()
opts.headless = True
cap = DesiredCapabilities().FIREFOX
browser = Firefox(capabilities=cap, options=opts)
browser.get('http://192.168.31.1')          # CHANGE
time.sleep(3)
alert = Alert(browser)

password = 'bXlSb3V0ZXJBZG1pblBhc3N3b3JkCg=='               # CHANGE
p = base64.b64decode(password).decode('utf-8')
alert.send_keys(f'admin{Keys.TAB}{p}')
alert.accept()
time.sleep(0.7)
print("Connected...")

mainMenu()
