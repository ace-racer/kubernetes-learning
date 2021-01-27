sudo docker build --tag mf:0.1 .
sudo docker run --publish 8501:8501 --name mf mf:0.1

# Other commands
sudo docker container ls -a

sudo docker container kill <<ContainerName>>
sudo docker container rm <<ContainerName>>

# Interactive session inside the container
sudo docker exec -it pd /bin/bash