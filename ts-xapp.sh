apt install iperf3
OAIC=`pwd`
sudo apt-get install nginx
          
sudo systemctl start nginx.service
cd /etc/nginx/sites-enabled
sudo unlink default
cd ../
cd ../../var/www
sudo mkdir xApp_config.local
cd xApp_config.local/
sudo mkdir config_files
cd ../../../etc/nginx/conf.d
sudo sh -c "echo 'server {
listen 5010 default_server;
server_name xApp_config.local;
location /config_files/ {
root /var/www/xApp_config.local/;
}
}' >xApp_config.local.conf"

echo ">>> reloading nginx..."
sudo nginx -t 
cd ${OAIC}
sudo cp TS-xApp/TS-xApp-config-file.json /var/www/xApp_config.local/config_files/
sudo systemctl reload nginx
echo ">>> getting machine IP..."
export MACHINE_IP=`hostname  -I | cut -f1 -d' '`

echo ">>> checking for config-file"
curl http://${MACHINE_IP}:5010/config_files/TS-xApp-config-file.json
echo ">>> building docker image...."
cd ${OAIC}/TS-xApp
echo ">>> checking directory"
ls
sudo docker build . -t xApp-registry.local:5008/TS-xApp:1.0.0

export KONG_PROXY=`sudo kubectl get svc -n ricplt -l app.kubernetes.io/name=kong -o jsonpath='{.items[0].spec.clusterIP}'`
export APPMGR_HTTP=`sudo kubectl get svc -n ricplt --field-selector metadata.name=service-ricplt-appmgr-http -o jsonpath='{.items[0].spec.clusterIP}'`
export ONBOARDER_HTTP=`sudo kubectl get svc -n ricplt --field-selector metadata.name=service-ricplt-xapp-onboarder-http -o jsonpath='{.items[0].spec.clusterIP}'`
