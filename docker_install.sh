sudo apt-get update
sudo apt-get install -y docker-ce
sudo apt-get install docker-compose -y
sudo usermod -aG docker "${USER}"
su - "${USER}"