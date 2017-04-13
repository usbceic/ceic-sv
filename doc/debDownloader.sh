sudo apt-get download $1
sudo apt-cache depends -i $1 | awk '/Depends:/ {print $2}' | xargs  sudo apt-get download
