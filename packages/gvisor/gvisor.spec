%global _cross_first_party 1
%global goproject github.com/google
%global gorepo gvisor
%global goimport %{goproject}/%{gorepo}

%global gover 20240610.0
%global rpmver %{gover}
%global gitrev 9437277bd1be6015d63a875d07dd2c5c137143f1

%global _dwz_low_mem_die_limit 0

Name: %{_cross_os}%{gorepo}
Version: %{rpmver}
Release: 1%{?dist}
Summary: Application Kernel for Containers
License: Apache-2.0
URL: https://gvisor.dev/
Source0: https://%{goimport}/archive/%{gitrev}.tar.gz
Source1: bundled-%{gitrev}.tar.gz
Source1000: clarify.toml

BuildRequires: git
BuildRequires: %{_cross_os}glibc-devel
Requires: %{_cross_os}containerd
Requires: %{name}(binaries)

%description
%{summary}.

%package bin
Summary: Application Kernel for Containers binaries
Provides: %{name}(binaries)
Requires: (%{_cross_os}image-feature(no-fips) and %{name})
Conflicts: (%{_cross_os}image-feature(fips) or %{name}-fips-bin)

%description bin
%{summary}.

%package fips-bin
Summary: Application Kernel for Containers binaries, FIPS edition
Provides: %{name}(binaries)
Requires: (%{_cross_os}image-feature(fips) and %{name})
Conflicts: (%{_cross_os}image-feature(no-fips) or %{name}-bin)

%description fips-bin
%{summary}.

%prep
%setup -n %{gorepo}-%{gitrev} -q
%setup -T -D -n %{gorepo}-%{gitrev} -b 1 -q
%cross_go_setup %{gorepo}-%{gitrev} %{goproject} %{goimport}

%build
%set_cross_go_flags

mkdir -p bin fips/bin
export LD_VERSION="-X version.version=%{gover}+bottlerocket"

declare -a BUILD_ARGS
BUILD_ARGS=(
  -ldflags="${GOLDFLAGS} ${LD_VERSION}"
)

export GO_VERSION="1.22.2"

go build "${BUILD_ARGS[@]}" -o bin/runsc ./runsc
gofips build "${BUILD_ARGS[@]}" -o fips/bin/runsc ./runsc

%install
install -d %{buildroot}%{_cross_bindir}
install -p -m 0755 bin/runsc %{buildroot}%{_cross_bindir}

install -d %{buildroot}%{_cross_fips_bindir}
install -p -m 0755 fips/bin/runsc %{buildroot}%{_cross_fips_bindir}

%cross_scan_attribution --clarify %{S:1000} go-vendor vendor

echo "%{goproject}/%{gorepo}" > %{buildroot}%{_cross_attribution_file}
echo "SPDX-License-Identifier: Apache-2.0 AND MIT" >> %{buildroot}%{_cross_attribution_file}

%files
%license LICENSE
%{_cross_attribution_file}
%{_cross_attribution_vendor_dir}

%files bin
%{_cross_bindir}/runsc

%files fips-bin
%{_cross_fips_bindir}/runsc

%changelog
