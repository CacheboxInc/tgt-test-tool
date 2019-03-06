import json
import requests
import time
import sys
import os

from collections import OrderedDict
from urllib.parse import urlencode
from config import *
from StordGitBuildFio import *


def init_components():
    etcd_ips = "127.0.0.1"
    data = { "service_type": "test_server", "service_instance" : 0, "etcd_ips" : "%s" %EtcdIps}
    stord_data = { "service_type": "test_server", "service_instance" : 0, "etcd_ips" : "%s" %EtcdIps}
    tgt_data1 = { "service_type": "test_server", "service_instance" : 0, "etcd_ips" : "%s" %EtcdIps}
    tgt_data2 = { "service_type": "test_server", "service_instance" : 1, "etcd_ips" : "%s" %EtcdIps}

    # Start component for stord_svc
    r = requests.post("%s://%s/ha_svc/v1.0/component_start" %(h, StordUrl), data=json.dumps(data), headers=headers, cert=cert, verify=False)
    assert (r.status_code == 200)
    print ("Stord: start component done")

    # Start component for tgt_svc
    r = requests.post("%s://%s/ha_svc/v1.0/component_start" %(h, TgtUrl), data=json.dumps(data), headers=headers, cert=cert, verify=False)
    assert (r.status_code == 200)
    print ("TGT: start component done")

    '''
    # Add new aero cluster at StorD
    aero_data = {"aeroid": "%s" %AeroClusterID, "AeroClusterIPs":"%s" %AeroClusterIPs,"AeroClusterPort":"%s" %AeroClusterPort,"AeroClusterID":"%s" %AeroClusterID}
    r = requests.post("%s://%s/stord_svc/v1.0/new_aero/?aero-id=%s" %(h, StordUrl, AeroClusterID), data=json.dumps(aero_data), headers=headers, cert=cert, verify=False)
    assert (r.status_code == 200)
    print ("Stord: Aero added")
    '''

    # Add new stord to tgt
    stord_data = { "StordIp": StordIp, "StordPort": TgtToStordPort}
    r = requests.post("%s://%s/tgt_svc/v1.0/new_stord" % (h, TgtUrl), data=json.dumps(stord_data), headers=headers, cert=cert, verify=False)
    assert (r.status_code == 200)
    print ("TGT: new stord added")

def new_vm(VmId, TargetName):

    print ("new_vm")
    TargetID = VmId

    vm_data = { "vmid": "%s" %VmId, "TargetID": "%s" %TargetID, "TargetName": "%s" %TargetName, "AeroClusterID":"%s" %AeroClusterID, "VmUUID":"1"}
    print ("vm_data : %s" % vm_data)

    r = requests.post("%s://%s/stord_svc/v1.0/new_vm/?vm-id=%s" %(h, StordUrl, VmId), data=json.dumps(vm_data), headers=headers, cert=cert, verify=False)
    assert (r.status_code == 200)
    print ("STORD: New VM added: %s" %VmId)

    vm_data1 = {"TargetName": "%s" %TargetName}
    r = requests.post("%s://%s/tgt_svc/v1.0/target_create/?tid=%s" % (h, TgtUrl, TargetID), data=json.dumps(vm_data1), headers=headers, cert=cert, verify=False)
    assert (r.status_code == 200)
    print ("TGT: New VM added: %s" %VmId)


