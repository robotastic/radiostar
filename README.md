# radiostar
 Learning how to Azure

`docker build -t radiostar:dev -f Dockerfile.dev .`


`docker run -v ${PWD}:/app -it radiostar:dev /bin/bash`  

`docker run --privileged --ulimit core=-1 -v ${PWD}:/app -v /dev/bus/usb:/dev/bus/usb  -v /var/run/dbus:/var/run/dbus -v /var/run/avahi-daemon/socket:/var/run/avahi-daemon/socket -it radiostar:dev /bin/bash` 