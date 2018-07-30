# shifter-tools
A collection of scripts for Shifter @ NERSC

## shiftercp

This script takes one or more executables or libraries (-f flag), determines the libraries
 that are linked to the file, and copies those libraries into a specified directory (-d flag).
This directory should be the VTune results directory. By copying the libraries
into this directory, VTune can finalize the results outside of a Shifter container.
If the recursive flag (-r) is provided, this script will find and copy the
implicitly linked libraries.

### Usage Flags

- `-f` : executable or library [required]
    - Accepts 1 or more arguments
- `-d` : output directory [optional]
    - Accepts only one arguments
    - Default: current working directory
- `-r` : enable recursion [optional]
    - Accepts zero arguments
    - Enables copying of implicitly linked libraries
    - `myexe` links to libfoo.so
    - libfoo.so links to libbar.so
    - Within recursion enabled, `shiftercp.py` will copy libbar.so into the output directory
- `--max-depth=<N>` : limits the depth of recursion [optional]
    - Accepts one integer argument
    - Default: `0`
    - `N == 0` means unlimited, all implicitly linked libraries will be found and copied
    - Only used in conjunction with `-r` flag
    - Example:
        - `myexe` links to libfoo.so
        - libfoo.so links to libbar.so (level 1)
        - libbar.so links to librt.so (level 2)
        - librt.so links to libdc.so (level 3)
        - if `N == 0`, all above libraries will be copied to output directory
        - if `N == 1`, libfoo.so and libbar.so will be copied to output directory
        - if `N == 2`, libfoo.so, libbar.so, and librt.so will be copied to output directory
