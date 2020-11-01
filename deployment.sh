## Refer: https://kubernetes.io/docs/concepts/overview/working-with-objects/kubernetes-objects/

apiVersion: extensions/v1beta1
kind: Deploymentmetadata:
  labels:
    run: hello
  name: hello
spec:
  replicas: 1
  selector:
    matchLabels:
      run: hello
  template:
    metadata:
      labels:
        run: hello
    spec:
      containers:
      - image: k8s.gcr.io/echoserver:1.9
        name: hello
        ports:
        - containerPort: 8080