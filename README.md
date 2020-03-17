pMDQ Test
-------------

An implementation of a WebSub hub using Flask-websub, an nginx publisher (metadata source) and subscriber in pyFF.

### Metadata source
Nginx server publishing metadata in docroot, adding hub and self url in Link headers  
Metadata source: ```config/nginx/html/idp.xml```  
Metadata endpoint: ```http://idp.websub.local/idp.xml```  
EntityID of metadata: ```http://idp.websub.local/idp```

### Hub
Flask-websub Hub, accepting topic urls for ```idp.websub.local``` and ```mdq.websub.local```

### MDQ
pyFF Subscriber/Publisher  
Metadata loaded from http://idp.websub.local/idp.xml

### Metadata consumer
pyFF Subscriber  
Metadata loaded from http://mdq.websub.local/entities/http://idp.websub.local/idp

## Testing
To build the idp/hub/mdq and sp dockers:  
```./build.sh```

To start the idp/hub/mdq and sp dockers:  
```./run.sh```

To login on idp/hub/mdq and sp:  
```
docker exec -ti pmdq_idp_1 /bin/bash
docker exec -ti pmdq_hub_1 /bin/bash
docker exec -ti pmdq_mdq_1 /bin/bash
docker exec -ti pmdq_sp_1 /bin/bash
```

Add this to your /etc/hosts file  
```
172.31.1.2      hub.websub.local
172.31.1.3      mdq.websub.local
172.31.1.4      idp.websub.local
172.31.1.5      sp.websub.local
```

In the dockers, the websub code is volume mounted on ```/opt/websub```  
The pyFF fork is volume mounted on ```/opt/pyFF```

Create a virtualenv and install Flask-websub in the hub docker:  
```
cd /opt/websub
virtualenv --python=python3 .
bin/pip install -e .
bin/pip install celery
bin/pip install redis
```

Create a virtualenv and install pyFF in the mdq docker:  
```
cd /opt/pyFF
virtualenv --python=python3 .
bin/pip install -e .
openssl req -nodes -x509 -newkey rsa:4096 -keyout sign.key -out sign.crt -days 3650 -subj "CN=websub.local"
```
Because of the shared volume mount, this also installs pyFF on sp docker.

Start the respective services by running the run scripts on each host:  
```
/opt/websub/run_hub.sh (on hub docker)
/opt/pyFF/run_pyff_mdq.sh (on mdq docker)
/opt/pyFF/run_pyff_sp.sh (on sp docker)
```

Now open three tabs in a browser  
```
http://idp.websub.local/idp.xml
http://mdq.websub.local/entities/http://idp.websub.local/idp
http://sp.websub.local/entities/http://idp.websub.local/idp
```

On the idp, check the metadata  
```
http://idp.websub.local/idp.xml
```

On the mdq, check the metadata of entityID http://idp.websub.local/idp  
```
http://mdq.websub.local/entities/http://idp.websub.local/idp
```

On the sp check the metadata of entityID http://idp.websub.local/idp  
```
http://sp.websub.local/entities/http://idp.websub.local/idp
```

Now update the original source metadata and update metadata by calling one of the following URLs using curl:

For a non-websub metadata provider (without hub) directly call the pyFF MDQ update endpoint:  

```
curl -X POST http://mdq.websub.local/api/update -F 'entry=http://idp.websub.local/idp'
```

For a websub capable metadata provider notify the hub:  

```
curl -X POST http://hub.websub.local/update -F 'topic=http://idp.websub.local/idp.xml'
```


See the metadata updated on the idp, mdq and the sp.


You can stop the dockers on your host by CTRL-C'ing ```run.sh``` on your host
