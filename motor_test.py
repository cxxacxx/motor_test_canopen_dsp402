# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 15:28:37 2021

@author: cxxha
"""
from ctypes import *
import time
import numpy as np

dll = windll.LoadLibrary('./ECanVci64.dll')  # 调用dll文件
nDeviceType = 3  # 设备类型USBCAN-2E-U
nDeviceInd = 0  # 索引号0，代表设备个数
nReserved = 0  # 无意义参数
# nCANInd = 1  # can通道号


# 定义一个python的'结构体'，使用ctypes继承Structure，内容是初始化需要的参数，依据产品手册
class VciInitConfig(Structure):
    _fields_ = [("AccCode", c_ulong),  # 验收码，后面是数据类型
                ("AccMask", c_ulong),  # 屏蔽码
                ("Reserved", c_ulong),  # 保留
                ("Filter", c_ubyte),  # 滤波使能。0=不使能，1=使能使能时，/
                # 请参照SJA1000验收滤波器设置验收码和屏蔽码。
                ("Timing0", c_ubyte),  # 波特率定时器0（BTR0）
                ("Timing1", c_ubyte),  # 波特率定时器1（BTR1)
                ("Mode", c_ubyte)]  # 模式。=0为正常模式，=1为只听模式， =2为自发自收模式


# 定义发送报文的结构体
class VciCanObj(Structure):
    _fields_ = [("ID", c_uint),  # 报文帧ID'''
                ("TimeStamp", c_uint),  # 接收到信息帧时的时间标识
                ("TimeFlag", c_ubyte),  # 是否使用时间标识， 为1时TimeStamp有效
                ("SendType", c_ubyte),  # 发送帧类型。=0时为正常发送,=1时为单次发送（不自动重发)，/
                # =2时为自发自收（用于测试CAN卡是否损坏） ， =3时为单次自发自收（只发送一次， 用于自测试），/
                # 只在此帧为发送帧时有意义。
                ("RemoteFlag", c_ubyte),  # 是否是远程帧。=0时为数据帧，=1时为远程帧。
                ("ExternFlag", c_ubyte),  # 是否是扩展帧。=0时为标准帧（11位帧ID），=1时为扩展帧（29位帧ID）。
                ("DataLen", c_ubyte),  # 数据长度DLC(<=8)， 即Data的长度
                ("Data", c_ubyte * 8),  # CAN报文的数据。 空间受DataLen的约束。
                ("Reserved", c_ubyte * 3)]  # 系统保留

def open_can():
    # 定义一个用于初始化的实例对象vic
    vic = VciInitConfig()
    vic.AccCode = 0x00000000
    vic.AccMask = 0xffffffff
    vic.reserved = 0
    vic.Filter = 0
    vic.Timing0 = 0x00  # 500Kbps
    vic.Timing1 = 0x14  # 500Kbps
    vic.Mode = 0
    '''设备的打开如果是双通道的设备的话，可以再用initcan函数初始化'''
    # OpenDevice(设备类型号，设备索引号，参数无意义)
    ret = dll.OpenDevice(nDeviceType, nDeviceInd, nReserved)
    print("opendevice:", ret)
    # InitCAN(设备类型号，设备索引号，第几路CAN，初始化参数initConfig)，
    ret = dll.InitCAN(nDeviceType, nDeviceInd, 0, byref(vic))
    print("initcan0:", ret)
    # StartCAN(设备类型号，设备索引号，第几路CAN)
    ret = dll.StartCAN(nDeviceType, nDeviceInd, 0)
    print("startcan0:", ret)
    time.sleep(1)

    vco = VciCanObj()
    vco.ID = 0x601  # 帧的ID
    vco.SendType = 1  # 发送帧类型，0是正常发送，1为单次发送，这里要选1！要不发不去！
    vco.RemoteFlag = 0
    vco.ExternFlag = 0
    vco.DataLen = 8
    vco.Data = (0x40, 0x41, 0x60, 0x00, 0x00, 0x00, 0x00,0x00)
    vco.Reserved = (0, 0, 0)
    
    # 定义报文实例对象，用于接收
    vco2 = VciCanObj()
    vco2.ID = 0x00000001  # 帧的ID 后面会变成真实发送的ID
    vco2.SendType = 0  # 这里0就可以收到
    vco2.RemoteFlag = 0
    vco2.ExternFlag = 0
    vco2.DataLen = 8
    vco2.Data = (1,2,3,4,5,6,7,0)
    return [vco,vco2]

def close_can():
    ret = dll.CloseDevice(nDeviceType, nDeviceInd)
    print("closedevice:", ret)
    
def send(id,v):
    vco.ID = id;
    vco.Data = v
    art = dll.Transmit(nDeviceType, nDeviceInd, 0, byref(vco), 8)  # 发送vco
    print("发送 ID: "+hex(vco.ID)+" 数据："+''.join('{:02X} '.format(i) for i in np.array(list(vco.Data))))
    time.sleep(0.5)
    ret = dll.Receive(nDeviceType, nDeviceInd, 0, byref(vco2), 8, 200)  # 以vco2的形式接收报文
    #time.sleep(3)  # 设置一个循环发送的时间
    if ret > 0:
        print("接收 ID: "+hex(vco2.ID)+" 数据："+''.join('{:02X} '.format(i) for i in np.array(list(vco2.Data))))
    
def send_test():    
    art = dll.Transmit(nDeviceType, nDeviceInd, 0, byref(vco), 8)  # 发送vco
    print("发送 ID: "+hex(vco.ID)+" 数据："+''.join('{:02X} '.format(i) for i in np.array(list(vco.Data))))
    #ret = dll.Receive(nDeviceType, nDeviceInd, 0, byref(vco2), 8, 20)  # 以vco2的形式接收报文
    #time.sleep(3)  # 设置一个循环发送的时间
    #if ret > 0:
    #    print("接收 ID: "+hex(vco2.ID)+" 数据："+''.join('{:02X} '.format(i) for i in np.array(list(vco2.Data))))

def init_node():
    send(0x000,(0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00))
    send(0x000,(0x82, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00))
    send(0x000,(0x82, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,0x00))
    #设置同步时间
    send(0x601,(0x23, 0x05, 0x10, 0x00, 0x80, 0x00, 0x00,0x00))
    send(0x601,(0x23, 0x06, 0x10, 0x00, 0xA0, 0x0F, 0x00,0x00))
    send(0x000,(0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,0x00))
    

def set_motor(v,a,d): #最大速度，加速度，减速度
    high, mid, low = bytes(d)
    send(0x601,(0x23, 0x84, 0x60, 0x00, low, mid, high,0x00))
    high, mid, low = bytes(a)
    send(0x601,(0x23, 0x83, 0x60, 0x00, low, mid, high,0x00))
    high, mid, low = bytes(v)
    send(0x601,(0x23, 0x81, 0x60, 0x00, low, mid, high,0x00))
    
def set_interpolation_position_mode():
    #设置速度，加速度   
    set_motor(50000,50000,50000)
    #设置模式   
    send(0x601,(0x2F, 0x60, 0x60, 0x00, 0x07, 0x00, 0x00,0x00))
    #send(0x601,(0x40, 0x41, 0x60, 0x00, 0x00, 0x00, 0x00,0x00))

def set_profile_position_mode():
    #设置速度，加速度   
    set_motor(50000,50000,50000)
    #设置模式   
    send(0x601,(0x2F, 0x60, 0x60, 0x00, 0x01, 0x00, 0x00,0x00))

def set_profile_velocity_mode():
    #设置速度，加速度   
    set_motor(5000,5000,5000)
    #设置模式   
    send(0x601,(0x2F, 0x60, 0x60, 0x00, 0x03, 0x00, 0x00,0x00))
    #send(0x601,(0x40, 0x41, 0x60, 0x00, 0x00, 0x00, 0x00,0x00))
    
def set_profile_torque_mode():
    set_motor(50000,50000,50000)
    #设置模式   
    send(0x601,(0x2F, 0x60, 0x60, 0x00, 0x04, 0x00, 0x00,0x00))
    
    send(0x601,(0x22, 0x87, 0x60, 0x00, 0x88, 0x13, 0x00,0x00))
    
    high,mid,low = bytes(1500)
    send(0x601,(0x22, 0x72, 0x60, 0x00, low, mid, high,0x00))
    
def bytes(integer):
    high,tmp = divmod(integer, 0x10000)
    mid,low = divmod(tmp, 0x100)
    return high,mid,low

def enable_motor():
    #使能电机
    send(0x601,(0x2B, 0x40, 0x60, 0x00, 0x06, 0x00, 0x00,0x00))
    send(0x601,(0x40, 0x41, 0x60, 0x00, 0x00, 0x00, 0x00,0x00))
    if((np.array(list(vco2.Data))[4]==8)&(np.array(list(vco2.Data))[5]==2)):
        print("电机使能过程出现错误，建议重新上电！")
    send(0x601,(0x2B, 0x40, 0x60, 0x00, 0x07, 0x00, 0x00,0x00))
    send(0x601,(0x40, 0x41, 0x60, 0x00, 0x00, 0x00, 0x00,0x00))
    if((np.array(list(vco2.Data))[4]==8)&(np.array(list(vco2.Data))[5]==2)):
        print("电机使能过程出现错误，建议重新上电！")
    send(0x601,(0x2B, 0x40, 0x60, 0x00, 0x0f, 0x00, 0x00,0x00))
    
    send(0x601,(0x40, 0x41, 0x60, 0x00, 0x00, 0x00, 0x00,0x00))
    if((np.array(list(vco2.Data))[4]==8)&(np.array(list(vco2.Data))[5]==2)):
        print("电机使能过程出现错误，建议重新上电！")

def stop_motor():
    send(0x601,(0x2B, 0x40, 0x60, 0x00, 0x06, 0x00, 0x00,0x00))
    
def going_back_forth(p1,p2):#p1,p2两个位置间往返转动
    high1,mid1,low1 = bytes(p1)
    high2,mid2,low2 = bytes(p2)
    i = 0;
    send(0x601,(0x2B, 0x40, 0x60, 0x00, 0x1f, 0x00, 0x00,0x00))#激活插补
    while(1):
        send(0x601,(0x2B, 0xC1, 0x60, 0x01, low1, mid1, 0x00,0x00))
        send(0x601,(0x2B, 0xC1, 0x60, 0x02, high1, 0x00, 0x00,0x00))    
        time.sleep(5)
        
        send(0x601,(0x2B, 0xC1, 0x60, 0x01, low2, mid2, 0x00,0x00))
        send(0x601,(0x2B, 0xC1, 0x60, 0x02, high2, 0x00, 0x00,0x00))
        time.sleep(5)
        i = i+1
        if i == 2:
            break
    send(0x601,(0x2B, 0x40, 0x60, 0x00, 0x0f, 0x00, 0x00,0x00))

def going_to(p):#转动到p
    high,mid,low = bytes(p)
    send(0x601,(0x23, 0x7A, 0x60, 0x00, low, mid, high,0x00))
    send(0x601,(0x2B, 0x40, 0x60, 0x00, 0x1f, 0x00, 0x00,0x00))
    time.sleep(5)
    send(0x601,(0x40, 0x41, 0x60, 0x00, 0x00, 0x00, 0x00,0x00))
    #send(0x601,(0x2B, 0x40, 0x60, 0x00, 0x0f, 0x00, 0x00,0x00))
    
def set_velocity(v):
    high,mid,low = bytes(v)
    send(0x601,(0x23, 0xFF, 0x60, 0x00, low, mid, high,0x00))
    
def set_torque(t):
    high,mid,low = bytes(t)
    send(0x601,(0x22, 0x71, 0x60, 0x00, low, mid, high,0x00))
    #send(0x601,(0x2B, 0x40, 0x60, 0x00, 0x0f, 0x00, 0x00,0x00))
    
def test_interpolation_position_mode():
    set_interpolation_position_mode()
    enable_motor()
    going_back_forth(0,100000)
    stop_motor()

def test_profile_position_mode():
    set_profile_position_mode()
    enable_motor()
    going_to(100000)
    going_to(200000)
    stop_motor()

def test_profile_velocity_mode():
    set_profile_velocity_mode()
    enable_motor()
    set_velocity(20000)
    time.sleep(3)
    set_velocity(30000)
    time.sleep(3)
    set_velocity(50000)
    time.sleep(3)
    set_velocity(0)

def test_torque_mode():
    set_profile_torque_mode()
    enable_motor()
    set_torque(50)
    time.sleep(3)
    set_torque(80)
    time.sleep(3)
    set_torque(100)
    time.sleep(3)
    set_torque(120)
    set_torque(0)
    
if __name__ == "__main__":
    [vco,vco2] = open_can()
    #init_node()
    #test_interpolation_position_mode()
    
    # test_profile_position_mode()
    
    # test_profile_velocity_mode()
    test_torque_mode()

    time.sleep(1)
    stop_motor()
    
    close_can()
    