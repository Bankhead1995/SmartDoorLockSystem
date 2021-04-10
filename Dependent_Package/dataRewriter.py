import os

sudoPassword = 'lock'
addUserCmd = 'mosquitto_passwd -b passwd '
deleteUserCmd = 'mosquitto_passwd -D passwd '
serviceRestartCmd = 'systemctl restart mosquitto.service'

def server_modifyUserPassword(name, passcode):
    os.chdir('/etc/mosquitto/')
    os.system('echo %s|sudo -S %s' % (sudoPassword, deleteUserCmd+name))
    os.system('echo %s|sudo -S %s' % (sudoPassword, addUserCmd+name+' '+passcode))
    os.system('echo %s|sudo -S %s' % (sudoPassword, serviceRestartCmd))

def server_modifyUserName(name,newName,passcode):
    os.chdir('/etc/mosquitto/')
    os.system('echo %s|sudo -S %s' % (sudoPassword, deleteUserCmd+name))
    os.system('echo %s|sudo -S %s' % (sudoPassword, addUserCmd+newName+' '+passcode))
    os.system('echo %s|sudo -S %s' % (sudoPassword, serviceRestartCmd))

def server_addUser(name, passcode):
    os.chdir('/etc/mosquitto/')
    os.system('echo %s|sudo -S %s' % (sudoPassword, addUserCmd+name+' '+passcode))
    os.system('echo %s|sudo -S %s' % (sudoPassword, serviceRestartCmd))

def server_deleteUser(name):
    os.chdir('/etc/mosquitto/')
    os.system('echo %s|sudo -S %s' % (sudoPassword, deleteUserCmd+name))
    os.system('echo %s|sudo -S %s' % (sudoPassword, serviceRestartCmd))