def create_vmdk(VmId, LunID, DevName, DevPath, VmdkID, target, createfile = "false"):
    TargetID = VmId

    vmdk_data = {"TargetID":"%s" %TargetID,"LunID":"%s" %LunID,"DevPath":"%s" %DevPath,"VmID":"%s" %VmId, "VmdkID":"%s" %VmdkID,"BlockSize":"4096","Compression":{"Enabled":"false"},"Encryption":{"Enabled":"false"},"RamCache":{"Enabled":"false","MemoryInMB":"1024"},"FileCache":{"Enabled":"false"},"SuccessHandler":{"Enabled":"false"}, "FileTarget":{"Enabled":"true", "CreateFile":"%s" %createfile, "TargetFilePath":"%s" %target, "TargetFileSize":"%s" %FileSize}}
    vmdk_data = {"TargetID":"%s" %TargetID,"LunID":"%s" %LunID,"DevPath":"%s" %DevPath,"VmID":"%s" %VmId, "VmdkID":"%s" %VmdkID,"BlockSize":"4096","Compression":{"Enabled":"false"},"Encryption":{"Enabled":"false"},"RamCache":{"Enabled":"true","MemoryInMB":"1024"},"FileCache":{"Enabled":"false", "Path":"/dev/shm/fil1.txt"},"SuccessHandler":{"Enabled":"true"}, "FileTarget":{"Enabled":"false", "CreateFile":"%s" %createfile, "TargetFilePath":"%s" %target, "TargetFileSize":"%s" %FileSize}, "VmUUID":"1", "VmdkUUID":"1"}
    #vmdk_data = {"TargetID":"%s" %TargetID,"LunID":"%s" %LunID,"DevPath":"%s" %DevPath,"VmID":"%s" %VmId, "VmdkID":"%s" %VmdkID,"BlockSize":"4096","Compression":{"Enabled":"false"},"Encryption":{"Enabled":"false"},"RamCache":{"Enabled":"true","MemoryInMB":"1024"},"FileCache":{"Enabled":"false", "Path":"/dev/shm/fil1.txt"},"SuccessHandler":{"Enabled":"true"}, "FileTarget":{"Enabled":"false", "CreateFile":"%s" %createfile, "TargetFilePath":"%s" %target, "TargetFileSize":"%s" %FileSize}, "VmUUID":"1", "VmdkUUID":"1", "ReadAhead":"false"}

    r = requests.post("%s://%s/stord_svc/v1.0/new_vmdk/?vm-id=%s&vmdk-id=%s" % (h, StordUrl, VmId, VmdkID), data=json.dumps(vmdk_data), headers=headers, cert=cert, verify=False)
    assert (r.status_code == 200)
    print ("STORD: New VMDK: %s added for VM: %s" %(VmdkID, VmId))

    data2 = {"DevName": "%s" %(DevName), "VmID":"%s" %VmId, "VmdkID":"%s" %VmdkID, "LunSize":"%s" %size_in_gb}
    r = requests.post("%s://%s/tgt_svc/v1.0/lun_create/?tid=%s&lid=%s" % (h, TgtUrl, TargetID, LunID), data=json.dumps(data2), headers=headers, cert=cert, verify=False)
    assert (r.status_code == 200)
    print ("TGT: New VMDK: %s added for VM: %s" %(VmdkID, VmId))

def truncate_disk(i, j):
    Name="iscsi-disk_%s_%s" %(i, j)
    Path="/var/hyc/%s" %(Name)
    cmd="sudo truncate --size=%sG %s" %(size_in_gb, Path)
    os.system(cmd);

    return Name, Path

def delete_vmdk(VmId, LunID, VmdkID):

    TargetID = VmId

    r = requests.post("%s://%s/tgt_svc/v1.0/lun_delete/?tid=%s&lid=%s" % (h, TgtUrl, TargetID, LunID), headers=headers, cert=cert, verify=False)
    assert (r.status_code == 200)
    print ("TGT: LUN %s deleted for VM: %s" %(LunID, TargetID))

    r = requests.post("%s://%s/stord_svc/v1.0/vmdk_delete/?vm-id=%s&vmdk-id=%s" % (h, StordUrl, VmId, VmdkID), headers=headers, cert=cert, verify=False)
    assert (r.status_code == 200)
    print ("STORD: VMDK %s deleted(vmdk_delete) for VM: %s" %(VmdkID, VmId))

