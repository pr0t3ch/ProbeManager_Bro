#!/usr/bin/env bash

echo '## Install Bro ##'
# Install on ProbeManager server
# Get args
arg=$1
destfull=$2

if [[ "$BRO_VERSION" == "" ]]; then
    BRO_VERSION="2.5.3"
fi
config=""
rules=""
# OSX with brew
if [[ $OSTYPE == *"darwin"* ]]; then
    if brew --version | grep -qw Homebrew ; then
        if ! brew list | grep -qw bro ; then
            brew install bro
        fi
        config="/usr/local/etc/"
        rules="/usr/local/opt/bro/share/bro/"
    fi
elif [ -f /etc/debian_version ]; then
    # Ubuntu
    if [[ "$TRAVIS" = true ]]; then
        if ! type bro ; then
            curl http://download.opensuse.org/repositories/network:bro/xUbuntu_14.04/Release.key | sudo apt-key add -
            echo "deb http://download.opensuse.org/repositories/network:/bro/xUbuntu_14.04/ /" | sudo tee -a /etc/apt/sources.list
            sudo apt-get update -qq
            sudo apt-get -y --allow-unauthenticated install bro
            export PATH=/opt/bro/bin:$PATH && export LD_LIBRARY_PATH=/opt/bro/lib/:$LD_LIBRARY_PATH
            sudo setcap cap_net_raw,cap_net_admin=eip $( which bro )
        fi
        sudo chown "$SERVER_USER":"$CURRENT_USER" $( which bro )
        sudo chown -R "$SERVER_USER":"$CURRENT_USER" /opt/bro
        sudo chmod -R 770 /opt/bro
        sudo chmod 750 $( which bro )
        config="/opt/bro/etc/"
        rules="/opt/bro/share/bro/"
    else # Debian and ubuntu
        if ! type bro ; then
            sudo apt update
            sudo apt install cmake make gcc g++ flex bison libpcap-dev libssl-dev python-dev swig zlib1g-dev libmagic-dev libgeoip-dev sendmail libcap2-bin wget curl ca-certificates
            wget https://www.bro.org/downloads/bro-"$BRO_VERSION".tar.gz
            tar xf bro-"$BRO_VERSION".tar.gz
            ( cd bro-"$BRO_VERSION" && ./configure )
            ( cd bro-"$BRO_VERSION" && make -j$(nproc)  )
            ( cd bro-"$BRO_VERSION" && sudo make install )
            rm bro-"$BRO_VERSION".tar.gz && sudo rm -rf bro-"$BRO_VERSION"
            export PATH=/usr/local/bro/bin:$PATH && export LD_LIBRARY_PATH=/usr/local/bro/lib/:$LD_LIBRARY_PATH
            sudo setcap cap_net_raw,cap_net_admin=eip $( which bro )
        fi
        if ! type critical-stack-intel ; then
            curl --silent https://packagecloud.io/install/repositories/criticalstack/critical-stack-intel/script.deb.sh | sudo bash
            sudo apt-get install critical-stack-intel
        fi
        if [[ "$arg" = 'prod' ]]; then
                sudo chown "$SERVER_USER":"$CURRENT_USER" $( which bro )
                sudo chown -R "$SERVER_USER":"$CURRENT_USER" /usr/local/bro
                sudo chown -R "$SERVER_USER":"$CURRENT_USER" /etc/bro
                sudo chmod -R 770 /usr/local/bro
                sudo chmod 750 $( which bro )
        else
                sudo chown "$CURRENT_USER" $( which bro )
                sudo chown -R "$CURRENT_USER" /usr/local/bro
        fi
        config="/usr/local/bro/etc/"
        rules="/etc/bro/"
    fi
fi

if ! type bro ; then
    exit 1
fi

which bro
bro --version
which broctl
broctl --version

echo "BRO_BINARY = '$( which bro )'" > "$destfull"probemanager/bro/settings.py
echo "BROCTL_BINARY = '$( which broctl )'" >> "$destfull"probemanager/bro/settings.py
echo "BRO_CONFIG = '$config'" >> "$destfull"probemanager/bro/settings.py#!/usr/bin/env bash

echo '## Install bro ##'
# Install on ProbeManager server
# Get args
arg=$1
destfull=$2

if [[ "$BRO_VERSION" == "" ]]; then
    BRO_VERSION="2.5.3"
