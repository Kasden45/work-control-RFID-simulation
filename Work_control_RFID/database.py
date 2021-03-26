import os
import sqlite3
from datetime import datetime
from tabulate import tabulate
from tocsv import create_report
import time

######################### FOR USER TO FILL ################################
db_name = 'system_db.db'  # Database name
######################### FOR USER TO FILL ################################
connection = 0


def create_database():
    global connection
    # If db exists, it's being removed
    if os.path.exists(db_name):
        os.remove(db_name)
        print("An old database removed.")
    connection = sqlite3.connect(db_name, check_same_thread=False)

    create_tables()
    connection.commit()
    print("The new database created.")


def close_connection():
    global connection
    connection.close()


def connect_with_db():
    print("Connect")
    global connection
    connection = sqlite3.connect(db_name, check_same_thread=False)


def create_tables():
    global connection
    print("Creating tables!")
    sql = []
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    result = cursor.fetchall()
    print(result)

    sql.append("""CREATE TABLE IF NOT EXISTS employees (
        employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname varchar(255) NOT NULL,
        lastname varchar(255) NOT NULL
         )""")

    sql.append("""CREATE TABLE IF NOT EXISTS terminals (
                terminal_id int(11) NOT NULL,
                PRIMARY KEY (terminal_id)
                 )""")

    sql.append("""CREATE TABLE IF NOT EXISTS cards (
                    card_id int(50) NOT NULL,
                    employee_id int(11) NULL,
                    PRIMARY KEY (card_id),
                    FOREIGN KEY (employee_id)
                        REFERENCES employees (employee_id)
                            ON DELETE SET NULL
                            ON UPDATE CASCADE,
                    UNIQUE (employee_id)
                     )""")

    sql.append("""CREATE TABLE IF NOT EXISTS uses (
                       `use_id` INTEGER PRIMARY KEY AUTOINCREMENT,
                       `card_id` int (50) NOT NULL,
                       `terminal_id` int(11) NOT NULL,
                       `time` TIMESTAMP  NOT NULL DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME'))
                        )""")

    sql.append("""CREATE TABLE IF NOT EXISTS `work_segments` (
                           `segment_id` INTEGER PRIMARY KEY AUTOINCREMENT,
                           `card_id` int (50) NOT NULL,
                           `start_time` DATETIME  NOT NULL,
                           `finish_time` DATETIME  NOT NULL,
                           `work_time` TIME  NOT NULL,
                           FOREIGN KEY (card_id)
                               REFERENCES cards (card_id)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE 
                            )""")

    for table in sql:
        cursor.execute(table)  # Create missing tables
    connection.commit()


# ***************** FUNCTIONS ADDING DATA TO DATABASE ************************
def add_employee(firstname, lastname):
    cursor = connection.cursor()
    # Create a new record
    try:
        sql = "INSERT INTO `employees` (`firstname`, `lastname`) VALUES (?, ?)"
        cursor.execute(sql, (firstname, lastname))
        connection.commit()
        print("Employee", firstname, lastname, "added!")
    except:
        print("Wrong input!")


def add_card(card_id, employee_id=0):
    cursor = connection.cursor()
    cursor.execute("select distinct employee_id from cards")
    result = cursor.fetchall()
    for card in result:
        if (str(card[0]) == str(employee_id)):
            print("!That employee already has a card!")
            return

    cursor.execute("select card_id from cards")
    result = cursor.fetchall()
    for card in result:
        if (str(card[0]) == str(card_id)):
            print("!Someone has card with id%s already!" % (card_id))
            return

        # Create a new record
    sql = "INSERT INTO `cards` (`card_id`, `employee_id`) VALUES (?, ?)"
    try:
        if employee_id != 0:
            cursor.execute(sql, (card_id, employee_id))
        else:
            sql = "INSERT INTO `cards` (`card_id`, `employee_id`) VALUES (%s, NULL)" % (card_id)
            cursor.execute(sql)
        connection.commit()
    except:
        print("Wrong input!")


