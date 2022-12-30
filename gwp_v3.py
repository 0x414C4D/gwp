import subprocess
import os
import re

def check_profile(name, os):
    
    wifi_profile = {}
    wifi_profile["ssid"] = name

    if os == 'nt':
        profile_info = subprocess.run(["netsh", "wlan", "show", "profiles", name], capture_output = True).stdout.decode()
        if not re.search("Security key           : Absent", profile_info):

            # look for the password
            profile_info_pass = subprocess.run(["netsh", "wlan", "show", "profiles", name, "key=clear"], capture_output=True).stdout.decode()
            password = re.search("Key Content            : (.*)\r", profile_info_pass)
            wifi_profile["password"] = password[1] if password else None
            
            # only return if there's data
            return wifi_profile
        
    elif os == 'posix':
        profile_info = subprocess.run(["sudo", "grep", "psk=", "/etc/NetworkManager/system-connections/" + name], capture_output=True).stdout.decode()
        if profile_info:

            # look for the password    
            password = re.search("psk=(.*)", profile_info)
            wifi_profile["password"] = password[1] if password else None

            # only return if there's data
            return wifi_profile


if os.name == 'nt':
    command_out = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output = True).stdout.decode()
    profile_names = (re.findall("All User Profile     : (.*)\r", command_out))

elif os.name == 'posix':
    command_out = subprocess.run(["ls", "/etc/NetworkManager/system-connections/"], capture_output=True).stdout.decode()
    profile_names = command_out.split("\n")

wifi_list = []
    

if len(profile_names):
    # information gathering section
    wifi_list = [check_profile(name, os.name) for name in profile_names]
    # output section with list unpacking
    print(*wifi_list, sep="\n")
    
    if os.name == 'nt':
        systeminfo = subprocess.run(["systeminfo"], capture_output=True).stdout.decode()

        # header section
        header = {}
        header["hostname"] = re.findall("Host Name:                 (.*)\r", systeminfo)[0]
        header["domain"] = re.findall("Domain:                    (.*)\r", systeminfo)[0]
        print(header)