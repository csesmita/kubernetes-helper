yes | sudo kubeadm reset && sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X && sudo rm -rf /etc/cni/net.d && sudo rm -rf $HOME/.kube/config && sudo ip link set cni1 down && sudo ip link set flannel.1 down && sudo ip link delete cni0 && sudo ip link delete flannel.1 && sudo systemctl restart containerd && sudo systemctl restart kubelet
sudo kubeadm join 128.110.217.163:6443 --token dvvu70.1i45jcj29okzytpm \
	        --discovery-token-ca-cert-hash sha256:50e39475cbf4efbe78df12cf0ffbfd2cc6872e37b41a993cfaab7e3e71acd225
