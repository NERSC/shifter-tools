#!/usr/bin/env python

import os
import re
import sys
import shutil
import argparse
import platform
import traceback
import subprocess


#------------------------------------------------------------------------------#
def resolve_paths(libs, excludes):
    """
    Ensure all paths are realpaths -- includes soft-link resolution even
    though this is typically not needed
    """
    rplibs = []
    rplinks = {}
    for lib in libs:
        skip = False
        for exclude in excludes:
            if re.search(exclude, lib) is not None:
                print("--> excluding '{}' matching regex '{}'".format(lib, exclude))
                skip = True
                break
        if skip is True:
            continue
        reallib = os.path.realpath(lib)
        rplibs.append(reallib)
        if reallib != lib:
            lname = os.path.basename(lib)
            ltarget = os.path.basename(reallib)
            rplinks[ltarget] = lname

    return rplibs, rplinks


#------------------------------------------------------------------------------#
def getlib(line, idx):
    lib = None

    # check at the preferred index
    if len(line) > idx and os.path.exists(line[idx]):
        lib = line[idx]
    else:
        # loop over line and try to find the library
        for col in line:
            if os.path.exists(col):
                if os.path.isfile(col) or os.path.islink(col):
                    lib = col
                    break

    if lib is None:
        if len(line) == 2 and "linux-vdso" in line[0]:
            return None
        elif line == ["statically", "linked"]:
            return None
        print("Warning! Failure to determine target in line: {}".format(line))

    return lib


#------------------------------------------------------------------------------#
def decode(variable):
    if isinstance(variable, list):
        l = []
        for var in variable:
            l.append(var.decode("utf-8").strip())
        return l
    else:
        return variable.decode("utf-8").strip()


#------------------------------------------------------------------------------#
def otool(files):
    """
    Run `otool -L <filename>`
    """
    libs = []
    for x in files:
        f = os.path.realpath(x)
        p = subprocess.Popen(["otool", "-L", f],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        result = decode(p.stdout.readlines())
        # pop first line because this just specifies the file on macOS
        result.pop(0)

        for l in result:
            if len(l) == 0:
                continue
            s = l.split()
            lib = None
            if "=>" in l:
                # len(s) == 3 is virtual library
                #   e.g. libXYZ => (0x5334534)
                if len(s) != 3:
                    lib = getlib(s, 2)
            else:
                lib = getlib(s, 0)

            # if the library was found
            if lib is not None:
                libs.append(lib)

    return libs

#------------------------------------------------------------------------------#
def ldd(files):
    """
    Run `ldd <filename>`
    """
    libs = []
    for x in files:
        f = os.path.realpath(x)
        p = subprocess.Popen(["ldd", f],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        result = decode(p.stdout.readlines())

        for l in result:
            if len(l) == 0:
                continue
            s = l.split()
            lib = None
            if "=>" in l:
                # len(s) == 3 is virtual library
                #   e.g. libXYZ => (0x5334534)
                if len(s) != 3:
                    lib = getlib(s, 2)
            else:
                lib = getlib(s, 0)

            # if the library was found
            if lib is not None:
                libs.append(lib)

    return libs


#------------------------------------------------------------------------------#
def copyfile(fsrc, fdir):
    """
    Copy a file to a directory
    """
    if not os.path.exists(fdir):
        os.makedirs(fdir)

    fdst = os.path.join(fdir, os.path.basename(fsrc))
    if os.path.exists(fsrc):
        shutil.copyfile(fsrc, fdst)
        shutil.copymode(fsrc, fdst)


#------------------------------------------------------------------------------#
def main(args):

    libs = []
    files = args.files

    #--------------------------------------------------------------------------#
    def run(filenames):
        if platform.system() == "Darwin":
            tmp = otool(filenames)
        else:
            tmp = ldd(filenames)
        return tmp
    #--------------------------------------------------------------------------#
    def printlist(title, l):
        print("")
        print("{}:".format(title))
        for x in l:
            print("\t{}".format(x))
        print("")
    #--------------------------------------------------------------------------#

    depth = 0
    while True:
        tmp = list(set(run(files)))

        if len(libs) > 0:
            tmp.extend(libs)
        tmp = sorted(list(set(tmp)))
        files = tmp

        if libs == tmp:
            break
        else:
            libs.extend(tmp)
            libs = sorted(list(set(libs)))
            if not args.recursive:
                break
            else:
                if args.max_depth > 0 and depth == args.max_depth:
                    print("\nReach max recursive depth of {}...".format(depth))
                    break
        depth += 1

    libs, links = resolve_paths(libs, args.exclude)

    printlist("Libraries copied to {}".format(args.destination), libs)

    for lib in libs:
        copyfile(lib, args.destination)

    for lsrc, ltarget in links.items():
        ldst = os.path.join(args.destination, ltarget)
        if not os.path.exists(ldst):
            os.symlink(lsrc, ldst)


#------------------------------------------------------------------------------#
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--files",
                        nargs="*",
                        type=str,
                        help="Get linked targets for this list of files")
    parser.add_argument("-d", "--destination",
                        type=str,
                        help="Destination directory (default: '%(default)s')",
                        default=os.getcwd())
    parser.add_argument("-r", "--recursive",
                        help=("Recursive ldd/otool resolution"),
                        action="store_true")
    parser.add_argument("--max-depth",
                        type=int,
                        help="Max recursive depth (default: %(default)s == unlimited)",
                        default=0)
    parser.add_argument("-e", "--exclude",
                        nargs="*",
                        type=str,
                        help=("List of regex expressions to exclude from copy using 're.search(<str>, <path>)' "
                              "(default: %(default)s), e.g. '^/usr/lib[6]?[4]?/lib.*\.so\.[0-9]$'"),
                        default=[])

    args = parser.parse_args()

    try:

        main(args)

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=5)
        print ('Exception - {}'.format(e))
        sys.exit(1)

    sys.exit(0)
