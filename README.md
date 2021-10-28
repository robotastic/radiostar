# radiostar
 Learning how to Azure

`docker build -t radiostar:dev -f Dockerfile.dev .`


## Start the Dev Container
`docker run -v ${PWD}:/app -it radiostar:dev /bin/bash`  

## Start the Dev Container with USB / RTL-SDR pass through
`docker run --privileged --ulimit core=-1 -v ${PWD}:/app -v /dev/bus/usb:/dev/bus/usb  -v /var/run/dbus:/var/run/dbus -v /var/run/avahi-daemon/socket:/var/run/avahi-daemon/socket -it radiostar:dev /bin/bash` 


## Join a running version of the Dev Container
`docker exec -it radiostar:dev /bin/bash`