def delete_vm(VmId):

    TargetID = VmId

    force_delete = 1
    r = requests.post("%s://%s/tgt_svc/v1.0/target_delete/?tid=%s&force=%s" % (h, TgtUrl, TargetID, force_delete), headers=headers, cert=cert, verify=False)
    assert (r.status_code == 200)
    print ("TGT: target %s deleted" %TargetID)

    r = requests.post("%s://%s/stord_svc/v1.0/vm_delete/?vm-id=%s" %(h, StordUrl, VmId))
    assert (r.status_code == 200)
    print ("STORD: target %s deleted" %VmId)


def deinit_components():

    data = { "service_type": "test_server", "service_instance" : 0, "etcd_ips" : "%s" %EtcdIps}
    r = requests.post("%s://%s/ha_svc/v1.0/component_stop" %(h, TgtUrl), data=json.dumps(data), headers=headers, cert=cert, verify=False)
    assert (r.status_code == 200)

    r = requests.post("%s://%s/ha_svc/v1.0/component_stop" %(h, StordUrl), data=json.dumps(data), headers=headers, cert=cert, verify=False)
    assert (r.status_code == 200)


def do_setup(vm_id, vmdk_id):

    TargetName = "%s-%s" %(TargetNameStr, vm_id)
    print ("TargetName : %s" %TargetName)
    print ("new VM")
    new_vm(vm_id, TargetName)
    DevName, DevPath = truncate_disk(vm_id, vmdk_id)
    print ("DevName : %s, DevPath : %s" % (DevName, DevPath))
    print ("create_vmdk")
    create_vmdk(vm_id, vmdk_id, DevName, DevPath, 1, FileTarget, "true")

    #print ("Sleeping for 100 seconds")
    time.sleep(10)

    print ("Discover luns sudo iscsiadm --mode discovery --type sendtargets --portal")
    cmd = "sudo iscsiadm --mode discovery --type sendtargets --portal %s" %TargetIp
    os.system(cmd);

    print ("Login sudo iscsiadm -m node --login")
    cmd = "sudo iscsiadm -m node --login"
    os.system(cmd);

    time.sleep(5)
    os.system("lsblk")

def do_cleanup():
    os.system("lsblk")

    cmd = "sudo iscsiadm -m node --logout"
    os.system(cmd);

    cmd = "sudo iscsiadm -m node -o delete"
    os.system(cmd);

    time.sleep(5)
    os.system("lsblk")

    """

    disk_no = 0
    for i in range(1, (no_of_vms + 1)):
        for j in range(1, (no_of_vmdks + 1)):
            disk_no += 1
            delete_vmdk(i, j, disk_no)
        delete_vm(i)
    """

#tgtd_args = '-f -e "http://127.0.0.1:2379" -s "tgt_svc" -v "v1.0" -p 9001 -D "127.0.0.1" -P 9876'.split()
#stord_args = '-etcd_ip="http://127.0.0.1:2379" -stord_version="v1.0" -svc_label="stord_svc" -ha_svc_port=9000 -v 1'.split()
tgtd_args = '-f -e http://127.0.0.1:2379 -s tgt_svc -v v1.0 -p 9001 -D 127.0.0.1 -P 9876'.split()
stord_args = '-etcd_ip=http://127.0.0.1:2379 -stord_version=v1.0 -svc_label=stord_svc -ha_svc_port=9000 -v 1'.split()
fio_args = '--name=random --ioengine=libaio --iodepth=32  --norandommap --group_reporting --gtod_reduce=1 --stonewall --rw=randrw --bs=16384 --direct=1 --size=102400 --numjobs=1 --rwmixread=1 --randrepeat=0 --filename=/dev/sdb --runtime=99999m --time_based=1 --size=10M'.split()

