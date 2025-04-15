#!/usr/bin/env python3

###
# Generates build files for the project.
# This file also includes the project configuration,
# such as compiler flags and the object matching status.
#
# Usage:
#   python3 configure.py
#   ninja
#
# Append --help to see available options.
###

import argparse
import sys
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List

from tools.project import (
    Object,
    ProgressCategory,
    ProjectConfig,
    calculate_progress,
    generate_build,
    is_windows,
)

# Game versions
DEFAULT_VERSION = 2  # BBA: WD has a debug linker map - target that primarily
VERSIONS = [
    "RSPE01",  # Wii Sports (USA, Rev 1)
    "RHAE01",  # Wii Play (USA, Rev 1)
    "RYWE01",  # Big Brain Academy: Wii Degree (USA)
    "RMCP01",  # Mario Kart Wii (PAL)
    "RFNE01",  # Wii Fit (USA, Rev 1)
    "R64E01",  # Wii Music (USA)
    "RUUE01",  # Animal Crossing: City Folk (USA, Rev 0)
    "R9IE01",  # Pikmin (USA)
    "RFPE01",  # Wii Fit Plus (USA)
    "SMNP01",  # New Super Mario Bros. Wii (PAL, Rev 1)
    "RZTE01",  # Wii Sports Resort (USA, Rev 1)
    "SOUE01",  # The Legend of Zelda: Skyward Sword (USA, Rev 0)
]


class EGGApp(IntEnum):
    OGWS = VERSIONS.index("RSPE01")
    WP = VERSIONS.index("RHAE01")
    BBA_WD = VERSIONS.index("RYWE01")
    MKW = VERSIONS.index("RMCP01")
    WF = VERSIONS.index("RFNE01")
    WM = VERSIONS.index("R64E01")
    AC_CF = VERSIONS.index("RUUE01")
    PIKMIN1 = VERSIONS.index("R9IE01")
    WFP = VERSIONS.index("RFPE01")
    NSMBW = VERSIONS.index("SMNP01")
    WSR = VERSIONS.index("RZTE01")
    LOZ_SS = VERSIONS.index("SOUE01")


# Specifies year/month for EGG_VERSION per game
def get_build_version_number(version_num: int) -> str:
    match version_num:
        case EGGApp.OGWS:
            return "200611L"
        case EGGApp.WP:
            return "200702L"
        case EGGApp.BBA_WD:
            return "200704L"
        case EGGApp.MKW:
            return "200804L"
        case EGGApp.WF:
            return "200805L"
        case EGGApp.WM:
            return "200810L"
        case EGGApp.AC_CF:
            return "200811L"
        case EGGApp.PIKMIN1:
            return "200903L"
        case EGGApp.WFP:
            return "200910L"
        case EGGApp.NSMBW:
            return "200911L"
        case EGGApp.WSR:
            return "201006L"
        case EGGApp.LOZ_SS:
            return "201111L"
        case _:
            raise ValueError("Version number must correspond to EGGApp entry")


# Specifies linker version per game
def get_config_linker_version(version_num: int) -> str:
    match version_num:
        # AC_CF and WF's linker version isn't known. Guess based on build strings
        case EGGApp.OGWS | EGGApp.WP | EGGApp.BBA_WD | EGGApp.WF | EGGApp.AC_CF | EGGApp.PIKMIN1:
            return "GC/3.0a5.2"
        case EGGApp.MKW:
            return "Wii/0x4201_127"
        case EGGApp.WM | EGGApp.WFP | EGGApp.NSMBW | EGGApp.WSR:
            return "Wii/1.1"
        case EGGApp.LOZ_SS:
            return "Wii/1.5"
        case _:
            raise ValueError("Version number must correspond to EGGApp entry")