def add_terminal(terminal_id):
    cursor = connection.cursor()
    # Create a new record
    sql = "INSERT INTO terminals (terminal_id) VALUES (%s)" % (terminal_id)
    try:
        cursor.execute(sql)
    except:
        print("Wrong query!")
    connection.commit()


def add_test_use(card_id, terminal_id, test_time):  # yyyy-mm-dd hh:mm:ss

    cursor = connection.cursor()
    sql = "select count(*) from uses where card_id=%s" % (card_id)
    cursor.execute(sql)
    number = cursor.fetchall()
    print(number)

    # New record
    sql = "INSERT INTO `uses` (`card_id`, `terminal_id`, `time`) VALUES (?, ?, ?)"
    try:
        cursor.execute(sql, (card_id, terminal_id, test_time))
        connection.commit()
    except:
        print("Wrong query!")
    if number[0][0] % 2 != 0:
        sql = """SELECT * FROM (SELECT * FROM uses where card_id=%s ORDER BY time DESC LIMIT 2 ) sub ORDER BY time ASC""" % (
            card_id)
        cursor.execute(sql)
        result = cursor.fetchall()
        add_work_segment(card_id, datetime.strptime(result[0][3], '%Y-%m-%d %H:%M:%S'),
                         datetime.strptime(result[1][3], '%Y-%m-%d %H:%M:%S'), str(
                datetime.strptime(result[1][3], '%Y-%m-%d %H:%M:%S') - datetime.strptime(result[0][3],
                                                                                         '%Y-%m-%d %H:%M:%S')))  # Jako czas pracy wprowadzana jest różnica między końcem, a początkiem


def add_use(card_id, terminal_id):
    cursor = connection.cursor()
    try:
        sql = "select count(*) from uses where card_id=%s" % (card_id)
        cursor.execute(sql)
        number = cursor.fetchall()
    except:
        print("Wrong input!")
    try:
        cursor.execute("select  terminal_id from terminals")  # Sprawdzanie czy istenieje taki terminal
        result = cursor.fetchall()
    except:
        print("Wrong input!")
    is_empty = True
    for card in result:
        if (str(card[0]) == str(terminal_id)):
            is_empty = False

    if is_empty:
        print("There is no terminal with such ID!")
        return

    # Tworzenie nowego rekordu
    sql = "INSERT INTO `uses` (`card_id`, `terminal_id`) VALUES (?, ?)"
    try:
        cursor.execute(sql, (card_id, terminal_id))
        connection.commit()
    except:
        print("Wrong input!")
    # Jeżeli wcześniej była nieparzysta ilosć użyć, to teraz jest użycie parzyste,
    # więc praca się kończy i zapisujemy segment
    if number[0][0] % 2 != 0:
        sql = """SELECT * FROM (SELECT * FROM uses where card_id=%s ORDER BY time DESC LIMIT 2 ) sub ORDER BY time ASC""" % (
            card_id)
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            add_work_segment(card_id, datetime.strptime(result[0][3], '%Y-%m-%d %H:%M:%S'),
                             datetime.strptime(result[1][3], '%Y-%m-%d %H:%M:%S'), str(
                    datetime.strptime(result[1][3], '%Y-%m-%d %H:%M:%S') - datetime.strptime(result[0][3],
                                                                                             '%Y-%m-%d %H:%M:%S')))  # Jako czas pracy wprowadzana jest różnica między końcem, a początkiem
        except:
            print("Wrong input!")


def add_work_segment(card_id, start_time, finish_time, work_time):
    cursor = connection.cursor()
    # Create a new record
    sql = "INSERT INTO `work_segments` (`card_id`,`start_time`, `finish_time`,`work_time`) VALUES (?,?,?,?)"
    cursor.execute(sql, (card_id, start_time, finish_time, work_time))
    connection.commit()


# ***************** PRINTING FUNCTIONS ************************
def print_tables():
    print("Printing tables!\n")
    cursor = connection.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    result = cursor.fetchall()
    print_better_table(result, ["table_name"])


