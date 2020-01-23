pMDQ
-------------

An implementation of a WebSub hub, publisher and subscriber as a Flask
extension. The implementation is meant to be used as a library that can be
integrated in a larger application.

This is a docker-compose version of Flask-Websub to demostrate pMDQ.

To build the pub/hub and sub dockers:
```./build.sh```

To start the pub/hub and sub dockers:
```./run.sh```

Add this to /etc/hosts
```
172.31.1.2      hub.websub.local
172.31.1.3      pub.websub.local
172.31.1.4      sub.websub.local
```

To log in to the pub/hub and sub:
```
ssh -i websub_key websub@pub.websub.local
ssh -i websub_key websub@hub.websub.local
ssh -i websub_key websub@sub.websub.local
```

The websub code is installed in
```/opt/websub```
