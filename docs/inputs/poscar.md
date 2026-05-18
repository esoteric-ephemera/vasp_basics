
## POSCAR

This is the geometry file of the calculation.
While you don't need to know how to write this by hand, you should know how to read and interpret it.
This will also be the format of the `CONTCAR` file printed at output (the final relaxed structure if applicable), as well as the generic form of the `XDATCAR` (structure along the relaxation or molecular dynamics trajectory).

### Format

Let's look at a "basic" [POSCAR](https://vasp.at/wiki/POSCAR).
Note that the format of this file has generally remained the same, but some of the lines have become optional over the years.
For general backwards compatibility, the older format discussed here should be preferred.

```
Zn4 S4
1.0
   5.4    0.0    0.0
   0.0    5.4    0.0
   0.0    0.0    5.4
Zn S
4 4
direct
   0.0    0.0    0.0 Zn
   0.0    0.5    0.5 Zn
   0.5    0.0    0.5 Zn
   0.5    0.5    0.0 Zn
   0.25   0.25    0.75 S
   0.25   0.75    0.25 S
   0.75   0.25    0.25 S
   0.75   0.75    0.75 S
```
The format is:
1. Comment, ignored
2. "Scaling factor" in Å. Think of this as a generic lattice constant. An equivalent way to how we've specified the above section is:
```
5.4
   1.0    0.0    0.0
   0.0    1.0    0.0
   0.0    0.0    1.0
```
3. The direct lattice vectors (in real-space) in Å.
The first line is the $\boldsymbol{a}$-lattice vector, the second is $\boldsymbol{b}$, and the third is $\boldsymbol{c}$.
These will be multiplied by the scale factor above.
In this example, we have a simple cubic lattice with $a=5.4$ Å.
4. List of the elements, grouped by symbol. The order of these **must** match the order in the POTCAR.
5. How many elements are in the structure, by type. Here, we state that the coordinates of 4 Zn atoms will be listed, then 4 S atoms.
6. Whether the coordinates of the atoms will be specified in units of the lattice vectors (`direct`) or in cartesian coordinates (`cartesian`). Either is fine.
7. The $a$, $b$, and $c$ (if `direct`) or $x$, $y$, $z$ (if `cartesian`) coordinates of the atoms. The atom label is optional but will be parsed by VASP.

### More options

#### Constrained relaxation

If you are performing a selective relaxation of some atoms (relevant for folks doing ApproxNEB), you need to specify the `selective dynamics` tag and which degrees of freedom can relax:
```
Zn4 S4
1.0
   5.4    0.0    0.0
   0.0    5.4    0.0
   0.0    0.0    5.4
Zn S
4 4
selective dyamics
direct
   0.0    0.0    0.0 F F F
   0.0    0.5    0.5 T F F
   0.5    0.0    0.5 F T F
   0.5    0.5    0.0 T T T
   0.25   0.25    0.75 T T T
   0.25   0.75    0.25 T T T
   0.75   0.25    0.25 T T T
   0.75   0.75    0.75 T T T
```

This specification states that the first Zn atom cannot move; the second Zn atom can only relax its first coordinate; the third Zn atom can only relax its second coordinate.
All other atoms are permitted to move in any direction.

#### Molecular dynamics

One can specify the velocities of the atoms to start a calculation.
A `CONTCAR` will include the final velocities, as well as the predictor-corrector values from the dynamics to aid in restarting a calculation.
