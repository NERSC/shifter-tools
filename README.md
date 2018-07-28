# shifter-tools
A collection of scripts for Shifter @ NERSC

## copy-shifter-libs.py

Use this script to copy linked libraries into VTune results directory.

- VTune results directory: `vtune-run0001`
- Profiled command: `/usr/local/bin/myexe` within Shifter container
- Assumes `./copy-shifter-libs.py` is in CWD

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
shifter ./copy-shifter-libs.py -d ${VTUNE_DIR} -f /usr/local/bin/myexe

# then, finalize on a login node
```

### Usage

```bash
usage: copy-shifter-libs.py [-h] [-f [FILES [FILES ...]]] [-d DESTINATION]
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
