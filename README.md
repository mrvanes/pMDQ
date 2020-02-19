pMDQ Test
-------------

An implementation of a WebSub hub using Flask-websub, an nginx publisher (metadata source) and subscriber in pyFF.

### Metadata source
Nginx server publishing metadata in docroot, adding hub and self url in Link headers

### Hub/Publisher
Flask-websub Hub, accepting topic urls for pub.websub.local and hub.websub.local
pyFF Subscriber/Publisher

### Subscribe
pyFF Subscriber

## Testing
To build the pub/hub and sub dockers:
```./build.sh```

Clone the pyFF websub branch of my fork in pyFF directory:
```git clone https://github.com/mrvanes/pyFF.git -b websub```


To start the pub/hub and sub dockers:
```./run.sh```

To log in to the pub/hub and sub:
```
docker exec -ti pmdq_pub_1 /bin/bash
docker exec -ti pmdq_hub_1 /bin/bash
docker exec -ti pmdq_sub_1 /bin/bash
```

Add this to your /etc/hosts file
```
172.31.1.2      hub.websub.local
172.31.1.3      pub.websub.local
172.31.1.4      sub.websub.local
```

In the dockers, the websub code is installed in
```/opt/websub```

In the dockers, the pyFF fork is volume mounted on
```/opt/pyFF```

On the metadata source (pub) nginx can be made publisher by using this nginx configuration in ```/etc/nginx/sites-enabled/default```
```
        location / {
                # First attempt to serve request as file, then
                # as directory, then fall back to displaying a 404.
                try_files $uri $uri/ =404;
                add_header 'Link' '<$scheme://$host$request_uri>; rel="self", <http://hub.websub.local:8080/hub>; rel="hub"';
```

There should be valid metadata in ```/var/www/html/idp.xml``` with entityID ```http://pub.websub.local/idp```.

The hub pyFF configuration points to ```http://pub.websub.local/idp.xml```

The sub pyff configuration points to ```http://hub.websub.local/entities/http://pub.websub.local/idp```

Start the respective services by running the run scripts on each host:

```
    /opt/websub/run_hub.sh (on hub docker)
    /opt/pyFF/run_pyff_hub.sh (on hub docker)
    /opt/pyFF/run_pyff_sub.sh (on sub docker)
```

Now open three tabs in a browser
```
http://pub.websub.local/
http://hub.websub.local/
http://sub.websub.local/
```

On the pub, check the Metadata
```
http://pub.websub.local/idp.xml
```

On the hub, check the entityID of the published metadata on pub
```
http://hub.websub.local/entities/http://pub.websub.local/idp
```

On the sub check the entityID of the published metadata on hub
```
http://sub.websub.local/entities/http://hub.websub.local/entities/http://pub.websub.local/idp
```

Now update the original source metadata and to update metadata call the following URL using curl:

```
curl -X POST http://hub.websub.local/api/update -F 'entry=http://pub.websub.local/idp.xml'
```

See the metadata updated on the hub and the sub.


You can stop the dockers on your host by running
```
docker-compose stop
```
