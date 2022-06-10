kubectl delete jobs `kubectl get jobs -o custom-columns=:.metadata.name`
rm -rf job[1-9]*.yaml
sudo rm /local/scratch/syslog
sudo systemctl restart rsyslog
echo "Ensuring node1 has NoSchedule Taint"
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints --no-headers | grep node1.sv440
echo "Number of pods still around = "
kubectl get pods| wc -l
echo "Check syslog is fine."
