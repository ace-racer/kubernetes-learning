## How to deploy streamlit application to Azure Kubernetes service

    ### 1. Upload the container to Azure container service (ACS)
    Deploy a custom image to a private container registry
    Taken from: https://docs.microsoft.com/en-us/azure/app-service/tutorial-custom-container?pivots=container-linux
    `sudo docker tag mf:0.1 indiamfs.azurecr.io/mf:latest`
    `sudo docker push indiamfs.azurecr.io/mf:latest`

    ### 2. Kubernetes version 1.18.14
        Taken from: https://docs.microsoft.com/en-us/azure/aks/cluster-container-registry-integration
        a. az aks update -n indiamfs -g myaks --attach-acr indiamfs
        b. kubectl apply -f azure-india-mf-deployment.yaml
        c. kubectl get pods

        Running pods


    ### 3. https://kubernetes.io/docs/concepts/services-networking/service/ and https://docs.microsoft.com/en-us/azure/application-gateway/ingress-controller-expose-service-over-http-https
    and https://raw.githubusercontent.com/kubernetes/examples/master/guestbook/all-in-one/guestbook-all-in-one.yaml
    # Complete guestbook application: https://raw.githubusercontent.com/kubernetes/examples/master/guestbook/all-in-one/guestbook-all-in-one.yaml
    a. Create a service:  kubectl apply -f azure-india-mf-service.yaml
    b. Create an ingress: kubectl apply -f azure-india-mf-ingress.yaml
    c. Install Helm for application gateway ingress controller - given up here!!