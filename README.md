# APTpy
A proof of concept Advanced Persistence Threat written in Python.
For more info about this project, please take a look at this blog post: https://www.nc-lp.com/blog/build-a-custom-apt-module

This is the client side, you can find the code for the server part [in this repository](https://github.com/tampe125/APTserver).

## Usage 
Simply start the script using:  
```
tampe125@Death-Star:~/git/APTpy$ python aptpy.py 

2017-03-09 12:37:10|INFO    | [MAIN] Client id: S1D8VCGV
2017-03-09 12:37:10|DEBUG   | [MAIN] Registering channels
2017-03-09 12:37:10|DEBUG   | [CHANNEL] Next connection attempt will be at 2017-03-09 12:37:25
2017-03-09 12:37:11|DEBUG   | [MAIN] Registering modules
2017-03-09 12:37:11|DEBUG   | [MAIN] Starting channel connection
2017-03-09 12:37:11|DEBUG   | [MAIN] Starting all modules
2017-03-09 12:37:11|DEBUG   | [MAIN] Starting main loop
2017-03-09 12:37:25|DEBUG   | [HTTP] Trying to contact the remote server
2017-03-09 12:37:26|DEBUG   | [HTTP] Got the key from the remote server
2017-03-09 12:37:26|DEBUG   | [HTTP] Trying to get new commands from the remote server
2017-03-09 12:37:26|DEBUG   | [HTTP] Trying to report completed jobs
2017-03-09 12:37:26|DEBUG   | [CHANNEL] Next connection attempt will be at 2017-03-09 12:37:41
2017-03-09 12:37:27|INFO    | [MAIN] Got command {u'cmd': u'ls -la', u'id': 1, u'module': u'ShellModule'} from the queue
2017-03-09 12:37:27|INFO    | [MAIN] Module ShellModule reclaimed the message
2017-03-09 12:37:41|DEBUG   | [HTTP] Trying to get new commands from the remote server
2017-03-09 12:37:42|DEBUG   | [HTTP] Trying to report completed jobs
2017-03-09 12:37:43|DEBUG   | [CHANNEL] Next connection attempt will be at 2017-03-09 12:37:58
```
**Please note: the client is compatible with Windows only.**

## Required changes
In order to keep interaction with the filesystem low, some values are hardcoded, so you'll have to change it accordingly to your needs.

**Turn debug off**  
Open [aptpy.py](https://github.com/tampe125/APTpy/blob/master/aptpy.py) file and set the `DEBUG` variable to `False`.  
This will suppress the output and increase the delay between the calls.  

**Change remote host for HTTP channel**  
Open [http.py](https://github.com/tampe125/APTpy/blob/master/lib/channels/http.py) file and change the variable `self._remote_host` with your server.

**Change public and private keys**  
Open [encrypt.py](https://github.com/tampe125/APTpy/blob/master/lib/encrypt.py) file and change the variables `CLIENT_PRIV_KEY`, `CLIENT_PUB_KEY`, `SRV_PUB_KEY`. Ideally, you should create your own public/private pairs for each client and change the main server pairs, too.
