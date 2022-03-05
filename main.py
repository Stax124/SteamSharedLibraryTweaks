import subprocess
import ctypes
import os
import sys
import logging
import coloredlogs

firewallRuleName = "SteamLibraryLock"


def isRunningElevated():
    logging.debug("Checking if we are running as admin")

    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    logging.debug("Is admin: %s" % is_admin)
    return is_admin


class SteamRules():
    def __init__(self) -> None:
        self.disableSteamIn = 'netsh advfirewall firewall set rule name="Steam" dir=in new enable=no'
        self.enableSteamIn = 'netsh advfirewall firewall set rule name="Steam" dir=in new enable=yes'

    def disableSteamRules(self):
        returnCode1 = subprocess.call(self.disableSteamIn.split())
        logging.debug(
            f"disableSteamRules returned code: {returnCode1}")

    def enableSteamRules(self):
        returnCode1 = subprocess.call(self.enableSteamIn.split())
        logging.debug(
            f"enableSteamRules returned code: {returnCode1}")


class CustomRules():
    def __init__(self) -> None:
        self.addBlockingCommandOut = 'netsh advfirewall firewall add rule name="{firewallRuleName}" dir=out action=block program="C:\Program Files (x86)\Steam\Steam.exe" enable=yes'.format(
            firewallRuleName=firewallRuleName)
        self.addBlockingCommandIn = 'netsh advfirewall firewall add rule name="{firewallRuleName}" dir=in action=block program="C:\Program Files (x86)\Steam\Steam.exe" enable=yes'.format(
            firewallRuleName=firewallRuleName)

        self.disableCustomIn = 'netsh advfirewall firewall set rule name="{firewallRuleName}" dir=in new enable=no'.format(
            firewallRuleName=firewallRuleName)
        self.disableCustomOut = 'netsh advfirewall firewall set rule name="{firewallRuleName}" dir=out new enable=no'.format(
            firewallRuleName=firewallRuleName)

        self.enableCustomIn = 'netsh advfirewall firewall set rule name="{firewallRuleName}" dir=in new enable=yes'.format(
            firewallRuleName=firewallRuleName)
        self.enableCustomOut = 'netsh advfirewall firewall set rule name="{firewallRuleName}" dir=out new enable=yes'.format(
            firewallRuleName=firewallRuleName)

    def isCustomRuleAlreadyCreated(self):
        logging.debug("Checking if custom rule is already created")

        try:
            stdout = subprocess.check_output(['netsh', 'advfirewall', 'firewall', 'show',
                                              'rule', 'name="{firewallRuleName}"'.format(firewallRuleName=firewallRuleName)]).decode("utf-8")
            logging.debug("Custom rule found")
            return True
        except subprocess.CalledProcessError as e:
            if e.output.decode("utf-8").strip() == "No rules match the specified criteria.":
                logging.debug("Custom rule not found")
                return False
            else:
                logging.debug("Error checking custom rule, raising error: %s" %
                              e.output.decode("utf-8").strip())
                raise e.output.decode("utf-8").strip()

    def addCustomRules(self):
        returnCode1 = subprocess.call(self.addBlockingCommandIn.split())
        returnCode2 = subprocess.call(self.addBlockingCommandOut.split())
        logging.debug(
            f"addCustomRules returned codes: {returnCode1}, {returnCode2}")

    def enableCustomRules(self):
        returnCode1 = subprocess.call(self.enableCustomIn.split())
        returnCode2 = subprocess.call(self.enableCustomOut.split())
        logging.debug(
            f"enableCustomRules returned codes: {returnCode1}, {returnCode2}")

    def disableCustomRules(self):
        returnCode1 = subprocess.call(self.disableCustomIn.split())
        returnCode2 = subprocess.call(self.disableCustomOut.split())
        logging.debug(
            f"disableCustomRules returned codes: {returnCode1}, {returnCode2}")


steamRules = SteamRules()
customRules = CustomRules()


def enable():
    logging.debug("Enabling Steam Blocking")

    if customRules.isCustomRuleAlreadyCreated():
        logging.debug(
            "Custom rule already exists, disabling default steam rules now")
        steamRules.disableSteamRules()
        logging.debug("Enabling custom rules")
        customRules.enableCustomRules()
    else:
        logging.debug("Custom rule not found, adding now")
        customRules.addCustomRules()
        logging.debug("Disabling default steam rules")
        steamRules.disableSteamRules()


def disable():
    logging.debug("Disabling Steam Blocking")

    logging.debug("Enabling default steam rules")
    steamRules.enableSteamRules()
    logging.debug("Disabling custom rules")
    customRules.disableCustomRules()


def main():
    if not isRunningElevated():
        logging.error("This script requires admin privileges.")
        sys.exit(1)

    confirm = True if input(
        "WARNING: This script will modify your firewall rules. Continue? [y/n] ").strip().lower() == "y" else False

    if not confirm:
        logging.warning("Aborting.")
        sys.exit(0)

    enable()

    logging.info("Press a key to disable Steam blocking")
    os.system("pause")

    disable()


if __name__ == "__main__":
    coloredlogs.install(level='DEBUG', datefmt='%H:%M:%S',
                        fmt='%(asctime)s %(levelname)s %(message)s')
    main()
