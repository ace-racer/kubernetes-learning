kubectl version --short && kubectl get componentstatus && kubectl get nodes && kubectl cluster-info

## Output:
#Client Version: v1.14.0
#Server Version: v1.14.0

#NAME                 STATUS    MESSAGE             ERROR
#scheduler            Healthy   ok
#controller-manager   Healthy   ok
#etcd-0               Healthy   {"health":"true"}

#NAME     STATUS   ROLES    AGE   VERSION
#master   Ready    master   13m   v1.14.0
#node01   Ready    <none>   12m   v1.14.0

#Kubernetes master is running at https://172.17.0.49:6443
#dash-kubernetes-dashboard is running at https://172.17.0.49:6443/api/v1/namespaces/kube-system/services/dash-kubernetes-dashboard:http/proxy
#KubeDNS is running at https://172.17.0.49:6443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

# The Helm package manager used for installing applications on Kubernetes is also available.

# You can administer your cluster with the kubectl CLI tool or use the visual Kubernetes Dashboard. Use this script to access the protected Dashboard.
# token.sh
#!/bin/bash
export COLOR_RESET='\e[0m'
export COLOR_LIGHT_GREEN='\e[0;49;32m'

# Technique to grab Kubernetes dashboard access token.
# Typically used in Katacoda scenarios.

echo 'To access the dashboard click on the Kubernetes Dashboard tab above this command '
echo 'line. At the sign in prompt select Token and paste in the token that is shown below.'
echo ''
echo 'For Kubernetes clusters exposed to the public, always lock administration access including '
echo 'access to the dashboard. Why? https://www.wired.com/story/cryptojacking-tesla-amazon-cloud/'

SECRET_RESOURCE=$(kubectl get secrets -n kube-system -o name | grep dash-kubernetes-dashboard-token)
ENCODED_TOKEN=$(kubectl get $SECRET_RESOURCE -n kube-system -o=jsonpath='{.data.token}')
export TOKEN=$(echo $ENCODED_TOKEN | base64 --decode)
echo ""
echo "--- Copy and paste this token for dashboard access ---"
echo -e $COLOR_LIGHT_GREEN
echo -e $TOKEN
echo -e $COLOR_RESET