# Specifies compiler flags per game
def get_egg_compiler_flags(version_num: int) -> List[str]:
    base_flags = [
        "-nodefaults",
        "-proc gekko",
        "-align powerpc",
        "-enum int",
        "-fp hardware",
        "-Cpp_exceptions off",
        # "-W all",
        "-O4,p",
        "-inline auto",
        '-pragma "cats off"',
        '-pragma "warn_notinlined off"',
        "-maxerrors 1",
        "-nosyspath",
        "-RTTI off",
        "-fp_contract on",
        "-str reuse",
        "-enc SJIS",
        "-i include",
        f"-i build/{config.version}/include",
        f"-DEGG_VERSION={get_build_version_number(version_num)}",
        f"-DVERSION_{config.version}",
    ]

    match version_num:
        case (
            EGGApp.OGWS
            | EGGApp.WP
            | EGGApp.BBA_WD
            | EGGApp.WF
            | EGGApp.WM
            | EGGApp.PIKMIN1
            | EGGApp.WFP
            | EGGApp.NSMBW
            | EGGApp.WSR
            | EGGApp.LOZ_SS
        ):
            return [
                *base_flags,
            ]
        case EGGApp.MKW:
            return [*base_flags, "-func_align=4"]
        case EGGApp.AC_CF:
            return [
                *base_flags,
                "-RTTI on",
            ]
        case _:
            raise ValueError("Version number must correspond to EGGApp entry")


parser = argparse.ArgumentParser()
parser.add_argument(
    "mode",
    choices=["configure", "progress"],
    default="configure",
    help="script mode (default: configure)",
    nargs="?",
)
parser.add_argument(
    "-v",
    "--version",
    choices=VERSIONS,
    type=str.upper,
    default=VERSIONS[DEFAULT_VERSION],
    help="version to build",
)
parser.add_argument(
    "--build-dir",
    metavar="DIR",
    type=Path,
    default=Path("build"),
    help="base build directory (default: build)",
)
parser.add_argument(
    "--binutils",
    metavar="BINARY",
    type=Path,
    help="path to binutils (optional)",
)
parser.add_argument(
    "--compilers",
    metavar="DIR",
    type=Path,
    help="path to compilers (optional)",
)
parser.add_argument(
    "--map",
    action="store_true",
    help="generate map file(s)",
)
parser.add_argument(
    "--debug",
    action="store_true",
    help="build with debug info (non-matching)",
)
if not is_windows():
    parser.add_argument(
        "--wrapper",
        metavar="BINARY",
        type=Path,
        help="path to wibo or wine (optional)",
    )
parser.add_argument(
    "--dtk",
    metavar="BINARY | DIR",
    type=Path,
    help="path to decomp-toolkit binary or source (optional)",
)
parser.add_argument(
    "--objdiff",
    metavar="BINARY | DIR",
    type=Path,
    help="path to objdiff-cli binary or source (optional)",
)
parser.add_argument(
    "--sjiswrap",
    metavar="EXE",
    type=Path,
    help="path to sjiswrap.exe (optional)",
)
parser.add_argument(
    "--verbose",
    action="store_true",
    help="print verbose output",
)
parser.add_argument(
    "--non-matching",
    dest="non_matching",
    action="store_true",
    help="builds equivalent (but non-matching) or modded objects",
)
parser.add_argument(
    "--no-progress",
    dest="progress",
    action="store_false",
    help="disable progress calculation",
)
args = parser.parse_args()

config = ProjectConfig()
config.version = str(args.version)
version_num = VERSIONS.index(config.version)

# Apply arguments
config.build_dir = args.build_dir
config.dtk_path = args.dtk
config.objdiff_path = args.objdiff
config.binutils_path = args.binutils
config.compilers_path = args.compilers
config.generate_map = args.map
config.non_matching = args.non_matching
config.sjiswrap_path = args.sjiswrap
config.progress = args.progress
if not is_windows():
    config.wrapper = args.wrapper
# Don't build asm unless we're --non-matching
if not config.non_matching:
    config.asm_dir = None

# Tool versions
config.binutils_tag = "2.42-1"
config.compilers_tag = "20240706"
config.dtk_tag = "v1.3.0"
config.objdiff_tag = "v2.4.0"
config.sjiswrap_tag = "v1.2.0"
config.wibo_tag = "0.6.11"

# Project
config.config_path = Path("config") / config.version / "config.yml"
config.check_sha_path = Path("config") / config.version / "build.sha1"
config.asflags = [
    "-mgekko",
    "--strip-local-absolute",
    "-I include",
    f"-I build/{config.version}/include",
    f"--defsym BUILD_VERSION={version_num}",
    f"--defsym VERSION_{config.version}",
]
config.ldflags = [
    "-fp hardware",
    "-nodefaults",
]
if args.debug:
    config.ldflags.append("-gdwarf-2")
