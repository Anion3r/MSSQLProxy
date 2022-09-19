# MSSQLProxy
一个能够利用MSSQL的xp_cmdshell功能来进行流量代理的脚本，用于在站酷分离且不出网SQL注入进行代理
# 其他
1. upload.py 能够方便的通过SQL注入上传文件
2. proxy.py 能够进行代理，但是在使用前记得更改 `exec_xp_cmdshell` 函数里的注入方法，根据自己的注入点灵活变通
# TODO
- [ ] 支持 `HTTPS` 代理
- [ ] 支持 `So5cks` 代理