def print_employees():
    cursor = connection.cursor()
    cursor.execute("select * from employees")
    result = cursor.fetchall()
    print("Employees:")
    headers = []
    pre_headers = cursor.description
    for tuple in pre_headers:
        headers.append(tuple[0])
    print_better_table(result, headers)


def print_cards():
    print("\nCards:")
    sql = """select cards.card_id, employees.employee_id, employees.firstname, employees.lastname
    from cards left outer join employees on employees.employee_id = cards.employee_id or cards.employee_id=NULL;"""
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    headers = []
    pre_headers = cursor.description
    for tuple in pre_headers:
        headers.append(tuple[0])
    print_better_table(result, headers)


def print_terminals():
    print("\nTerminals:")
    sql = """select * from terminals;"""
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    headers = []
    pre_headers = cursor.description
    for tuple in pre_headers:
        headers.append(tuple[0])
    print_better_table(result, headers)


def print_uses():
    print("\nUses:")
    sql = """select uses.use_id, uses.card_id, employees.firstname, employees.lastname, uses.terminal_id, uses.time 
            from (uses left outer join cards on uses.card_id=cards.card_id)
            left outer join employees on cards.employee_id=employees.employee_id;"""
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    headers = []
    pre_headers = cursor.description
    for tuple in pre_headers:
        headers.append(tuple[0])
    print_better_table(result, headers)


def print_work_segments():
    print("\nWork segments:")
    sql = """select work_segments.segment_id, employees.*, work_segments.start_time,
        work_segments.finish_time, work_segments.work_time
        from (work_segments inner join cards on work_segments.card_id=cards.card_id)
        inner join employees on cards.employee_id=employees.employee_id;"""
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    headers = []
    pre_headers = cursor.description
    for tuple in pre_headers:
        headers.append(tuple[0])
    print_better_table(result, headers)


"""FUNCTION SUUPORTING TABLE PRINTING"""


def print_better_table(source_table, headers):
    print()
    if not bool(source_table):
        return
    table_of_dics = []
    for dic in source_table:
        table = []
        for key in dic:
            table.append(key)
        table_of_dics.append(table)
    print(tabulate(table_of_dics, headers=headers, tablefmt='orgtbl'))


# ***************** FUNCTIONS MODIFYING DATA ************************
def card_to_employee(card_id, new_employee_id):
    cursor = connection.cursor()
    cursor.execute("select distinct employee_id from cards")
    result = cursor.fetchall()
    for card in result:
        if str(card[0]) == str(new_employee_id):
            print("!That employee already has a card!")
            return
    cursor.execute("select card_id from cards where employee_id is not null")
    result = cursor.fetchall()
    for card in result:
        if (str(card[0]) == str(card_id)):
            print("!Someone has card with id%s already!" % (card_id))
            return
    cursor.execute("select card_id from cards where employee_id is null")
    result = cursor.fetchall()
    is_empty = False
    for card in result:
        if (str(card[0]) == str(card_id)):
            is_empty = True

    if not is_empty:
        print("There is no card with such ID!")
        return
    # Check if employee with this ID exits
    cursor.execute("select  employee_id from employees")
    result = cursor.fetchall()
    for card in result:
        if (str(card[0]) == str(new_employee_id)):
            is_empty = False

    if is_empty:
        print("There is no employee with such ID!")
        return

    sql = """update cards set employee_id = %s where card_id=%s """ % (new_employee_id, card_id)
    try:
        cursor.execute(sql)
        connection.commit()
    except:
        print("Wrong input!")


def remove_employee_from_card(card_id):
    sql = """update cards set employee_id = NULL where card_id=%s """ % (card_id)
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
    except:
        print("Wrong input!")


