from database import *

"""
        Function used at the beginning
"""


def start(arg):
    if not arg:
        create_database()
        print_tables()

        add_custom_employees()
        add_custom_cards()
        add_custom_terminals()
        add_custom_uses()

        print_employees()
        print_cards()
        print_terminals()
        print_uses()
        print_work_segments()
        os.system('cls' if os.name == 'nt' else 'clear')  # Clears console


# ***************** FUNCTIONS ADDING CUSTOM DATA ************************

def add_custom_terminals():
    add_terminal(15)
    add_terminal(14)
    add_terminal(16)
    add_terminal(18)
    add_terminal(17)
    add_terminal(11)
    add_terminal(12)
    add_terminal(13)
    add_terminal(19)
    add_terminal(10)


def add_custom_employees():
    add_employee("Michał", "Karbownik")
    add_employee("Jan", "Kowalski")
    add_employee("Wojciech", "Inglot")
    add_employee("Marek", "Kowalski")
    add_employee("Michał", "Kowalski")
    add_employee("Karol", "Wasilewski")
    add_employee("Marek", "Nowak")


def add_custom_cards():
    add_card(333, 1)
    add_card(111, 3)
    add_card(222, 2)
    add_card(card_id=666)
    add_card(888, 4)
    add_card(777, 6)
    add_card(444, 7)


def add_custom_uses():
    add_test_use(222, 14, "2020-03-30 07:28:24")
    add_test_use(333, 14, "2020-03-30 07:38:24")
    add_test_use(111, 14, "2020-03-30 10:25:28")
    add_test_use(222, 14, "2020-03-30 13:25:28")
    add_test_use(333, 12, "2020-03-30 19:45:00")
    add_test_use(111, 14, "2020-03-30 21:18:24")
    add_test_use(333, 14, "2020-03-31 07:48:24")
    add_test_use(111, 14, "2020-03-31 11:38:14")
    add_test_use(333, 12, "2020-03-31 14:38:58")
    add_test_use(111, 14, "2020-03-31 19:38:24")
    add_test_use(333, 12, "2020-04-01 10:22:20")
    add_test_use(333, 14, "2020-04-01 21:48:24")
    add_test_use(101, 17, "2020-04-01 22:22:23")


# ***************** FUNCTION SHOWING INTERFACE ************************
def show_interface():
    time.sleep(0.1)
    print("""\nINTERFACE
 - press '1' to assign a RFID card to a employee
 - press '2' to add new RFID card
 - press '3' to record usage of a RFID card (zamiast odczytania czujnika)
 - press '4' to print a table 
 - press '5' to add a new employee
 - press '6' to remove a RFID card from an employee
 - press '7' to add a RFID terminal
 - press '8' to create a report
 - press '9' to remove RFID terminal
 - press 'i' to show text interface
 - press 'q' to stop the system""")  # to interfejs testowy


def check_config():
    plik = open('config.txt', 'r')
    try:
        tekst = plik.read()
    finally:
        plik.close()

    if "create_database=1" in tekst:
        plik = open('config.txt', 'w')
        plik.write("create_database=0")
        return False
    elif "create_database=0" in tekst:
        return True