fi
config=""
rules=""
# OSX with brew
if [[ $OSTYPE == *"darwin"* ]]; then
    if brew --version | grep -qw Homebrew ; then
        if ! brew list | grep -qw bro ; then
            brew install bro
        fi
        config="/usr/local/etc/"
        rules="/usr/local/opt/bro/share/bro/"
    fi
elif [ -f /etc/debian_version ]; then
    # Ubuntu
    if [[ "$TRAVIS" = true ]]; then
        if ! type bro ; then
            curl -fsSL https://download.opensuse.org/repositories/security:bro/xUbuntu_18.04/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/security:bro.gpg > /dev/null
            echo 'deb http://download.opensuse.org/repositories/security:/bro/xUbuntu_18.04/ /' | sudo tee /etc/apt/sources.list.d/security:bro.list
            sudo apt-get update -qq
            sudo apt-get -y --allow-unauthenticated install bro
            export PATH=/opt/bro/bin:$PATH && export LD_LIBRARY_PATH=/opt/bro/lib/:$LD_LIBRARY_PATH
            sudo setcap cap_net_raw,cap_net_admin=eip $( which bro )
        fi
        sudo chown "$SERVER_USER":"$CURRENT_USER" $( which bro )
        sudo chown -R "$SERVER_USER":"$CURRENT_USER" /opt/bro
        sudo chmod -R 770 /opt/bro
        sudo chmod 750 $( which bro )
        config="/opt/bro/etc/"
        rules="/opt/bro/share/bro/"
    else # Debian and ubuntu
        if ! type bro ; then
            sudo apt update
            sudo apt install cmake make gcc g++ flex bison libpcap-dev libssl-dev python-dev swig zlib1g-dev libmagic-dev libgeoip-dev sendmail libcap2-bin wget curl ca-certificates
            wget https://download.zeek.org/bro-"$BRO_VERSION".tar.gz
            tar xf bro-"$BRO_VERSION".tar.gz
            ( cd bro-"$BRO_VERSION" && ./configure )
            ( cd bro-"$BRO_VERSION" && make -j$(nproc)  )
            ( cd bro-"$BRO_VERSION" && sudo make install )
            rm bro-"$BRO_VERSION".tar.gz && sudo rm -rf bro-"$BRO_VERSION"
            export PATH=/usr/local/bro/bin:$PATH && export LD_LIBRARY_PATH=/usr/local/bro/lib/:$LD_LIBRARY_PATH
            sudo setcap cap_net_raw,cap_net_admin=eip $( which bro )
        fi
        if ! type critical-stack-intel ; then
            curl --silent https://packagecloud.io/install/repositories/criticalstack/critical-stack-intel/script.deb.sh | sudo bash
            sudo apt-get install critical-stack-intel
        fi
        if [[ "$arg" = 'prod' ]]; then
                sudo chown "$SERVER_USER":"$CURRENT_USER" $( which bro )
                sudo chown -R "$SERVER_USER":"$CURRENT_USER" /usr/local/bro
                sudo chown -R "$SERVER_USER":"$CURRENT_USER" /etc/bro
                sudo chmod -R 770 /usr/local/bro
                sudo chmod 750 $( which bro )
        else
                sudo chown "$CURRENT_USER" $( which bro )
                sudo chown -R "$CURRENT_USER" /usr/local/bro
        fi
        config="/usr/local/bro/etc/"
        rules="/etc/bro/"
    fi
fi

if ! type bro ; then
    exit 1
fi

which bro
bro --version
which broctl
broctl --version

echo "BRO_BINARY = '$( which bro )'" > "$destfull"probemanager/bro/settings.py
echo "BROCTL_BINARY = '$( which broctl )'" >> "$destfull"probemanager/bro/settings.py
echo "BRO_CONFIG = '$config'" >> "$destfull"probemanager/bro/settings.py
echo "BRO_RULES = '$rules'" >> "$destfull"probemanager/bro/settings.py
echo "BRO_VERSION = '$BRO_VERSION'" >> "$destfull"probemanager/bro/settings.py

echo "BRO_RULES = '$rules'" >> "$destfull"probemanager/bro/settings.py
echo "BRO_VERSION = '$BRO_VERSION'" >> "$destfull"probemanager/bro/settings.py
