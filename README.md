# ist.rc.caixote
A Python implementation of a Dropbox-like user folder file synchronization.

### Project Infos
* **Date:** Semester 1 - 2016/2017 (Nov 2016)
* **Topic:** Dropbox-like file synchronization
* **Course:** Redes de Computadores (RC) | Computer Networks
* **Course Link:** https://fenix.tecnico.ulisboa.pt/disciplinas/RC9179/2016-2017/1-semestre

### Usage

## Requirements
* Python3
* Bash
* Port/File R/W permissions

#### Server
```shell
cd server
python3 Server.py PORT
```

#### Caixote (Client)
```
python3 Caixote.py HOST PORT USERNAME FOLDERNAME
```

Or connect using `telnet` or `netcat` with `HOST PORT`


### Disclaimer
This repository, and every other `ist.COURSE.*` repos on GitHub correspond to school projects from the respective *COURSE*. The code on this repo is intended for educational purposes. I do not take any responsibility, liability or whateverity over any code faults, inconsistency or anything else. If you intend on copying most or parts of the code for your school projects, keep in mind that this repo is public, and that your professor might search the web for similar project solutions or whatnot and choose to fail you for copying.
