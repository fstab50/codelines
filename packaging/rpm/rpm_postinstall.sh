#!/bin/bash

#
#  xlines preinstall script :  Copyright 2018-2019, Blake Huber
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  see: https://www.gnu.org/licenses/#GPL
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  contained in the program LICENSE file.
#

#
#   Script Log Output
#
#       - Can be found in the system log location
#       - typically /var/log/messages
#
#

_project='xlines'
loginfo='[INFO]'
logwarn='[WARN]'

declare -a python_packages

python_packages=(
    'setuptools'
    'distro'
)


function _pip_exec(){
    ##
    ##  Finds pip executable for python3 regardless of upgrade
    ##
    local _pip
    logger "$loginfo: Locating Python3 pip executable..."

    if [[ $(/usr/local/bin/pip3 --version 2>/dev/null | grep "python\ 3.[6-9]") ]]; then
        _pip="/usr/local/bin/pip3"
        echo "$_pip"
        logger "$loginfo: pip3 executable path found: $_pip"
        return 0

    elif [[ $(/usr/bin/pip3 --version 2>/dev/null | grep "python\ 3.[6-9]") ]]; then
        _pip="/usr/bin/pip3"
        echo "$_pip"
        logger "$loginfo: pip3 executable path found: $_pip"
        return 0

    elif [[ $(/usr/local/bin/pip --version 2>/dev/null | grep "python\ 3.[6-9]") ]]; then
        _pip="/usr/local/bin/pip"
        echo "$_pip"
        logger "$loginfo: pip3 executable path found: $_pip"
        return 0
    fi

    logger "$logwarn: failed to find pip executable path"
    return 1
}


function _python_prerequisites(){
    ##
    ##  install Python3 package dependencies
    ##
    local pip_bin="$1"

    for pkg in "${python_packages[@]}"; do
        $pip_bin install -U $pkg
    done
}


function _redhat_centos(){
    ##
    ##  determines if Redhat Enterprise Linux, Centos
    ##
    if [[ -f /etc/redhat-release ]]; then
        return 0

    elif [[ $(grep -i centos /etc/os-release) ]]; then
        return 0

    elif [[ $(grep -i redhat /etc/os-release) ]]; then
        return 0
    fi

    return 1
}


function _amazonlinux(){
    ##
    ##  determines if Amazon Linux
    ##
    if [[ $(grep -i 'amazon linux' /etc/os-release) ]] && \
         [[ $(grep 'VERSION' /etc/os-release | grep '2') ]]; then
        logger "$loginfo: Amazon Linux 2 OS environment detected."
        return 0
    fi
    return 1
}


function _fedoralinux(){
    ##
    ##  determines if Amazon Linux
    ##
    if [[ $(distro 2>&1 | head -n 1 | grep -i fedora) ]]; then
        logger "$loginfo: Fedora Linux OS environment detected."
        return 0
    fi
    return 1
}


function python_dependencies(){
    ##
    ##  Validates if deps installed (true) or not (false)
    ##
    local pip_bin="$1"

    if [[ $($pip_bin list | grep -i pygments) ]]; then
        logger "$loginfo: Current pygments install detected, skipping fresh install"
        return 0
    else
        return 1
    fi
}


function set_permissions(){
    ##
    ##  Set ownership perms on ~/.config directory
    ##
    logger "$loginfo: Set USER $USER ownership on .config directory..."

    if [ "$SUDO_USER" ]; then
        chown -R $SUDO_USER:$SUDO_USER /home/$SUDO_USER/.config
    else
        chown -R $USER:$USER /home/$USER/.config
    fi
}


# --- main --------------------------------------------------------------------


# build and update locate db
logger "$loginfo: Creating and updating local mlocate databases..."

# locate pip executable
_PIP=$(_pip_exec)

# install python dependencies
_python_prerequisites "$_PIP"

# determine os
os=$(distro 2>&1 | head -n 1 | awk '{print $2}')

case $os in
    'Amazon')
        logger "$loginfo: Amazon Linux os environment detected."

        if ! python_dependencies $_PIP; then
            logger "$loginfo: Missing Pygments library. Installing via pip3..."
            # install pygments
            $_PIP install pygments
        fi
        ;;

    'Fedora')
        logger "$loginfo: Fedora os environment detected."

        if ! python_dependencies $_PIP; then
            logger "$logwarn: Missing Pygments library. Installing via pip3..."
            # install pygments
            $_PIP install pygments
        fi
        ;;

    'Redhat' | 'CentOS')
        logger "$loginfo: Redhat LInux OS environment detected."
        ;;

    *)
        if _amazonlinux && ! python_dependencies $_PIP; then
            logger "$loginfo: Amazon Linux 2 os detected, but missing Pygments library. Installing..."
            # install pygments
            $_PIP install pygments

        elif _fedoralinux && ! python_dependencies $_PIP; then
            logger "$loginfo: Fedora os detected, but missing Pygments library. Installing..."
            # install pygments
            $_PIP install pygments

        elif _redhat_centos; then
            logger "$loginfo: Redhat LInux OS environment detected."
        fi
        ;;
esac

# generate bytecode artifacts
if which py3compile >/dev/null 2>&1; then
    logger "$loginfo: py3compile found... initating bytecode compilation"
    py3compile --package python3?-xlines
else
    logger "$loginfo: py3compile not found... skipping bytecode compilation"
fi

# return user ownership to ~/.config directory
set_permissions

# <-- end python package postinstall script -->

exit 0
