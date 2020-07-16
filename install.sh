#!/usr/bin/env bash

echo '## Install Bro ##'
# Install on ProbeManager server
# Get args
arg=$1
destfull=$2

if [[ "$ZEEK_VERSION" == "" ]]; then
    ZEEK_VERSION="2.5.3"
fi
config=""
rules=""
# OSX with brew
if [[ $OSTYPE == *"darwin"* ]]; then
    if brew --version | grep -qw Homebrew ; then
        if ! brew list | grep -qw zeek ; then
            brew install zeek
        fi
        config="/usr/local/etc/"
        rules="/usr/local/opt/zeek/share/zeek/"
    fi
elif [ -f /etc/debian_version ]; then
    # Ubuntu
    if [[ "$TRAVIS" = true ]]; then
        if ! type zeek ; then
            echo 'deb http://download.opensuse.org/repositories/security:/zeek/xUbuntu_18.04/ /' | sudo tee /etc/apt/sources.list.d/security:zeek.list
curl -fsSL https://download.opensuse.org/repositories/security:zeek/xUbuntu_18.04/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/security:zeek.gpg > /dev/null
sudo apt update -qq
            sudo apt-get -y --allow-unauthenticated install zeek
            export PATH=/opt/zeek/bin:$PATH && export LD_LIBRARY_PATH=/opt/zeek/lib/:$LD_LIBRARY_PATH
            sudo setcap cap_net_raw,cap_net_admin=eip $( which zeek )
        fi
        sudo chown "$SERVER_USER":"$CURRENT_USER" $( which zeek )
        sudo chown -R "$SERVER_USER":"$CURRENT_USER" /opt/zeek
        sudo chmod -R 770 /opt/zeek
        sudo chmod 750 $( which zeek )
        config="/opt/zeek/etc/"
        rules="/opt/zeek/share/zeek/"
    else # Debian and ubuntu
        if ! type zeek ; then
            sudo apt update
            sudo apt install cmake make gcc g++ flex bison libpcap-dev libssl-dev python-dev swig zlib1g-dev libmagic-dev libgeoip-dev sendmail libcap2-bin wget curl ca-certificates
            wget https://www.zeek.org/downloads/zeek-"$ZEEK_VERSION".tar.gz
            tar xf zeek-"$ZEEK_VERSION".tar.gz
            ( cd zeek-"$ZEEK_VERSION" && ./configure )
            ( cd zeek-"$ZEEK_VERSION" && make -j$(nproc)  )
            ( cd zeek-"$ZEEK_VERSION" && sudo make install )
            rm zeek-"$ZEEK_VERSION".tar.gz && sudo rm -rf zeek-"$ZEEK_VERSION"
            export PATH=/usr/local/zeek/bin:$PATH && export LD_LIBRARY_PATH=/usr/local/zeek/lib/:$LD_LIBRARY_PATH
            sudo setcap cap_net_raw,cap_net_admin=eip $( which zeek )
        fi
        if ! type critical-stack-intel ; then
            curl --silent https://packagecloud.io/install/repositories/criticalstack/critical-stack-intel/script.deb.sh | sudo bash
            sudo apt-get install critical-stack-intel
        fi
        if [[ "$arg" = 'prod' ]]; then
                sudo chown "$SERVER_USER":"$CURRENT_USER" $( which zeek )
                sudo chown -R "$SERVER_USER":"$CURRENT_USER" /usr/local/zeek
                sudo chown -R "$SERVER_USER":"$CURRENT_USER" /etc/zeek
                sudo chmod -R 770 /usr/local/zeek
                sudo chmod 750 $( which zeek )
        else
                sudo chown "$CURRENT_USER" $( which zeek )
                sudo chown -R "$CURRENT_USER" /usr/local/zeek
        fi
        config="/usr/local/zeek/etc/"
        rules="/etc/zeek/"
    fi
fi

if ! type zeek ; then
    exit 1
fi

which zeek
zeek --version
which zeekctl
zeekctl --version

echo "ZEEK_BINARY = '$( which zeek )'" > "$destfull"probemanager/zeek/settings.py
echo "BROCTL_BINARY = '$( which zeekctl )'" >> "$destfull"probemanager/zeek/settings.py
echo "ZEEK_CONFIG = '$config'" >> "$destfull"probemanager/zeek/settings.py#!/usr/bin/env bash

echo '## Install zeek ##'
# Install on ProbeManager server
# Get args
arg=$1
destfull=$2

if [[ "$ZEEK_VERSION" == "" ]]; then
    ZEEK_VERSION="2.5.3"
