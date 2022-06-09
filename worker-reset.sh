yes | sudo kubeadm reset && sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X && sudo rm -rf /etc/cni/net.d && sudo rm -rf $HOME/.kube/config; sudo ip link set cni1 down ; sudo ip link set flannel.1 down ; sudo ip link delete cni0 ; sudo ip link delete flannel.1 ; sudo systemctl restart containerd && sudo systemctl restart kubelet
sudo kubeadm join 128.110.219.85:6443 --token tkutx2.igtmj6aansi9m8hg \
	        --discovery-token-ca-cert-hash sha256:3299e195bac12fbc2c7358674de5b3c4e0d8c55d0c73944d6a29d9decf222e5f
