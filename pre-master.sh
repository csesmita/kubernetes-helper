#!/bin/bash

#git clone https://github.com/csesmita/kubernetes-helper.git
#cd kubernetes-helper
git config --global credential.helper store
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
bash remote-setup.sh
yes | sudo kubeadm reset && sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X && sudo rm -rf /etc/cni/net.d && sudo rm -rf $HOME/.kube/config ; sudo ip link set cni0 down ; sudo ip link set flannel.1 down ; sudo ip link delete cni0 ; sudo ip link delete flannel.1 ; sudo systemctl restart containerd && sudo systemctl restart kubelet
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
mkdir -p $HOME/.kube && sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config && sudo chown sv440:decentralizedsch $HOME/.kube/config && kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
echo "Add kubeadm join command into worker-reset.sh. Dont run it since it will be run using master.sh."
read  -n 1 -p "Press any key to enter"
echo "Enter the number of nodes not including the master node (so, workers + management)"
read numnodes
eval `ssh-agent`
echo "Enter ssh password at the next prompt."
ssh-add
bash setup-worker.sh $numnodes
bash master.sh $numnodes