if __name__ == '__main__':
    cert = None
    if h == "https" :
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        h = "https"
        cert=('./cert/cert.pem', './cert/key.pem')

    print ("Cleanup existing crap first")
    do_cleanup()
    '''
    # build_dir_name = BuildDirName()
    build_dir_name = "build2019-02-11-10:00"
    print ("build_dir_name : %s" % build_dir_name)

    print("Building STORD")
    stord = Stord("/home/prasad/", "master", "Release", stord_args)
    stord.Clone()
    stord.Build(build_dir_name)

    print("Building TGTD")
    tgtd = Tgtd("/home/prasad/", "master", "Release", tgtd_args)
    tgtd.Clone()
    tgtd.Build(build_dir_name)
    init_done = False

    if not stord.IsRunning():
        stord.Run()

    if not tgtd.IsRunning():
        tgtd.Run()
    #print("TGTD = %d, STORD = %d ETCD = %d" % (tgtd.Pid(), stord.Pid(), etcd.Pid()))
    print("TGTD = %d, STORD = %d" % (tgtd.Pid(), stord.Pid()))
    time.sleep(6)
    '''
    cnt = 1
    vm_id = 1
    vmdk_id = 1
    DevName, DevPath = truncate_disk(vm_id, vmdk_id)
    TargetName = "%s-%s" %(TargetNameStr, vm_id)

    print ("Initiate components")
    init_components()

    print ("do setup")
    do_setup(vm_id, vmdk_id)
    print ("do setup done")

'''
    print ("running fio")
    print ("fio_args : %s" % fio_args)
    print ("running fio")
    print ("fio_args : %s" % fio_args)
    fio = Fio('/usr/bin/fio', fio_args)
    fio.Run()
    print ("Fio Started succesfully")
    while True:
        print ("Iteration %s" % cnt)
        print ("Sleeping for 60 minutes")

        time.sleep(3600)

        print ("Crashing TGT")
        tgtd.Crash()

        print ("sleeping for 90 seconds before restart")
        time.sleep(90)
        if tgtd.IsRunning():
            print ("TGT is not crashed, Still running.")
            sys.exit(1)

        print ("Starting TGTD")
        tgtd.Run()
        print ("sleeping for 10 seconds after TGTD service restart")
        time.sleep(10)
        if not tgtd.IsRunning():
            print ("TGT is not running.")
            sys.exit(1)


        print("TGTD = %d, STORD = %d" % (tgtd.Pid(), stord.Pid()))
        print ("re-exporting the luns at TGT side")
        # Start TGT
        data = { "service_type": "test_server", "service_instance" : 0, "etcd_ips" : "%s" %EtcdIps}
        r = requests.post("%s://%s/ha_svc/v1.0/component_start" %(h, TgtUrl), data=json.dumps(data), headers=headers, cert=cert, verify=False)
        assert (r.status_code == 200)
        print ("TGT: start component done")

        # Add new stord to tgt
        stord_data = { "StordIp": StordIp, "StordPort": TgtToStordPort}
        print ("stord_data : %s" % stord_data)
        r = requests.post("%s://%s/tgt_svc/v1.0/new_stord" % (h, TgtUrl), data=json.dumps(stord_data), headers=headers, cert=cert, verify=False)
        assert (r.status_code == 200)
        print ("TGT: stord added")

        vm_data1 = {"TargetName": "%s" %TargetName}
        TargetID = vm_id
        LunID = vmdk_id
        r = requests.post("%s://%s/tgt_svc/v1.0/target_create/?tid=%s" % (h, TgtUrl, TargetID), data=json.dumps(vm_data1), headers=headers, cert=cert, verify=False)
        assert (r.status_code == 200)
        print ("TGT: New target added: %s" % vm_id)

        data2 = {"DevName": "%s" %(DevName), "VmID":"%s" %vm_id, "VmdkID":"%s" %vmdk_id, "LunSize":"%s" %size_in_gb}
        r = requests.post("%s://%s/tgt_svc/v1.0/lun_create/?tid=%s&lid=%s" % (h, TgtUrl, TargetID, LunID), data=json.dumps(data2), headers=headers, cert=cert, verify=False)
        assert (r.status_code == 200)
        print ("TGT: New VMDK: %s added for VM: %s" %(vm_id, vmdk_id))

        print ("sleeping for 10 seconds")
        time.sleep(10)
        if not fio.IsRunning():
            print ("FIO crashed.")
            sys.exit(1)

        cnt = cnt + 1
'''
