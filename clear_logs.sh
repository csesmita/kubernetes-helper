sudo rm /local/scratch/syslog
sudo systemctl restart docker
sudo systemctl restart rsyslog
sudo systemctl stop kubelet
sudo systemctl start kubelet
yes | sudo docker system prune -a
