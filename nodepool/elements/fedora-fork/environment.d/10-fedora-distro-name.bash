export DISTRO_NAME=fedora
export DIB_RELEASE=${DIB_RELEASE:-34}
export EFI_BOOT_DIR="EFI/fedora"

# Note the filename URL has a "sub-release" in it
#  http:// ... Fedora-Cloud-Base-25-1.3.x86_64.qcow2
#                                   ^^^
# It's not exactly clear how this is generated, or how we could
# determine this programatically.  Other projects have more
# complicated regex-based scripts to find this, which we can examine
# if this becomes an issue ... see thread at [1]
#
# [1] https://lists.fedoraproject.org/archives/list/cloud@lists.fedoraproject.org/thread/2WFO2FKIGUQYRQXIR35UVJGRHF7LQENJ/
if [ -n "${DIB_FEDORA_SUBRELEASE:-}" ]; then
    echo "using DIB_FEDORA_SUBRELEASE"
elif [[ ${DIB_RELEASE} == '28' ]]; then
    export DIB_FEDORA_SUBRELEASE=1.1
elif [[ ${DIB_RELEASE} == '29' ]]; then
    export DIB_FEDORA_SUBRELEASE=1.2
elif [[ ${DIB_RELEASE} == '30' ]]; then
    export DIB_FEDORA_SUBRELEASE=1.2
elif [[ ${DIB_RELEASE} == '31' ]]; then
    export DIB_FEDORA_SUBRELEASE=1.9
elif [[ ${DIB_RELEASE} == '32' ]]; then
    export DIB_FEDORA_SUBRELEASE=1.6
elif [[ ${DIB_RELEASE} == '33' ]]; then
    export DIB_FEDORA_SUBRELEASE=1.2
elif [[ ${DIB_RELEASE} == '34' ]]; then
    export DIB_FEDORA_SUBRELEASE=1.2
else
    echo "Unsupported Fedora release"
    exit 1
fi
