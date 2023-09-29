sudo rm /local/scratch/syslog
sudo rm /local/scratch/kubeletqueue
sudo systemctl restart docker
sudo systemctl restart rsyslog
sudo systemctl stop kubelet
sudo systemctl start kubelet
yes | sudo docker system prune -a
