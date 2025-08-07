#!/bin/sh

# This script installs the Nix package manager on your system by
# downloading a binary distribution and running its installer script
# (which in turn creates and populates /nix).

{ # Prevent execution if this script was only partially downloaded
oops() {
    echo "$0:" "$@" >&2
    exit 1
}

umask 0022

tmpDir="$(mktemp -d -t nix-binary-tarball-unpack.XXXXXXXXXX || \
          oops "Can't create temporary directory for downloading the Nix binary tarball")"
cleanup() {
    rm -rf "$tmpDir"
}
trap cleanup EXIT INT QUIT TERM

require_util() {
    command -v "$1" > /dev/null 2>&1 ||
        oops "you do not have '$1' installed, which I need to $2"
}

case "$(uname -s).$(uname -m)" in
    Linux.x86_64)
        hash=a53ceb24793488510f67baaed59dc7c049af6d3c7683cd7760274f7a1bec7b2a
        path=zcwli8rfk09f5686jmgbqim9girqcrlx/nix-2.30.2-x86_64-linux.tar.xz
        system=x86_64-linux
        ;;
    Linux.i?86)
        hash=e9eabb071f425bd192353ce5ab630db5068844e606835bc5e422c68b0abded14
        path=zzj1sl8j8mg8zsai1vz9y69r1fxghxin/nix-2.30.2-i686-linux.tar.xz
        system=i686-linux
        ;;
    Linux.aarch64)
        hash=b9c5d93dfce77ac2c9727bcdd8791fc8f2529f56b22f71f0644671929ac03fe2
        path=1v3fwjka9fxxnwf8bhcai1a10nqjr33a/nix-2.30.2-aarch64-linux.tar.xz
        system=aarch64-linux
        ;;
    Linux.armv6l)
        hash=1dd8d452451915d0d525b3d8980d674088d4b8bbf5b56f293bfb295530581e49
        path=4xkqs1nn5fj8n0gzkh8nijzrchn6xv00/nix-2.30.2-armv6l-linux.tar.xz
        system=armv6l-linux
        ;;
    Linux.armv7l)
        hash=4681ad3cdbb7c5f0225cc2161f9727f33e4b0d44b50a375c6b83c67b4ee7d3d2
        path=5zv2mnvjqi53dxyi258jhfh2pfk4ibq3/nix-2.30.2-armv7l-linux.tar.xz
        system=armv7l-linux
        ;;
    Linux.riscv64)
        hash=cb87cdae66abd4ab8c6d5a43557602d699f31bed0202dc3af1a763ce892c5da5
        path=mry6gr17lda66mi10rqhqpvh8fip1kcr/nix-2.30.2-riscv64-linux.tar.xz
        system=riscv64-linux
        ;;
    Darwin.x86_64)
        hash=4628d6af18b5130ef5c47e6e1993f1a78897bcd9c8ad194a9b3b2f93eab49fbb
        path=yff6s23srra1s637cvw40sjwa093y0kp/nix-2.30.2-x86_64-darwin.tar.xz
        system=x86_64-darwin
        ;;
    Darwin.arm64|Darwin.aarch64)
        hash=fc4ded27d4403deab9da7fadc64887bae8b4ea2194f107f448d37d8ec130415f
        path=0qly8s1jhsnxvr9jm9pmrhns4cg8a69g/nix-2.30.2-aarch64-darwin.tar.xz
        system=aarch64-darwin
        ;;
    *) oops "sorry, there is no binary distribution of Nix for your platform";;
esac

# Use this command-line option to fetch the tarballs using nar-serve or Cachix
if [ "${1:-}" = "--tarball-url-prefix" ]; then
    if [ -z "${2:-}" ]; then
        oops "missing argument for --tarball-url-prefix"
    fi
    url=${2}/${path}
    shift 2
else
    url=https://releases.nixos.org/nix/nix-2.30.2/nix-2.30.2-$system.tar.xz
fi

tarball=$tmpDir/nix-2.30.2-$system.tar.xz

require_util tar "unpack the binary tarball"
if [ "$(uname -s)" != "Darwin" ]; then
    require_util xz "unpack the binary tarball"
fi

if command -v curl > /dev/null 2>&1; then
    fetch() { curl --fail -L "$1" -o "$2"; }
elif command -v wget > /dev/null 2>&1; then
    fetch() { wget "$1" -O "$2"; }
else
    oops "you don't have wget or curl installed, which I need to download the binary tarball"
fi

echo "downloading Nix 2.30.2 binary tarball for $system from '$url' to '$tmpDir'..."
fetch "$url" "$tarball" || oops "failed to download '$url'"

if command -v sha256sum > /dev/null 2>&1; then
    hash2="$(sha256sum -b "$tarball" | cut -c1-64)"
elif command -v shasum > /dev/null 2>&1; then
    hash2="$(shasum -a 256 -b "$tarball" | cut -c1-64)"
elif command -v openssl > /dev/null 2>&1; then
    hash2="$(openssl dgst -r -sha256 "$tarball" | cut -c1-64)"
else
    oops "cannot verify the SHA-256 hash of '$url'; you need one of 'shasum', 'sha256sum', or 'openssl'"
fi

if [ "$hash" != "$hash2" ]; then
    oops "SHA-256 hash mismatch in '$url'; expected $hash, got $hash2"
fi

unpack=$tmpDir/unpack
mkdir -p "$unpack"
tar -xJf "$tarball" -C "$unpack" || oops "failed to unpack '$url'"

script=$(echo "$unpack"/*/install)

[ -e "$script" ] || oops "installation script is missing from the binary tarball!"
export INVOKED_FROM_INSTALL_IN=1
"$script" "$@"

} # End of wrapping