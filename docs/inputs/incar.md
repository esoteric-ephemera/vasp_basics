
## INCAR

The [INCAR](https://vasp.at/wiki/INCAR) enumerates most of the basic control parameters of a VASP calculation.
This includes both the details of the scientific simulation, like the functional used or the magnetic state of that system, and the mathematical ones.

### Format

The INCAR takes the form of a plaintext list of `key = value` pairs, like:

```fortran
EDIFF = 680 # the plane-wave cutoff energy in eV
EDIFFG = -0.05 # Indicating that relaxation stops when forces reach less than 0.05 eV/Å
METAGGA = R2SCAN # We use the r2SCAN meta-GGA as a base
LHFCALC = True # We also use exact / "Hartree-Fock" exchange
AEXX = 0.25 # We use 25% exact exchange --> r2SCAN0 global hybrid
```

There are a couple of things to note.
FORTRAN (the language used by VASP) has historically been case insensitive and space insensitive (with the exception of FORTRAN70).
That means that specifying:
```fortran
ALGO = All
```
and
```fortran
ALGO = ALL
```
are parsed the same way.
Similarly, in FORTRAN, `bool`s are written as `.True.` and `.False`, but VASP can also parse leading `T` and `F` characters consistently, so these should all be parsed as `.True.`:
```fortran
LWAVE = .True.
LCHARG = .TRUE.
LAECHG = T
LELF = True
```
That being said, it's best not to abuse this since newer FORTRAN and newer INCAR tags are case sensitive.

### Important parameters

There is a huge list of INCAR parameters available via the  [VASP manual](https://vasp.at/wiki/INCAR).
Note that every parameter has a default value, so the user need only specify values they want changed.
It's infeasible to specify all parameters in VASP explicitly.
A more complete list of INCAR tags (after being parsed) is available in the `vasprun.xml`.

We'll go over a few key ones:

| Parameter | Meaning | General Recommendation |
| -- | -- | -- |
| [ALGO](https://vasp.at/wiki/ALGO) | How the linear algebra problem is solved. | In general, try `Normal`. This is robust enough for meta-GGAs and generally fast enough. If you hit any issues with the calculation, try `All`, which is much more expensive but reliable. For GGAs, you can use `Fast` by default. Unless you fully understand the purpose of the other options, avoid setting them. |
| [EDIFF](https://vasp.at/wiki/EDIFF) | Energy convergence criterion. Lower values mean more accurate calculations. | 10<sup>-6</sup> to 10<sup>-5</sup> eV is generally adequate. Linear response and phonon calculations will require lower ("tighter") values, such as 10<sup>-9</sup> eV. |
| [EDIFFG](https://vasp.at/wiki/EDIFFG) | Force convergence criterion. If a positive value, the relaxation stops when the energy differences (eV) are below this value. If a negative value, the relaxation stops if the force magnitudes are below this value (eV/Å). Lower (in magnitude) values mean a more accurate calculation. | Depends - a "coarse" relaxation would be roughly $0.05$ to $0.1$ eV/Å, a "fine" relaxation would be $\sim 0.02$ eV/Å. Larger structures will tend to need coarser relaxation parameters. |
| [ENCUT](https://vasp.at/wiki/ENCUT) | Plane wave energy cutoff in eV. Higher value **generally but not always** mean a more accurate calculation. | At least 110% of the maximum ENMAX of the POTCARs you use. If you see an error with `PSMAXN` in the OUTCAR(run `grep PSMAXN OUTCAR`), lower this - the cutoff is too high and the calculation will become unstable. |
| [GGA](https://vasp.at/wiki/EDIFFG) | The choice of generalized gradient approximation (GGA) to use, or confusingly, the choice of local density approximation (LDA) to use. | Avoid setting this parameter if you plan to use the `METAGGA` tag. This will cause unintentional shifts to the total energy that render it meaningless. Unless you are pursuing an academic work in DFT, avoid using the LDA (`GGA = CA`). Functionally, both `PBE` (`GGA = PE`) and `PBEsol` (`GGA = PS`) are suitable for high-throughput work. PBEsol will be slightly more accurate for geometries and for the energetics of metals, but PBE is a better general-purpose functional. |
| [KSPACING](https://vasp.at/wiki/KSPACING) | The spacing between $\bm{k}$-points in the calculation. Is superseded by the KPOINTS file if one is provided. Lower values indicate a higher density of $\bm{k}$-points, and thus a more accurate calculation. | Depends on the electronic structure. 0.22 is a fine general default if you don't know the electronic structure <it>a priori</it>. Metals and semi-metals (up to 0.2 eV gap) will need a higher density of $\bm{k}$-points, stick to 0.22 for these. Narrow gap insulators (0.2 to 1 eV) can use up to 0.3. Wider gap (1 to 2 eV) insulators can use up to 0.44. Ultrawide gap insulators (more than 2 eV gap) can use 0.5. For a benchmark calculation 0.1 is what I typically use. |
| [METAGGA](https://vasp.at/wiki/METAGGA) | The choice of meta-GGA. | My personal bias recommends r<sup>2</sup>SCAN, but you could also use SCAN if time costs aren't a concern, or TASK if you wanted to explore band gaps. |
| [NELM](https://vasp.at/wiki/NELM) | The maximum number of electronic self-consistency steps. This is the "inner-loop" of a calculation. Every static calculation and each step of a relaxation will depend sensitively on this. | 100-200 is typically fine. 200 is more than enough but could be set for systems with challenging electronic structure. |
| [NSW](https://vasp.at/wiki/NSW) | The maximum number of steps permitted in a relaxation, or the number of frames undertaken in molecular dynamics. | 100 is typically fine for a relaxation. You may need more for nudged elastic band calculations. For MD, determine this based on the desired simulation time. |
| [PREC](https://vasp.at/wiki/PREC) | The density of the Fourier grid used by VASP. | Use `Accurate` unless you have a very good reason to use another value. |