- `-e` : regex string [optional]
    - Accepts one or more strings
    - Disabled copying libraries that match the regex string
    - See [Python re documentation](https://docs.python.org/3/library/re.html) for Regex information
    - Uses `re.search(..., <library-name>)`
- `--copy-files` : copy the list of files (e.g. `-f` parameters) to output directory [optional]
    - Accepts zero arguments
    - The list of files provided by `-f` flag will also be copied to output directory


### SLURM Example

- VTune results directory: `vtune-run0001`
- Profiled command: `/usr/local/bin/myexe` within Shifter container
- Assumes `./shiftercp.py` is in CWD

```bash
#!/bin/bash

#SBATCH --qos=debug
#SBATCH -N 1
#SBATCH -t 00:30:00
#SBATCH --image=<username/some-image>
# ... additional sbatch parameters ...

module load vtune

PID_FILE=$(mktemp pid.XXXXXXX)
VTUNE_DIR=${PWD}/vtune-run0001

# run command in shifter, submit to background
shifter /usr/local/bin/myexe & echo $! &> ${PID_FILE}

# attach VTune to process, defer finalization
amplxe-cl -collect <collection-mode> -finalization-mode deferred -r ${VTUNE_DIR} --target-pid=$(cat ${PID_FILE}) ...

# use script to copy libraries linked to myexe into ${VTUNE_DIR}
shifter ./shiftercp.py -d ${VTUNE_DIR} -f /usr/local/bin/myexe

# then, finalize on a login node
```

### Usage

```bash
usage: shiftercp.py [-h] [-f [FILES [FILES ...]]] [-d DESTINATION]
                            [-r] [--max-depth MAX_DEPTH]
                            [-e [EXCLUDE [EXCLUDE ...]]]

optional arguments:
  -h, --help            show this help message and exit
  -f [FILES [FILES ...]], --files [FILES [FILES ...]]
                        Get linked targets for this list of files
  -d DESTINATION, --destination DESTINATION
                        Destination directory (default:
                        '${PWD}')
  -r, --recursive       Recursive ldd/otool resolution
  --max-depth MAX_DEPTH
                        Max recursive depth (default: 0 == unlimited)
  -e [EXCLUDE [EXCLUDE ...]], --exclude [EXCLUDE [EXCLUDE ...]]
                        List of regex expressions to exclude from copy using
                        're.search(<str>, <path>)' (default: []), e.g.
                        '^/usr/lib[6]?[4]?/lib.*\.so\.[0-9]$'
```

### Example

```bash
$ ./shiftercp.py -r -d example -f $(which python)

Libraries copied to example:
    /System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation
    /opt/local/Library/Frameworks/Python.framework/Versions/3.6/Python
    /opt/local/lib/libiconv.2.dylib
    /opt/local/lib/libintl.8.dylib
    /usr/lib/closure/libclosured.dylib
    /usr/lib/libDiagnosticMessagesClient.dylib
    /usr/lib/libSystem.B.dylib
    /usr/lib/libc++.1.dylib
    /usr/lib/libc++abi.dylib
    /usr/lib/libicucore.A.dylib
    /usr/lib/libobjc.A.dylib
    /usr/lib/libz.1.dylib
    /usr/lib/system/libcache.dylib
    /usr/lib/system/libcommonCrypto.dylib
    /usr/lib/system/libcompiler_rt.dylib
    /usr/lib/system/libcopyfile.dylib
    /usr/lib/system/libcorecrypto.dylib
    /usr/lib/system/libdispatch.dylib
    /usr/lib/system/libdyld.dylib
    /usr/lib/system/libkeymgr.dylib
    /usr/lib/system/liblaunch.dylib
    /usr/lib/system/libmacho.dylib
    /usr/lib/system/libquarantine.dylib
    /usr/lib/system/libremovefile.dylib
    /usr/lib/system/libsystem_asl.dylib
    /usr/lib/system/libsystem_blocks.dylib
    /usr/lib/system/libsystem_c.dylib
    /usr/lib/system/libsystem_configuration.dylib
    /usr/lib/system/libsystem_coreservices.dylib
    /usr/lib/system/libsystem_darwin.dylib
    /usr/lib/system/libsystem_dnssd.dylib
    /usr/lib/system/libsystem_info.dylib
    /usr/lib/system/libsystem_kernel.dylib
    /usr/lib/system/libsystem_m.dylib
    /usr/lib/system/libsystem_malloc.dylib
    /usr/lib/system/libsystem_network.dylib
    /usr/lib/system/libsystem_networkextension.dylib
    /usr/lib/system/libsystem_notify.dylib
    /usr/lib/system/libsystem_platform.dylib
    /usr/lib/system/libsystem_pthread.dylib
    /usr/lib/system/libsystem_sandbox.dylib
    /usr/lib/system/libsystem_secinit.dylib
    /usr/lib/system/libsystem_symptoms.dylib
    /usr/lib/system/libsystem_trace.dylib
    /usr/lib/system/libunwind.dylib
    /usr/lib/system/libxpc.dylib

$ ls example/
CoreFoundation                    libcommonCrypto.dylib             libintl.8.dylib
libsystem_blocks.dylib            libsystem_m.dylib                 libsystem_secinit.dylib
Python                            libcompiler_rt.dylib              libkeymgr.dylib
libsystem_c.dylib                 libsystem_malloc.dylib            libsystem_symptoms.dylib
libDiagnosticMessagesClient.dylib libcopyfile.dylib                 liblaunch.dylib
libsystem_configuration.dylib     libsystem_network.dylib           libsystem_trace.dylib
libSystem.B.dylib                 libcorecrypto.dylib               libmacho.dylib
libsystem_coreservices.dylib      libsystem_networkextension.dylib  libunwind.dylib
libc++.1.dylib                    libdispatch.dylib                 libobjc.A.dylib
libsystem_darwin.dylib            libsystem_notify.dylib            libxpc.dylib
libc++abi.dylib                   libdyld.dylib                     libquarantine.dylib
libsystem_dnssd.dylib             libsystem_platform.dylib          libz.1.dylib
libcache.dylib                    libiconv.2.dylib                  libremovefile.dylib
libsystem_info.dylib              libsystem_pthread.dylib           libclosured.dylib
libicucore.A.dylib                libsystem_asl.dylib               libsystem_kernel.dylib
libsystem_sandbox.dylib
```
