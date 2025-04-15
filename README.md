EGG Library
[![Discord Badge]][discord]
=============

[Discord Badge]: https://img.shields.io/discord/727908905392275526?color=%237289DA&logo=discord&logoColor=%23FFFFFF
[discord]: https://discord.gg/hKx3FJJgrV

A work-in-progress decompilation of the EGG library.

This repository does **not** contain any game assets or assembly whatsoever. An existing copy of any of the supported games is required.

The goal of this repository is to provide one set of source files supporting all games and applications linking the EGG library.

Supported versions:

- `R64E01`: Wii Music (USA)
- `RFNE01`: Wii Fit (USA, Rev 1)
- `RFPE01`: Wii Fit Plus (USA)
- `RHAE01`: Wii Play (USA, Rev 1)
- `RMCP01`: Mario Kart Wii (PAL)
- `RSPE01`: Wii Sports (USA, Rev 1)
- `RUUE01`: Animal Crossing: City Folk (USA, Rev 0)
- `RYWE01`: Big Brain Academy: Wii Degree (USA)
- `RZTE01`: Wii Sports Resort (USA, Rev 1)
- `SMNP01`: New Super Mario Bros. Wii (PAL, Rev 1)
- `SOUE01`: The Legend of Zelda: Skyward Sword (USA, Rev 0)

Dependencies
============

Windows
--------

On Windows, it's **highly recommended** to use native tooling. WSL or msys2 are **not** required.  
When running under WSL, [objdiff](#diffing) is unable to get filesystem notifications for automatic rebuilds.

- Install [Python](https://www.python.org/downloads/) and add it to `%PATH%`.
  - Also available from the [Windows Store](https://apps.microsoft.com/store/detail/python-311/9NRWMJP3717K).
- Download [ninja](https://github.com/ninja-build/ninja/releases) and add it to `%PATH%`.
  - Quick install via pip: `pip install ninja`

macOS
------

- Install [ninja](https://github.com/ninja-build/ninja/wiki/Pre-built-Ninja-packages):

  ```sh
  brew install ninja
  ```

- Install [wine-crossover](https://github.com/Gcenx/homebrew-wine):

  ```sh
  brew install --cask --no-quarantine gcenx/wine/wine-crossover
  ```

After OS upgrades, if macOS complains about `Wine Crossover.app` being unverified, you can unquarantine it using:

```sh
sudo xattr -rd com.apple.quarantine '/Applications/Wine Crossover.app'
```

Linux
------

- Install [ninja](https://github.com/ninja-build/ninja/wiki/Pre-built-Ninja-packages).
- For non-x86(_64) platforms: Install wine from your package manager.
  - For x86(_64), [wibo](https://github.com/decompals/wibo), a minimal 32-bit Windows binary wrapper, will be automatically downloaded and used.

Building
========

- Clone the repository:

  ```sh
  git clone https://github.com/vabold/EGG.git
  ```

- Copy the target's disc image to `orig/GAMEID`.
  - Supported formats: ISO (GCM), RVZ, WIA, WBFS, CISO, NFS, GCZ, TGC
  - After the initial build, the disc image can be deleted to save space.

- Configure:

  ```sh
  python configure.py
  ```

  To use a version other than `RYWE01`, specify it with `--version`.

- Build:

  ```sh
  ninja
  ```

Diffing
=======

Once the initial build succeeds, an `objdiff.json` should exist in the project root.

Download the latest release from [encounter/objdiff](https://github.com/encounter/objdiff). Under project settings, set `Project directory`. The configuration should be loaded automatically.

Select an object from the left sidebar to begin diffing. Changes to the project will rebuild automatically: changes to source files, headers, `configure.py`, `splits.txt` or `symbols.txt`.