if args.map:
    config.ldflags.append("-listclosure")

# Use for any additional files that should cause a re-configure when modified
config.reconfig_deps = []

# Optional numeric ID for decomp.me preset
# Can be overridden in libraries or objects
config.scratch_preset_id = None

# Base flags, common to most GC/Wii games.
# Generally leave untouched, with overrides added below.
cflags_base = [
    "-nodefaults",
    "-proc gekko",
    "-align powerpc",
    "-enum int",
    "-fp hardware",
    "-Cpp_exceptions off",
    # "-W all",
    "-O4,p",
    "-inline auto",
    '-pragma "cats off"',
    '-pragma "warn_notinlined off"',
    "-maxerrors 1",
    "-nosyspath",
    "-RTTI off",
    "-fp_contract on",
    "-str reuse",
    "-enc SJIS",
    "-i include",
    f"-i build/{config.version}/include",
    f"-DVERSION_{config.version}",
]

# Debug flags
if args.debug:
    # Or -sym dwarf-2 for Wii compilers
    cflags_base.extend(["-sym on", "-DDEBUG=1"])
else:
    cflags_base.append("-DNDEBUG=1")

# Metrowerks library flags
cflags_runtime = [
    *cflags_base,
    "-use_lmw_stmw on",
    "-str reuse,pool,readonly",
    "-gccinc",
    "-common off",
    "-inline auto",
]

# REL flags
cflags_rel = [
    *cflags_base,
    "-sdata 0",
    "-sdata2 0",
]

config.linker_version = get_config_linker_version(version_num)


# Helper function for Dolphin libraries
def DolphinLib(lib_name: str, objects: List[Object]) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "mw_version": "GC/1.2.5n",
        "cflags": cflags_base,
        "progress_category": "sdk",
        "objects": objects,
    }


# Helper function for REL script objects
def Rel(lib_name: str, objects: List[Object]) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "mw_version": "GC/1.3.2",
        "cflags": cflags_rel,
        "progress_category": "game",
        "objects": objects,
    }


Matching = True  # Object matches and should be linked
NonMatching = False  # Object does not match and should not be linked
Equivalent = (
    config.non_matching
)  # Object should be linked when configured with --non-matching


# Object is only matching for specific versions
def MatchingFor(*versions):
    return config.version in versions


config.warn_missing_config = True
config.warn_missing_source = False
config.libs = [
    {
        "lib": "Runtime.PPCEABI.H",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "sdk",  # str | List[str]
        "objects": [
            Object(NonMatching, "Runtime.PPCEABI.H/global_destructor_chain.c"),
            Object(NonMatching, "Runtime.PPCEABI.H/__init_cpp_exceptions.cpp"),
        ],
    },
    {
        "lib": "EGG",
        "mw_version": config.linker_version,
        "cflags": get_egg_compiler_flags(version_num),
        "progress_category": "egg",
        "objects": [
            Object(Matching, "egg/core/eggDisposer.cpp"),
        ],
    },
]


# Optional callback to adjust link order. This can be used to add, remove, or reorder objects.
# This is called once per module, with the module ID and the current link order.
#
# For example, this adds "dummy.c" to the end of the DOL link order if configured with --non-matching.
# "dummy.c" *must* be configured as a Matching (or Equivalent) object in order to be linked.
def link_order_callback(module_id: int, objects: List[str]) -> List[str]:
    # Don't modify the link order for matching builds
    if not config.non_matching:
        return objects
    if module_id == 0:  # DOL
        return objects + ["dummy.c"]
    return objects


# Uncomment to enable the link order callback.
# config.link_order_callback = link_order_callback


# Optional extra categories for progress tracking
# Adjust as desired for your project
config.progress_categories = [
    ProgressCategory("egg", "EGG Library Code"),
    ProgressCategory("sdk", "SDK Code"),
]
config.progress_each_module = args.verbose

if args.mode == "configure":
    # Write build.ninja and objdiff.json
    generate_build(config)
elif args.mode == "progress":
    # Print progress and write progress.json
    calculate_progress(config)
else:
    sys.exit("Unknown mode: " + args.mode)
