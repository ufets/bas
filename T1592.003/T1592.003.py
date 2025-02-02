import sys
from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

def get_firmware_info(ip):
    errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(
        SnmpEngine(),
        CommunityData('public', mpModel=0),
        UdpTransportTarget((ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'))
    ))

    if errorIndication:
        print(f"Ошибка SNMP: {errorIndication}")
    elif errorStatus:
        print(f"Ошибка SNMP: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1] or '?'}")
    else:
        for varBind in varBinds:
            print(f"Информация о прошивке: {varBind}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python snmp_get.py <ip_address>")
    else:
        get_firmware_info(sys.argv[1])