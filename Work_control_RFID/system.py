from starter import *
import paho.mqtt.client as mqtt
import time

# Default terminal ID
terminal_id = "14"
# Broker IP
broker = "localhost"

# MQTT Client
client = mqtt.Client()


def process_message(client, userdata, message):
    # Messaeg decoding
    message_decoded = (str(message.payload.decode("utf-8"))).split(".")

    # Display received message
    if message_decoded[0] != "Client connected" and message_decoded[0] != "Client disconnected":
        print(time.ctime() + ", " +
              "RFID card no." + message_decoded[0] + " has been used.")

        # Store in database
        add_use(message_decoded[0], message_decoded[1])
    else:
        print(message_decoded[0] + " : " + message_decoded[1])


def connect_to_broker():
    # Connect to broker
    client.connect(broker)
    # Send message about connection
    client.on_message = process_message
    # Start client and start listening for info
    client.loop_start()
    client.subscribe("card/id")


def disconnect_from_broker():
    # Disconnet the client
    client.loop_stop()
    client.disconnect()


def run_receiver():
    connect_to_broker()


if __name__ == "__main__":
    start(check_config())  # Check config and create database if needed
    connect_with_db()
    show_interface()
    run_receiver()  # start connection with broker
    show_interface()
    while True:  # Main program loop
        select = input()
        if select == '1':
            input_assign_card()
        elif select == '2':
            input_card()
        elif select == '3':
            input_card_used()
        elif select == '4':
            print_table()
        elif select == '5':
            input_employee()
        elif select == '6':
            input_remove_employee_from_card()
        elif select == '7':
            input_terminal()
        elif select == '8':
            make_a_raport()
        elif select == '9':
            input_remove_terminal()
        elif select == 'i':
            show_interface()
        elif select == 'q':
            exit()

    disconnect_from_broker()
    close_connection()
