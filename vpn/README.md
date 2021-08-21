# VPN

IP를 기준으로 스트리밍 되는 camera를 장소에 관계없이 사용하기 위하여 VPN을 구축한후 해당 네트워크에 연결시킵니다.



VPN 공식사이트 : https://www.pivpn.io/

VPN 설치 설명1 : https://iotmaker.kr/iotbook-vpn/

VPN 설치 설명2 : https://blog.lkaybob.pe.kr/post/tech/pi-home-vpn/

VPN 설치 설명3 : https://ziwon.github.io/post/wireguard/

wireguard Allowed IPs : https://blog.stackframe.dev/8

https://slowbootkernelhacks.blogspot.com/2020/09/wireguard-vpn.html



## VPN Sepc

IP : 211.179.42.130 (VPN Network : 10.6.0.1)

PORT : 51820 (UDP)

VPN Type : openVPN

DNS 제공자 : 구글 (8.8.8.8)



설정파일 위치 : /etc/wireguard/wg0.conf
/etc/pivpn/wireguard/setupVars.conf

key 파일들도 위 폴더에 있음.





## 설치 

### 설치하기

```sh
curl -L https://install.pivpn.io | bash
```



### VPN Port

`51820`



### 설치확인

커맨드라인에 `pivpn` 을 입력하여 확인 가능합니다.

```sh
 $ pivpn
::: Control all PiVPN specific functions!
:::
::: Usage: pivpn <command> [option]
:::
::: Commands:
:::    -a, add              Create a client conf profile
:::    -c, clients          List any connected clients to the server
:::    -d, debug            Start a debugging session if having trouble
:::    -l, list             List all clients
:::   -qr, qrcode           Show the qrcode of a client for use with the mobile app
:::    -r, remove           Remove a client
:::  -off, off              Disable a user
:::   -on, on               Enable a user
:::    -h, help             Show this help dialog
:::    -u, uninstall        Uninstall pivpn from your system!
:::   -up, update           Updates PiVPN Scripts
:::   -bk, backup           Backup VPN configs and user profiles
```



### VPN Network 연결정보

`ifconfig` 명령어를 사용해서보면 새로 `tun0` 라는 openVPN 네트워크가 추가된 것을 확인할 수 있습니다. (참고로 wireguard는 `wg0` 입니다.)

```sh
 $ ifconfig
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.25.60  netmask 255.255.255.0  broadcast 192.168.25.255
        inet6 fe80::abec:3077:7670:35fd  prefixlen 64  scopeid 0x20<link>
        ether e4:5f:01:1b:a3:73  txqueuelen 1000  (Ethernet)
        RX packets 15155  bytes 3140152 (2.9 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 13608  bytes 7626252 (7.2 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 689  bytes 39597 (38.6 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 689  bytes 39597 (38.6 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

tun0: flags=4305<UP,POINTOPOINT,RUNNING,NOARP,MULTICAST>  mtu 1500
        inet 10.8.0.1  netmask 255.255.255.0  destination 10.8.0.1
        inet6 fe80::5633:be3:3e8a:3210  prefixlen 64  scopeid 0x20<link>
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 100  (UNSPEC)
        RX packets 3095  bytes 1467780 (1.3 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 7202  bytes 3191705 (3.0 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

wlan0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        ether e4:5f:01:1b:a3:74  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```


## VPN profile 관리

접속을 위해 사용되는 oepnVPN Profile 파일을 만듭니다.



### 만들어진 profile 관리

```sh
 $ pivpn -l
::: There are no clients to list
```



### 새 profile 만들기

localTest 라는 이름에 인증서를 새로 만듭니다. 아래 예제는 `localTest` 라는 이름으로 인증서를 만듭니다.

```sh
 $ pivpn -a -n localTest
::: Client Keys generated
::: Client config generated
::: Updated server config
::: WireGuard reloaded
======================================================================
::: Done! localTest.conf successfully created!
::: localTest.conf was copied to /home/pi/configs for easy transfer.
::: Please use this profile only on one device and create additional
::: profiles for other devices. You can also use pivpn -qr
::: to generate a QR Code you can scan with the mobile app.
======================================================================
```

