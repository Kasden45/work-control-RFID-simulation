#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import tkinter

# Default terminal ID
terminal_id = "14"
# Broker IP
broker = "localhost"

# MQTT Client
client = mqtt.Client()
# Main window with buttons simulationg the use of RFID card
window = tkinter.Tk()

def call_worker(card_id):
    client.publish("card/id", card_id + "." + terminal_id,)


def create_main_window():
    window.geometry("300x200")
    title = "Terminal no.%s" % (terminal_id)
    window.title(title)

    intro_label = tkinter.Label(window, text="Select card to use:")
    intro_label.grid(row=0, columnspan=5)

    button_1 = tkinter.Button(window, text="Card 111",
                              command=lambda: call_worker("111"))
    button_1.grid(row=1, column=0)
    button_2 = tkinter.Button(window, text="Card 222",
                              command=lambda: call_worker("222"))
    button_2.grid(row=2, column=0)
    button_3 = tkinter.Button(window, text="Card 333",
                              command=lambda: call_worker("333"))
    button_3.grid(row=3, column=0)
    button_4 = tkinter.Button(window, text="Card 444",
                              command=lambda: call_worker("444"))
    button_4.grid(row=1, column=1)
    button_5 = tkinter.Button(window, text="Card 777",
                              command=lambda: call_worker("777"))
    button_5.grid(row=2, column=1)
    button_6 = tkinter.Button(window, text="Card 888",
                              command=lambda: call_worker("888"))
    button_6.grid(row=3, column=1)
    button_stop = tkinter.Button(window, text="Stop", command=window.quit)
    button_stop.grid(row=4, columnspan=2)


def connect_to_broker():
    # Connect to the broker.
    client.connect(broker)
    # Send message about conenction.
    call_worker("Client connected")


def disconnect_from_broker():
    # Send message about disconenction.
    call_worker("Client disconnected")
    # Disconnet the client.
    client.disconnect()


def run_sender():
    connect_to_broker()
    create_main_window()

    # Start to display window (It will stay here until window is displayed)
    window.mainloop()

    disconnect_from_broker()


if __name__ == "__main__":
    terminal_id = input("Enter RFID terminal's ID: ")
    run_sender()