fi
config=""
rules=""
# OSX with brew
if [[ $OSTYPE == *"darwin"* ]]; then
    if brew --version | grep -qw Homebrew ; then
        if ! brew list | grep -qw zeek ; then
            brew install zeek
        fi
        config="/usr/local/etc/"
        rules="/usr/local/opt/zeek/share/zeek/"
    fi
elif [ -f /etc/debian_version ]; then
    # Ubuntu
    if [[ "$TRAVIS" = true ]]; then
        if ! type zeek ; then
            curl -fsSL https://download.opensuse.org/repositories/security:zeek/xUbuntu_18.04/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/security:zeek.gpg > /dev/null
            echo 'deb http://download.opensuse.org/repositories/security:/zeek/xUbuntu_18.04/ /' | sudo tee /etc/apt/sources.list.d/security:zeek.list
            sudo apt-get update -qq
            sudo apt-get -y --allow-unauthenticated install zeek
            export PATH=/opt/zeek/bin:$PATH && export LD_LIBRARY_PATH=/opt/zeek/lib/:$LD_LIBRARY_PATH
            sudo setcap cap_net_raw,cap_net_admin=eip $( which zeek )
        fi
        sudo chown "$SERVER_USER":"$CURRENT_USER" $( which zeek )
        sudo chown -R "$SERVER_USER":"$CURRENT_USER" /opt/zeek
        sudo chmod -R 770 /opt/zeek
        sudo chmod 750 $( which zeek )
        config="/opt/zeek/etc/"
        rules="/opt/zeek/share/zeek/"
    else # Debian and ubuntu
        if ! type zeek ; then
            sudo apt update
            sudo apt install cmake make gcc g++ flex bison libpcap-dev libssl-dev python-dev swig zlib1g-dev libmagic-dev libgeoip-dev sendmail libcap2-bin wget curl ca-certificates
            wget https://download.zeek.org/zeek-"$ZEEK_VERSION".tar.gz
            tar xf zeek-"$ZEEK_VERSION".tar.gz
            ( cd zeek-"$ZEEK_VERSION" && ./configure )
            ( cd zeek-"$ZEEK_VERSION" && make -j$(nproc)  )
            ( cd zeek-"$ZEEK_VERSION" && sudo make install )
            rm zeek-"$ZEEK_VERSION".tar.gz && sudo rm -rf zeek-"$ZEEK_VERSION"
            export PATH=/usr/local/zeek/bin:$PATH && export LD_LIBRARY_PATH=/usr/local/zeek/lib/:$LD_LIBRARY_PATH
            sudo setcap cap_net_raw,cap_net_admin=eip $( which zeek )
        fi
        if ! type critical-stack-intel ; then
            curl --silent https://packagecloud.io/install/repositories/criticalstack/critical-stack-intel/script.deb.sh | sudo bash
            sudo apt-get install critical-stack-intel
        fi
        if [[ "$arg" = 'prod' ]]; then
                sudo chown "$SERVER_USER":"$CURRENT_USER" $( which zeek )
                sudo chown -R "$SERVER_USER":"$CURRENT_USER" /usr/local/zeek
                sudo chown -R "$SERVER_USER":"$CURRENT_USER" /etc/zeek
                sudo chmod -R 770 /usr/local/zeek
                sudo chmod 750 $( which zeek )
        else
                sudo chown "$CURRENT_USER" $( which zeek )
                sudo chown -R "$CURRENT_USER" /usr/local/zeek
        fi
        config="/usr/local/zeek/etc/"
        rules="/etc/zeek/"
    fi
fi

if ! type zeek ; then
    exit 1
fi

which zeek
zeek --version
which zeekctl
zeekctl --version

echo "ZEEK_BINARY = '$( which zeek )'" > "$destfull"probemanager/zeek/settings.py
echo "BROCTL_BINARY = '$( which zeekctl )'" >> "$destfull"probemanager/zeek/settings.py
echo "ZEEK_CONFIG = '$config'" >> "$destfull"probemanager/zeek/settings.py
echo "ZEEK_RULES = '$rules'" >> "$destfull"probemanager/zeek/settings.py
echo "ZEEK_VERSION = '$ZEEK_VERSION'" >> "$destfull"probemanager/zeek/settings.py

echo "ZEEK_RULES = '$rules'" >> "$destfull"probemanager/zeek/settings.py
echo "ZEEK_VERSION = '$ZEEK_VERSION'" >> "$destfull"probemanager/zeek/settings.py
