# Gopyxl

## Setup
Use of this package requires an installation of [Goma](https://github.com/goma/goma) (see link for details).

Then, install the dependencies with pip (Python 3.7+):

```shell
$ pip install -r requirements.txt
``` 

A lid-driven cavity example is included in this repo for reference on formatting the Excel (.xlsx) template.  To generate the Goma input file, run `python goxlsx_reader_v2.py path/to/xlsx/template`.

To run Goma using the interactive CLI wrapper, run `python goma_wrapper.py path/to/input/file`


## Background

Gopyxl is a suite of Python tools to create an Excel and interactive CLI interface for the multi-phase, multi-physics Finite Element Method (FEM) software package, [Goma](https://github.com/goma/goma), developed at Sandia National Laboratory.  Many parameters must be set correctly for a FEM problem to be well-defined; in Goma, these parameters are specified in an input file, mesh file, and other locations.  Gopyxl assists the user in keeping all parameters relevant to a project in an Excel template, which contain data validation fields (dropdown boxes) to assist the user specifying various parameters.  `goxlsx_reader.py` reads the Excel template and generates the input file Goma will actually use.

Then, `goma_wrapper.py` is an interactive wrapper around Goma using Python's pexpect.  The user is able to run their input file and perform other tasks interactively, such as:

- Add runtime flags for the solver
- Load a "guess file" (an initial guess based on a previously saved solution)
- Saved converged or intermediate solutions

Solutions are saved in unique directories that specify the datetime when it was created.  Copies of all input files as well as a logfile are included so that the user keeps a record of exactly how a solution was derived.  These saved solutions can later be loaded as initial guesses for subsequent problems.

## Sample Session

Below is a sample session of running the included lid-driven cavity example in the interactive CLI:

```shell
python ~/goma_wrapper.py square_input.inp
Input file selected: square_input.inp


Goma Wrapper



Session name: 08-15-2022_sn-001
square.exoII --> guess.exoII
Run line: goma -i square_input.inp

Goma has NOT run yet
 1 Run Goma
 2 Add flags
 3 Load Guess/Cont solution
 4 Run with auto-Newton Factor
 5 Debug mode
 6 Save session
 7 Exit without saving session
 8 Exit and save session

Goma Wrapper Choice: 1
You selected 1 Run Goma
Parsing input file square_input.inp
Relevant files:
contin.dat
square_input.inp
echo_water.mat
out.exoII
water.mat
soln.dat
square.exoII
Running: /home/kerry/spack/opt/spack/linux-ubuntu20.04-x86_64_v4/gcc-9.4.0/goma-7.1.1-4pmbhwpvn63imkdbalyyxf5u2h4zk2r4/bin/goma -i square_input.inp
v7.1.1
/*************************************************************************
* Goma - Multiphysics finite element software                            *
* Sandia National Laboratories                                           *
*                                                                        *
* Copyright (c) 2022 Goma Developers, National Technology & Engineering  *
*               Solutions of Sandia, LLC (NTESS)                         *
*                                                                        *
* Under the terms of Contract DE-NA0003525, the U.S. Government retains  *
* certain rights in this software.                                       *
*                                                                        *
* This software is distributed under the GNU General Public License.     *
* See LICENSE file.                                                      *
\************************************************************************/

PRS, PAS, RRR, KSC, RAC, TAB, DRN, PLH, DAL, IDG, ACK, ACS, RBS, RRL, MMH, SRS
HKM, RAR, EDW, PKN, SAR, EMB, KT, DSB, DSH, WWO ...




Number of unknowns            = 4562

Number of matrix nonzeroes    = 188484


               R e s i d u a l         C o r r e c t i o n

   ToD   itn   L_oo    L_1     L_2     L_oo    L_1     L_2   lis  asm/slv (sec)
-------- --- ------- ------- ------- ------- ------- ------- --- ---------------
10:09:35 [0] 6.9e-02 2.6e+00 3.5e-01 1.0e+01 4.2e+03 1.9e+02  1  3.0e-02/4.0e-02
10:09:35 [1] 1.3e-02 1.2e+00 5.7e-02 3.2e-01 1.2e+02 3.0e+00  1  4.0e-02/3.0e-02
10:09:35 [2] 1.5e-03 1.9e-01 7.4e-03 2.6e-02 1.8e+01 4.3e-01  1  4.0e-02/3.0e-02
10:09:36 [3] 1.3e-05 3.5e-03 1.2e-04 3.2e-03 1.3e+00 5.7e-02  1  3.0e-02/3.0e-02
10:09:36 [4] 2.9e-09 5.8e-07 2.0e-08 9.6e-03 3.8e+00 1.9e-01  1  4.0e-02/3.0e-02
10:09:36 [5] 1.7e-14 9.4e-13 4.5e-14                         skp 3.0e-02/0.0e+00
-------- --- ------- ------- ------- ------- ------- ------- --- ---------------
scaled solution norms   1.020e+01  9.355e-01  2.872e+00
                converged SS!

-done


Proc 0 runtime:       0.01 Minutes.

Success
Gorun has completed (Success).  Process took 0.8055529594421387 seconds.
Run line: goma -i square_input.inp

Goma has ALREADY run
 1 Run Goma
 2 Add flags
 3 Load Guess/Cont solution
 4 Run with auto-Newton Factor
 5 Debug mode
 6 Save session
 7 Exit without saving session
 8 Exit and save session

Goma Wrapper Choice: 8
You selected 8 Exit and save session
Creating directory 08-15-2022_sn-001
Expected file contin.dat is missing.  Skipping.
Copying square_input.inp to 08-15-2022_sn-001/square_input.inp
Copying echo_water.mat to 08-15-2022_sn-001/echo_water.mat
Copying out.exoII to 08-15-2022_sn-001/out.exoII
Copying water.mat to 08-15-2022_sn-001/water.mat
Copying 08-15-2022_sn-001_100935_tgplog.txt to 08-15-2022_sn-001/08-15-2022_sn-001_100935_log.txt
Copying soln.dat to 08-15-2022_sn-001/soln.dat
Copying square.exoII to 08-15-2022_sn-001/square.exoII
Copying a bunch of files
Clearing temp files:
All done!
```
