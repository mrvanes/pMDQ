pMDQ
-------------

An implementation of a WebSub hub, publisher and subscriber as a Flask
extension. The implementation builds on https://flask-websub.readthedocs.io/en/latest/examples.html

This is a docker-compose version of Flask-Websub to demostrates a possible implementation of pMDQ.

To build the pub/hub and sub dockers:
```./build.sh```

To start the pub/hub and sub dockers:
```./run.sh```

To log in to the pub/hub and sub:
```
docker exec -ti pmdq_pub_1 /bin/bash
docker exec -ti pmdq_hub_1 /bin/bash
docker exec -ti pmdq_sub_1 /bin/bash
```

Add this to /etc/hosts
```
172.31.1.2      hub.websub.local
172.31.1.3      pub.websub.local
172.31.1.4      sub.websub.local
```

The websub code is installed in
```/opt/websub```

Start the respective services by running the run scripts on each host:
```
/opt/websub/run_publisher.sh
/opt/websub/run_hub.sh
/opt/websub/run_subscriber.sh
```

Now open three tabs in a browser
```
http://pub.websub.local/
http://hub.websub.local/
http://sub.websub.local/
```

On the pub, check the Metadata
```[pub]metadata-1[pub]```
The [pub] parts designate imaginative pub-signature.

On the hub, click "Subscribe" and return to the home page. Check metadata.
```[hub][pub]metadata-1[pub][hub]```
The [hub] parts designate imaginative hub-signature, the metadata-1 is the original pub md topic.

Now on the sub, click "Subscribe" and return home, the page will show metadata on the bottom:
```
http://hub.websub.local/md?id=http://pub.websub.local/md
[hub][pub]metadata-1[pub][hub]
```
The url designates hub's metadata topic, and the line below the hub-signed metadata of pub.

Now, on the pub click "Update" and check the metadata on pub, hub and sub:
pub: ```[pub]metadata-2[pub]```
hub: ```[hub][pub]metadata-2[pub][hub]```
sub: ```[pub]metadata-3[pub]```

The update on pub automatically triggered an update on sub, via pub's callback on hub's subscriber. This can all be checked by the logging in the running applications in the dockers.
