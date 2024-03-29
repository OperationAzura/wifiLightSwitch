from wifiLightSwitch.ota import OTAUpdater

def download_and_install_update_if_available():
    o = OTAUpdater('https://github.com/OperationAzura/wifiLightSwitch')
    o.check_for_update_to_install_during_next_reboot()
    o.download_and_install_update_if_available('DWW 2.4', 'bazinga1')

def start():
    import wifiLightSwitch.wifiLightSwitchMain as stm
    stm.run()

def boot():
    download_and_install_update_if_available()
    start()

boot()