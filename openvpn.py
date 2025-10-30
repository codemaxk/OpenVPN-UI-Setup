from subprocess import Popen, PIPE

vpnName = "OpenVPN"
vpnExtension = "ovpn"


def createUser(user):
    if user in listUsers():
        return

    commandsRSA = [
        "cd /etc/openvpn/server/easy-rsa/",
        f'sudo ./easyrsa --batch --days=3650 build-client-full "{user}" nopass',
    ]

    processRSA = Popen(
        "/bin/bash",
        shell=False,
        universal_newlines=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
    )
    processRSA.communicate("\n".join(commandsRSA))


def getConfig(user):
    commands = [
        "{",
        "cat /etc/openvpn/server/client-common.txt",
        'echo "<ca>"',
        "sudo cat /etc/openvpn/server/easy-rsa/pki/ca.crt",
        'echo "</ca>"',
        'echo "<cert>"',
        f'sudo sed -ne "/BEGIN CERTIFICATE/,$ p" /etc/openvpn/server/easy-rsa/pki/issued/"{user}".crt',
        'echo "</cert>"',
        'echo "<key>"',
        f'sudo cat /etc/openvpn/server/easy-rsa/pki/private/"{user}".key',
        'echo "</key>"',
        'echo "<tls-crypt>"',
        f'sudo sed -ne "/BEGIN OpenVPN Static key/,$ p" /etc/openvpn/server/tc.key',
        'echo "</tls-crypt>"',
        "}",
    ]

    process = Popen(
        "/bin/bash",
        shell=False,
        universal_newlines=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
    )
    config, err = process.communicate("\n".join(commands))

    config = config.replace(
        "cipher AES-256-CBC",
        "cipher AES-128-CBC\ntun-mtu 60000\ntun-mtu-extra 32\nmssfix 1450\nfast-io",
    )

    return config


def listUsers():
    commands = [
        'sudo tail -n +2 /etc/openvpn/server/easy-rsa/pki/index.txt | grep "^V" | cut -d "=" -f 2'
    ]
    process = Popen(
        "/bin/bash",
        shell=False,
        universal_newlines=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
    )
    users, err = process.communicate("\n".join(commands))

    return [user for user in users.split("\n") if user]


def removeUser(user):
    if user not in listUsers():
        return

    commands = [
        "cd /etc/openvpn/server/easy-rsa/",
        f'sudo ./easyrsa --batch revoke "{user}"',
        "sudo ./easyrsa --batch --days=3650 gen-crl",
        "sudo rm -f /etc/openvpn/server/crl.pem",
        "sudo cp /etc/openvpn/server/easy-rsa/pki/crl.pem /etc/openvpn/server/crl.pem",
        'chown nobody:"nogroup" /etc/openvpn/server/crl.pem',
    ]
    process = Popen(
        "/bin/bash",
        shell=False,
        universal_newlines=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
    )
    process.communicate("\n".join(commands))


def parse_log():
    log_path = '/path/to/openvpn-status.log'  # Update this path to your OpenVPN status log file
    try:
        with open(log_path, 'r') as file:
            lines = file.readlines()

        client_start = lines.index("OpenVPN CLIENT LIST\n") + 2
        client_end = lines.index("ROUTING TABLE\n") - 1
        client_info = lines[client_start:client_end]

        print("User Sessions:")
        for client in client_info:
            details = client.split(',')
            print(f"User: {details[0]}, IP: {details[1]}, Received: {details[2]}, Sent: {details[3]}, Connected Since: {details[4]}")
    except FileNotFoundError:
        print(f"Error: The file {log_path} does not exist.")
    except ValueError:
        print("Error: The necessary log markers are missing.")