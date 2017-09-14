#
# spec file for package raspberrypi-3-drivers
#
# Copyright (c) 2017 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

%define name_base raspberrypi-3
%define _buildshell /bin/bash

Name:           %{name_base}-drivers
Version:        0
Release:        0
Summary:        Device drivers for Raspberry Pi peripherals
License:        GPLv2
Group:          System/Kernel
Url:            
Source0:        %{name}-%{version}.tar.xz
Source1:        raspberrypi-linux.tar.xz        
BuildRequires: %kernel_module_package_buildreqs
%if 0%{?dtc_symbols}
BuildRequires:  dtc >= 1.4.3
%else
BuildRequires:  dtc >= 1.4.0
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%kernel_module_package

%description
Device drivers for Raspberry Pi peripherals

%package raspberrypi-3-dtbs
Summary:
Group:

%description %{name_base}-dtbs
Devivce tree binaries for Raspberry Pi peripherals

%prep
%setup
set -- *
mkdir source
mv "$@" source/
mkdir obj

%define src_version $(rpm -qa |grep kernel-obs-build |sed -E 's/kernel-obs-build-([0-9]+\.[0-9]+\.[0-9]+)-[0-9\.]+\.noarch/\1/g')

%build
for flavor in %flavors_to_build; do
    rm -rf obj/$flavor
    cp -r source obj/$flavor
    make -C %{kernel_source $flavor} modules M=$PWD/obj/$flavor
done

%build %{name_base}-dtbs
source=linux-%srcversion
cp $source/COPYING .
SRCDIR=`pwd`/$source
mkdir pp
PPDIR=`pwd`/pp
export DTC_FLAGS="-R 4 -p 0x1000"
%if 0%{?dtc_symbols}
DTC_FLAGS="$DTC_FLAGS -@"
%endif

cd $source/arch/arm64/boot/dts
for dts in al/*.dts allwinner/*.dts altera/*.dts amd/*.dts amlogic/*.dts apm/*.dts arm/*.dts broadcom/*.dts cavium/*.dts exynos/*.dts freescale/*.dts hisilicon/*.dts lg/*.dts marvell/*.dts mediatek/*.dts nvidia/*.dts qcom/*.dts renesas/*.dts rockchip/*.dts socionext/*.dts sprd/*.dts xilinx/*.dts zte/*.dts ; do
    target=${dts%*.dts}
    mkdir -p $PPDIR/$(dirname $target)
    cpp -x assembler-with-cpp -undef -D__DTS__ -nostdinc -I. -I$SRCDIR/include/ -I$SRCDIR/scripts/dtc/include-prefixes/ -P $target.dts -o $PPDIR/$target.dts
    dtc $DTC_FLAGS -I dts -O dtb -i ./$(dirname $target) -o $PPDIR/$target.dtb $PPDIR/$target.dts
done

%define dtbdir /boot/dtb-%kernelrelease


%install
export INSTALL_MOD_PATH=$RPM_BUILD_ROOT
export INSTALL_MOD_DIR=updates
for flavor in %flavors_to_build; do
    make -C %{kernel_source $flavor} modules_install M=$PWD/obj/$flavor
done

%install %{name_base}-dtbs
cd pp
for dts in al/*.dts allwinner/*.dts altera/*.dts amd/*.dts amlogic/*.dts apm/*.dts arm/*.dts broadcom/*.dts cavium/*.dts exynos/*.dts freescale/*.dts hisilicon/*.dts lg/*.dts marvell/*.dts mediatek/*.dts nvidia/*.dts qcom/*.dts renesas/*.dts rockchip/*.dts socionext/*.dts sprd/*.dts xilinx/*.dts zte/*.dts ; do
    target=${dts%*.dts}
    install -m 700 -d %{buildroot}%{dtbdir}/$(dirname $target)
    install -m 644 $target.dtb %{buildroot}%{dtbdir}/$(dirname $target)
%ifarch aarch64
    # HACK: work around U-Boot ignoring vendor dir
    baselink=%{dtbdir}/$(basename $target).dtb
    vendordir=$(basename $(dirname $target))
    ln -s $target.dtb %{buildroot}$baselink
    echo $baselink >> ../dtb-$vendordir.list
%endif
done
cd -


%post
%postun

%post %{name_base}-dtbs
cd /boot
# If /boot/dtb is a symlink, remove it, so that we can replace it.
[ -d dtb ] && [ -L dtb ] && rm -f dtb
# Unless /boot/dtb exists as real directory, create a symlink.
[ -d dtb ] || ln -sf dtb-%kernelrelease dtb

%files
%defattr(-,root,root)
%doc ChangeLog README COPYING

%ifarch aarch64
%files -n %{name_base}-dtbs -f %{name_base}-dtbs.list
%else
%files -n %{name_base}-dtbs
%endif
%defattr(-,root,root)
%doc COPYING
%ghost /boot/dtb
%dir %{dtbdir}
%dir %{dtbdir}/zte
%{dtbdir}/zte/*.dtb


%changelog

