

## POTCAR

In solid state calculations, and in calculations of molecules with "heavy" atoms (usually Kr and up), it is common to use what is called a "pseudopotential" to describe the interaction between nuclei and electrons.
Let's remind ourselves that the interaction between a point nucleus of charge $Ze$ at position $\boldsymbol{R}$, and an electron of charge $-e$ at position $\boldsymbol{r}$, is the Coulomb interaction:
$$
V(|\boldsymbol{r} - \boldsymbol{R}|) = - \frac{Z e^2}{|\boldsymbol{r} - \boldsymbol{R}|}.
$$
Then af pseudopotential replaces $N_c$ of the "core" electrons with an effective interaction, and removes them from the calculation entirely.
The remaining $N_v$ electrons experience a modified interaction called the pseudopotential.
Perhaps the simplest pseudopotential is the "muffin-tin" potential
$$
\widetilde{V}(s) = \left\{
    \begin{array}{rr}
    V_0, & s < r_\mathrm{cut} \\
    -Z e^2/s, & s \geq r_\mathrm{cut}
    \end{array}
\right.
$$
where now $\boldsymbol{s} = \boldsymbol{r} - \boldsymbol{R}$, the separation distance between the nucleus and electron.

The basic idea of pseudopotentials are active and participant electrons.
Active electrons are those which participate in the formation and breaking of chemical bonds.
They are the electrons which allow for bonding across atoms, and delocalize in metals, leading to the formation of metallic bonds.
Participant electrons are tightly bound to the core of a nucleus, and don't feature much in the previous phenomena.
However, ideally, they would change their distribution in space given the presence of different valence bonding arrangements.

Similarly, if you are trying to study core-hole excitations (moving a deep core electron into an excited state, possibly ionizing an atom), a pseudopotential will be unable to describe this process.
This is because a pseudopotential **freezes** the core electrons in some configuration and assumes they never change.

Pseudopotentials are still useful because they are chosen to contain enough valence electrons to still accurately describe phenomena like bond-formation and breaking.
However, it is very easy to use a pseudopotential which has too few electrons and therefore not be able to represent certain bonding arrangements.

A good example is the oxygen atom, which has the electronic configuration $1s^2 \, 2s^2 \, 2p^4$.
In principle, oxygen has only two unpaired eletrons in the $p$ shell, which are most likely to participate in bonding.
However, using only these two electrons as valence electrons would prevent one from being able to form, e.g., ozone.

Typically, the minimal pseudopotential will include **all** electrons in the outermost unfilled shell.
For oxygen, this is the $n = 2$ shell, so 6 electrons.

### The Vacuum Level

Each pseudopotential, when combined with a particular functional, has a unique, unknown vacuum level.
This is the value of the pseudopotential at infinite separation, very far from any atom.

**Thus the absolute total energies from a pseudopotential calculation are meaningless on their own.**
Only energy differences, such as the cohesive or binding energy (energy relative to isolated atoms), or formation energy (relative to some stable phase) are meaningful.

This also means that you cannot easily compare absolute total energies between two different pseudopotentials.
You can, however, compare their energy differences.