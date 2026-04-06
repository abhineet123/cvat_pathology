<a id="remote_access___debug_functions_deploy_"></a>
# remote_access       @ debug/functions/deploy-->cvat_setup
`remote access setup is only needed on the host and the client doesn't even need to have cvat installed or working`

sudo docker compose -f docker-compose.yml build

sudo docker compose -f docker-compose.yml  -f docker-compose.override.yml build
sudo docker compose -f docker-compose.yml -f docker-compose.override.yml up -d

CVAT_HOST=104.205.236.116 sudo -E docker compose -f docker-compose.yml -f docker-compose.override.yml up -d

https://github.com/cvat-ai/cvat/issues/1095#issuecomment-578744392
```
services:
  cvat_server:
    ports:
      - "8070:8080"
    environment:
      ALLOWED_HOSTS: '*'
      UI_SCHEME: http
      UI_HOST: 104.205.236.116
      UI_PORT: 7060
  cvat_ui:
    build:
      args:
        REACT_APP_API_HOST: 104.205.236.116
        REACT_APP_API_PORT: 8060
      dockerfile: Dockerfile.ui
    ports:
      - "7070:80"
```

<a id="issues___debug_functions_deploy_"></a>
## issues       @ remote_access-->cvat_setup_obsolete
Can access CVAT over LAN but not Internet #1095
https://github.com/cvat-ai/cvat/issues/1095
404 not found when access through localhost  #3835
https://github.com/cvat-ai/cvat/issues/3835
Accessing CVAT from local network #3982
https://github.com/cvat-ai/cvat/issues/3982
Unable to access cvat running on localhost:8080 via ngrok tunnel #7075
https://github.com/cvat-ai/cvat/issues/7075
Remote access to CVAT, unable to connect remotely via LAN or internet domain (via <HOST-IP>:port or <FQDN>:port). Blocked by CORS policy: No 'Access-Control-Allow-Origin, Network Error and net::ERR CONNECTION REFUSED errors. #1011
https://github.com/cvat-ai/cvat/issues/1011
Access CVAT remotely via <HOST_IP>:port or <FQDN>:port?  #128
https://github.com/cvat-ai/cvat/issues/128
Got 404 not page found after I deployed CVAT 2.41.0 successfully #10008
https://github.com/cvat-ai/cvat/issues/10008
404 Page not found on CVAT server link #8715
https://github.com/cvat-ai/cvat/issues/8715
'404 page not found' when accessing from remote machine #7192
https://github.com/cvat-ai/cvat/issues/7192

