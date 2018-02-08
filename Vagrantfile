# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version. Please don't change it unless you know what
# you're doing.
VAGRANTFILE_VERSION = "2"

# WTF ENVIRONMENT VARIABLES
WTF_WEB_PORT = "5000"
WTF_WEB_HOST = "0.0.0.0"

WTF_API_PORT = "5000"
WTF_API_HOST = "0.0.0.0"

WTF_PORT = "5000"
WTF_HOST = "0.0.0.0"

Vagrant.configure(VAGRANTFILE_VERSION) do |config|

  config.vm.box = "ubuntu/trusty64"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  config.vm.network "forwarded_port", guest: WTF_PORT, host: WTF_PORT

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Enable provisioning with a shell script. Updates & Installs pip and pipenv.
  config.vm.provision "shell", inline: <<-SHELL
    add-apt-repository ppa:jonathonf/python-3.6
    apt-get update -y && apt-get install python3.6 -y
    curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
    python3.6 get-pip.py
    pip3 install pipenv
    echo "cd /vagrant" >> /home/vagrant/.bashrc
    echo "export WTF_HOST=#{WTF_HOST}" >> /home/vagrant/.bash_profile
    echo "export WTF_PORT=#{WTF_PORT}" >> /home/vagrant/.bash_profile
    echo "export WTF_API_HOST=#{WTF_API_HOST}" >> /home/vagrant/.bash_profile
    echo "export WTF_API_PORT=#{WTF_API_PORT}" >> /home/vagrant/.bash_profile
    echo "export WTF_WEB_PORT=#{WTF_WEB_PORT}" >> /home/vagrant/.bash_profile
    echo "export WTF_WEB_HOST=#{WTF_WEB_HOST}" >> /home/vagrant/.bash_profile
  SHELL
end
