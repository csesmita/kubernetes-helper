kubectl delete jobs `kubectl get jobs -o custom-columns=:.metadata.name`
rm -rf job[1-9]*.yaml
echo $w1tch#123 | sudo rm /local/scratch/syslog
sudo systemctl restart rsyslog
echo "Number of pods still around = "
kubectl get pods| wc -l
echo "Check syslog is fine."
