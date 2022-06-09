sudo rm /local/scratch/syslog
sudo systemctl restart docker
sudo systemctl restart rsyslog
yes | sudo docker system prune -a