해당 인증서는 openVPN의 경우 `home/<리눅스계정>/ovpns' 경로에서 확인할 수 있습니다.
(WireGuard의 경우 `home/<리눅스계정>/configs`)

```sh
~/configs $ ls
localTest.conf
```



### Profile 삭제

```sh
$ pivpn -r <인증서이름>
```

---



# 이하 WireGuard 관련내용 (현재는 사용하지 않음)
## VPN에 외부인터넷 연결 추가하기

### 설정파일 수정

`/etc/wireguard/wg0.conf` 파일에 아래와 같은 코드를 추가합니다.

```sh
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
```

이후부터 `wg-quick` 명령어를 이용하여 해당 네트워크를 조작할때 외부인터넷연결과 관련된 동작이 자동으로 실행됩니다.

```sh
root@:/etc/wireguard# wg-quick down wg0
[#] ip link delete dev wg0
[#] iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
iptables: Bad rule (does a matching rule exist in that chain?).

root@:/etc/wireguard# wg-quick up wg0
[#] ip link add wg0 type wireguard
[#] wg setconf wg0 /dev/fd/63
[#] ip -4 address add 10.6.0.1/24 dev wg0
[#] ip link set mtu 1420 up dev wg0
[#] iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```



또한 해당 네트워크 명령이 시스템부팅시 자동으로 실행되도록 아래 명령어를 서비스에 등록합니다.

```sh
$ systemctl enable wg-quick@wg0
```




## 스마트폰에서 연결하기

### 프로필을 QR코드 형식으로 나타내기

커맨드라인에서 `pivpn -qr <인증서명>` 을 입력하면 해당 인증정보가 담긴 VPN QR 코드가 생성됩니다.

```sh
 $ pivpn -qr localTest
::: Showing client localTest below
=====================================================================
█████████████████████████████████████████████████████████████████████
█████████████████████████████████████████████████████████████████████
████ ▄▄▄▄▄ █▄▀▄█▀▀  ▄█▄▄▄▄ ▄▄ ▀ ▀ ▄▄ ▄▄█▄▄▄ ▄▄▄ ▀█ ████  █ ▄▄▄▄▄ ████
████ █   █ ██ ▀▀▄▄▀▄▄ ▀▄▀▀ ▀ ▀█ ▄█▄▄ █▄██ ▀▄▄▄▀ ▄  █ █ ▄ █ █   █ ████
████ █▄▄▄█ ██▀█▀█▄█▄█▄█▄ ▄▄▀██▄█ ▄▄▄ ▀▄▀ ▄█▄▄▀▀▄▄  ▀▄█ ▄██ █▄▄▄█ ████
████▄▄▄▄▄▄▄█ █ █ █▄█▄█▄▀▄▀▄█ ▀▄▀ █▄█ █ ▀▄▀ █▄▀ ▀▄█ ▀ ▀ █▄█▄▄▄▄▄▄▄████
████ ▄█  █▄▀█ ▄▀██ ▀ ▄▀▄▀▄ ▀▄█▄█ ▄▄ ▄  ▀▄█ ▀▄▀ ▀▀█▄▀▄ ▀█ ▀ ██▀▀█ ████
████ ▄▄ ▀ ▄▄▀█ █▀▀▀▄▄▄ █▄▄█▀█ ▄▄▀ ▀▀ ▄▀ ▀█▄ ▄ █▄ █▀ ▄▄▀▄ ▄▀  ▀▀█▄████
████▀▄ ▀ ▀▄██▀█ ▀▀▄▄██▄▄▀██  ▀▄██▄ █▄▀▄██▄ ▀▄█ ▀▀▀▄ ▀ █ █▄ █▄▄ ▄▀████
█████▄  █ ▄█▀▀▀▄▄█▄█▀███  ▄ █ ▄▄██▀▀██▀▄ ▄▀  █▄▀▀▀ █▀▄▄▄▀█▀▄▀█▄▀█████
████  ▄ ▄▄▄  ▄ ▀█▄█ ██▄█▀▄▄▄▄▀▄▄   █▄▀███▀█▀▀█▄ ▀▀▀█ ▄ ▀▀▀▀▀▀█▀ ▀████
████  ▄▀ ▄▄█▀█ ▀▄▀  ▀▄▄ █ ▄▄▀ ▄▄ ▀▀ █ █ █  ▀▄▄▀ ▀███▄▀▀▄▀▄█▄▀▄▀▀█████
████▀▄  ██▄▀█████▀█▄▄  ▄▀▀   █ ▄▀▄▄▄▄▀▀  ▀▀█ █▀ ▀█▄ ▀▀ ▄▀ ▄▄██▄▀▀████
████▄ █ ▀ ▄▀▀▀▀▀▄█ ▄▄▄    ▀▀▀▀ ▀▀▀▀▄ █▄ ▄█▀▀▀▀▄██▄█  ▄██  ▀█ ▀▀▄▀████
████ ███▀▄▄▄ ▀ ██▀▄▄    ██▀▄▀  ▄▄▄█  ▀▄  ▀█ ▀▀▀█▄ █▀█▄▀▄▀▀ ▀▄▄█ ▀████
████▀█▄▄  ▄ ▀███▀██▄█▄ ▄▀ █▄█▀  █ ▀ ▀▄▀█ █▀▄▀▄▀█ ▀██ ▄ █ ▀█▄█▀  ▄████
████  ▄▄ ▄▄▄ ▄▄██▀▀▀ ▀▄▄▄█▀▄  ▄  ▄▄▄ ██▀██▄▀ █▄ ▄▄█▄▀█▀█ ▄▄▄ ██▀▀████
████ ▄█  █▄█ ▄▄▄█▀▀██ █▀▀  █▀▄▄▄ █▄█ ▄▀█▄▄  ▄▄▄▄▀▄▀▄▄ ██ █▄█ ▀▀ █████
████▄▄▀▀  ▄▄▄▀ ▀▄▀▀█  ▀▄▄▄██ ██▄▄▄   █ ▀▄▀ █▄▀ ▄██ ▄ ▀ ▄  ▄  ▄ █ ████
████ ██▀█▄▄█▀▄▀▀█▄ █▀▄▄▄ ▄▄▀▀▀▀▀▀▄▄██ ▀ ▀█▄▄▀▀ ▀▄▄ ▀ █▀▄▀ ▄█▀▄ ▄▀████
████▄▄█ ▄▄▄▀ █▄▄▀▄  ▄█▀▀▀  █ ▄▄▄▀▀▀▀█ █▀▀▀ ▀█▄  █ ▄  █▀▄▀▄█▄▄▀  ▀████
████▄▄▄█▄█▄ ▀▀▄ ▄▄▄▄▀▄█▀  ▀█▀▄█▄ ▀ ▀█▀▄▀▄▄▀▄▄▄▄▄██▄█ ▄█▀█▀ ▄▄ ▀█ ████
████ █ ▀ █▄██▀  █▄ ▄█▀▀█▄▄▀█ ▄▀▀▄█▄██ ▀▀ ▄█ █▄ ▄▄▀█▀▄ ▄   ▀▀▄█   ████
█████ ▀▄█ ▄▄ ▀ ▀█  ▄██ ▀▀ █▄█▄▄ ▀ ██ ▄▄   ▀  ▄ ▄   ▄▀▀██▄▀ █ █▄█ ████
████▄ ▀▄▀█▄ █ ▀█▄▄ ▀▀ ▄▀▀ █▀ ▀▀█ ▀▀██  █ ▀█▀    █▄ ▀ █▀█▀▀▄▀ █▀▀▄████
████ ▀█▄█▄▄▀▀ █▀▀▀▀▀▀ ▄██ █▀█▀   ▄█▄ █▀█ ▄▀ █▀▀▀█▄▀▄██▄▄▄▀▄ ▄▀ ▀▄████
████▀ ▀▄▄█▄▄▀ █▀▀█▀   ▀▀▄▄▄▀█▀ ▄ █▄▄  ██▄▄ █▄▄█▄▀▄▄▀ ▀█▄▀▄ ▄ ██▄▄████
████▀▀ ▄ ▄▄ ▄▀▀▄█▄  ██▄█  ▄█▀  ▀▀█▄▄█  ▀▄▄▀█▀█▄ ██▀█▄▄▄▄██ ▄  █▄▄████
████▄▄▄▄██▄▄▀█ ▄  ███▄▄▀█ █ █▀▀▄ ▄▄▄   █   █▄  ▄ ▄ ▄█ █  ▄▄▄  ▀ █████
████ ▄▄▄▄▄ ██▄▄▀▀▀▀▄▀  ▀ ▄ ▄█▄▄▀ █▄█ ▄  ▄ ▄ ▄ ▄ ▄▄█▄▄█▀  █▄█  ▄  ████
████ █   █ █ █ ▄█▄  ▄▀ ▀▄█▄▄ ▄▀█▄▄  ▄  ▄ █  █▀▀ ▀██▀▀  ▄▄▄▄▄ ▄█▄▀████
████ █▄▄▄█ █▀█ █ ▀▄█▀ ▄██▄█▀███▄█▄ ▀█▄  ███▄▀ ▀ ▀▄▄ ▄██▄█ █▀ ▄▀  ████
████▄▄▄▄▄▄▄█▄▄▄▄█▄█▄██▄█▄▄▄▄█▄▄█▄███▄▄▄▄█▄▄███▄▄██████▄▄▄██▄▄▄▄█▄████
█████████████████████████████████████████████████████████████████████
█████████████████████████████████████████████████████████████████████
=====================================================================
```





## Window에서 연결하기

우선 window용 WireGuard 프로그램을 다운받아 설치합니다.

WireGuard 프로그램 : https://www.wireguard.com/install/



라즈베리파이에서 VPN 인증서 파일을 가져옵니다.



해당 인증서를 사용하여 연결을 만듭니다.



연결 이후 커맨드라인에서 `ipconfig` 명령을 통해 네트워크 정보를 확인해 보면 해당 인증서명으로 새로운 네트워크가 추가된 것을 볼 수 있습니다.

```sh
>ipconfig
Windows IP 구성

알 수 없는 어댑터 localTest:
   연결별 DNS 접미사. . . . :
   IPv4 주소 . . . . . . . . . : 10.6.0.2
   서브넷 마스크 . . . . . . . : 255.255.255.0
   기본 게이트웨이 . . . . . . : 0.0.0.0
```

