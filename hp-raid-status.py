#!/usr/bin/env python3

""" get status of HP raid massive, need to install hpacucli """


import subprocess
import re


outdir = '/etc/zabbix/raid_massive_stat/' # output dir (don't forget to place / at the end)


""" Get status of RAID controller. Send Ok if OK and BAD if fail """
def getraidstatus():
    direct_output = subprocess.check_output('/usr/sbin/hpacucli ctrl all show status | grep Controller', shell=True)
    if direct_output[22:-1].decode("utf-8") != 'OK':
        res = 'BAD'
    else:
        res = 'OK'
    file = None
    try:
        file = open(outdir + 'raid_status', 'w')
    except IOError:
        msg = ("Unable to create file on disk.")
        file.close()
        return False
    finally:
        if file != None:
            file.write(str(res))
            file.close()
        return True


""" get status of cache on RAID controller. Send Ok if OK and BAD if fail """
def cachestatus():
    direct_output = subprocess.check_output('/usr/sbin/hpacucli ctrl all show status | grep Cache', shell=True)
    if direct_output[17:-1].decode("utf-8") != 'OK':
        res = 'BAD'
    else:
        res = 'OK'
    file = None
    try:
        file = open(outdir + 'raid_cache_status', 'w')
    except IOError:
        msg = ("Unable to create file on disk.")
        file.close()
        return False
    finally:
        if file != None:
            file.write(str(res))
            file.close()
        return True


""" get raid slots """
def getraidslot():
    direct_output = subprocess.check_output('/usr/sbin/hpacucli ctrl all show detail | grep Slot:', shell=True)
    slot = (direct_output.decode("utf-8").split('\n')[0][-1:])
    return slot.strip()


""" get list of logical drives (return list of logical drives) """
def getlds():
    slot = getraidslot()
    direct_output = subprocess.check_output('/usr/sbin/hpacucli ctrl slot=' + slot + ' ld all show status', shell=True)
    lds = (direct_output.decode("utf-8").split('\n'))
    for item in lds:
        if len(item) <1:
            lds.remove(item)
    lds.remove('')
    ldrives = []
    for ld in lds:
        ldrives.append (re.findall(r'logicaldrive(.*?)\(', ld, re.DOTALL)[0].strip())
    return ldrives

""" get list of physical drives (return list of physical drives) """
def getphs():
    slot = getraidslot()
    direct_output = subprocess.check_output('/usr/sbin/hpacucli ctrl slot=' + slot + ' pd all show detail | grep physicaldrive', shell=True)
    pds = (direct_output.decode("utf-8").split('\n'))
    pds.remove('')
    phsdrive = []
    for x in pds:
        phsdrive.append(x.split()[1])
    return phsdrive


""" get state of physical drives """
def getphsstate():
    phs = getphs()
    slot = getraidslot()
    pds = []
    for x in slot:
        for ph in phs:
            direct_output = subprocess.check_output('/usr/sbin/hpacucli ctrl slot='+x+' pd '+ph+' show | grep Status', shell=True)
            pdstate = (direct_output.decode("utf-8").split('\n'))
            pdstate.remove('')
            pds.append(pdstate[0])
            #print(ph[5:] + ' '+pdstate[0][-2:])
            file = None
            try:
                file = open(outdir + 'raid_physicaldrive_state_' + str(ph[5:]), 'w')
            except IOError:
                msg = ("Unable to create file on disk.")
                file.close()
                return False
            finally:
                if file != None:
                    file.write(pdstate[0][-2:])
                    file.close()
    return True



""" get status of logical drives """
def getldstatus():
    lds = getlds()
    slot = getraidslot()
    ldout = []
    for sl in slot:
        for ld in lds:
            direct_output = subprocess.check_output('/usr/sbin/hpacucli ctrl slot='+sl+' ld '+ ld +' show status', shell=True)
            ldsin = (direct_output.decode("utf-8").split('\n'))
            for ldstate in ldsin:
                if len(ldstate) <1:
                    ldsin.remove(ldstate)
            ldsin.remove('')
            ldout.append(ldsin[0][-2:])
        for x in lds:
            file = None
            try:
                file = open(outdir + 'raid_logicaldrive_state_'+x, 'w')
            except IOError:
                msg = ("Unable to create file on disk.")
                file.close()
                return
            finally:
                if file != None:
                    file.write(ldout[int(x)-1])
                    file.close()



""" get temperature of physical drives """
def getphtemperature():
    phs = getphs()
    slot = getraidslot()
    for x in slot:
        for ph in phs:
            try:
                direct_output = subprocess.check_output('/usr/sbin/hpacucli ctrl slot='+ x +' pd '+ ph +' show | grep Current', shell=True)
                temp = (re.sub("\D", "", direct_output.decode("utf-8")))
            except subprocess.CalledProcessError as e: # some hard drives don't giving current temperature
                temp = '0'
            file = None
            try:
                file = open(outdir + 'raid_physicaldrive_temperature_' + ph[5:], 'w')
            except IOError:
                msg = ("Unable to create file on disk.")
                file.close()
                return False
            finally:
                if file != None:
                    file.write(temp)
                    file.close()
    return True





if __name__ == "__main__":
    """ Check RAID status """
    getraidstatus()
    """ Check RAID cache status"""
    cachestatus()
    """ Check logical drives status"""
    getldstatus()
    """ Check physical drives state"""
    getphsstate()
    """ Check temperature of physical drives """
    getphtemperature()