# ***************** FUNCTIONS INTERACTING WITH USER INPUT ************************
def input_assign_card():
    time.sleep(0.1)
    print("\nCard assignment!")
    print_cards()
    card_id = input('Card_id :')
    print_employees()
    employee_id = input('Employee_id :')
    card_to_employee(card_id, employee_id)
    print("<press 'i' to show text interface>")


def input_card_used():
    time.sleep(0.1)
    print("\nCard used!")
    print_cards()
    card_id = input('Card_id :')
    print_terminals()
    terminal_id = input('Terminal :')
    add_use(card_id, terminal_id)
    print("<press 'i' to show text interface>")


def input_card():
    time.sleep(0.1)
    print("\nCard addition!")
    print_cards()
    card_id = input('Card_id :')
    add_card(card_id)
    print("<press 'i' to show text interface>")


def input_terminal():
    time.sleep(0.1)
    print("\nAdding new terminal!")
    print_terminals()
    terminal_id = input('Terminal_id :')
    add_terminal(terminal_id)
    print("<press 'i' to show text interface>")


def input_employee():
    time.sleep(0.1)
    print("\nAdding new employee!")
    print_employees()
    firstname = input("Type first name: ")
    lastname = input("Type last name: ")
    add_employee(firstname, lastname)
    print("<press 'i' to show text interface>")


def input_remove_terminal():
    time.sleep(0.1)
    print("\nRemoving terminal!")
    print_terminals()
    id = input("Type terminal id: ")
    remove_terminal(id)
    print("<press 'i' to show text interface>")


def make_a_raport():
    time.sleep(0.1)
    chose = input("""\nIf you want a raport for one employee, enter '1'
if you want a raport for all employees, enter '2'\n""")
    if chose == '1':
        print_employees()
        first = input("Type first name: ")
        last = input("Type last name: ")
        sql = """select work_segments.card_id, cards.employee_id, employees.firstname, employees.lastname,
         work_segments.start_time, work_segments.finish_time, work_segments.work_time
         from (employees inner join cards on employees.employee_id=cards.employee_id)
         inner join work_segments on cards.card_id=work_segments.card_id 
         where employees.firstname='%s' and employees.lastname='%s';""" % (first, last)
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        if not bool(result):  # Jeżeli nie ma rekordów w tej kwerendzie, to nie twórz raportu
            print("No data!\n", "<press 'i' to show text interface>")
            return
        create_report(result, "%s_%s" % (first, last))
        print("<press 'i' to show text interface>")
    elif chose == '2':
        sql = """select work_segments.card_id, cards.employee_id, employees.firstname, employees.lastname,
                 work_segments.start_time, work_segments.finish_time, work_segments.work_time
                 from (employees inner join cards on employees.employee_id=cards.employee_id)
                 inner join work_segments on cards.card_id=work_segments.card_id;"""
        name = input("Type the name od the raport file: ")
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        if not bool(result):  # Jeżeli nie ma rekordów w tej kwerendzie, to nie twórz raportu
            print("No data!\n", "<press 'i' to show text interface>")
            return
        create_report(result, name)
        print("<press 'i' to show text interface>")


def remove_terminal(id):
    time.sleep(0.1)
    cursor = connection.cursor()
    sql = "DELETE FROM TERMINALS WHERE terminal_id=%s" % (id)
    cursor.execute(sql)
    connection.commit()


def input_remove_employee_from_card():
    time.sleep(0.1)
    print("\nRemoving card from the employee!")
    print_cards()
    print_employees()
    card_id = input('Card_id :')
    remove_employee_from_card(card_id)
    print("<press 'i' to show text interface>")


def print_table():
    time.sleep(0.1)
    select = input("\nSelect table to print:\n"
                   "1. Employees\n"
                   "2. RFID Cards\n"
                   "3. Uses\n"
                   "4. RFID Terminals\n"
                   "5. Work segments\n")
    if select == '1':
        print_employees()
    elif select == '2':
        print_cards()
    elif select == '3':
        print_uses()
    elif select == '4':
        print_terminals()
    elif select == '5':
        print_work_segments()
    print("<press 'i' to show text interface>")
