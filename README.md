pMDQ Test
-------------

An implementation of a WebSub hub using Flask-websub, an nginx publisher (Federation A metadata source) and subscriber (Federation B) in pyFF.

### Metadata source Federation A
Nginx server publishing metadata in docroot, adding hub and self url in Link headers  
Metadata source: ```config/nginx/html/feda.xml```  
Metadata endpoint: ```http://feda.websub.local/feda.xml```  
EntityID of metadata: ```http://feda.websub.local/feda```

### Hub
Flask-websub Hub, accepting topic urls for ```feda.websub.local``` and ```mdq.websub.local```

### MDQ
pyFF Subscriber/Publisher  
Metadata loaded from http://feda.websub.local/feda.xml

### Metadata consumer Federation B
pyFF Subscriber  
Metadata loaded from http://mdq.websub.local/.well-known/webfinger

## Testing
To build the feda/hub/mdq and fedb dockers:  
```./build.sh```

To start the feda/hub/mdq and fedb dockers:  
```./run.sh```

To login on feda/hub/mdq and fedb:  
```
docker exec -ti pmdq_feda_1 /bin/bash
docker exec -ti pmdq_hub_1  /bin/bash
docker exec -ti pmdq_mdq_1  /bin/bash
docker exec -ti pmdq_fedb_1 /bin/bash
```

Add this to your /etc/hosts file  
```
172.31.1.2      hub.websub.local
172.31.1.3      mdq.websub.local
172.31.1.4      feda.websub.local
172.31.1.5      fedb.websub.local
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
/opt/pyFF/run_pyff_fedb.sh (on sp docker)
```

Now open three tabs in a browser  
```
http://feda.websub.local/feda.xml
http://mdq.websub.local/entities/http://feda.websub.local/feda
http://fedb.websub.local/entities/http://feda.websub.local/feda
```

On Federtation A, check the metadata  
```
http://feda.websub.local/feda.xml
```

On the mdq, check the metadata of entityID http://feda.websub.local/feda  
```
http://mdq.websub.local/entities/http://feda.websub.local/feda
```

On Federation B check the metadata of entityID http://feda.websub.local/feda  
```
http://fedb.websub.local/entities/http://feda.websub.local/feda
```

Now update the original source metadata and update metadata by calling one of the following URLs using curl:

For a non-websub metadata provider (without hub) directly call the pyFF MDQ update endpoint:  

```
curl -X POST http://mdq.websub.local/api/update -F 'entry=http://feda.websub.local/feda'
```

For a websub capable metadata provider notify the hub:  

```
curl -X POST http://hub.websub.local/update -F 'topic=http://feda.websub.local/feda.xml'
```


See the metadata updated on Federation A, mdq and Federation B.


You can stop the dockers on your host by CTRL-C'ing ```run.sh``` on your host
