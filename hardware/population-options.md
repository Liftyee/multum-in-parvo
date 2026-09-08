# Population options — revision A draft

Select one RF path and one battery-protection option. Fuel gauge and peripheral power are independent choices.

| Option | Fit | Leave open / DNP |
|---|---|---|
| Normal RF, default | U601, R602–R605, C611–C612, R623 | U602 and all FEM-group parts, R606/R607/R609 |
| FEM RF | U602, FEM-group RF/supply/control parts including R606/R607/R609 | Normal RF group U601, R602–R605, C611–C612, R623 |
| Raw cell, default | U301, Q301, Q302, R301/R302, C301 | R303 |
| Externally protected pack | R303, 0 Ω rated for burst current | U301, Q301/Q302, R301/R302, C301 |
| Fuel gauge | U502, C504, R504–R506 | Entire group for minimum current |
| Peripheral rail | U503, R507, C505/C506, J501 | Entire group if unused |

**C610, C622, C626 and C628 remain DNP initially**, including in the FEM population. Their tuning status takes precedence over the broader FEM-group instruction. Fit them only according to measured matching results. R610 starts at 0 Ω and C627 at 68 pF; these are common to both RF variants.

Never fit R303 with an unprotected cell. It bypasses the negative-side protection and does not short the cell terminals, but it removes protection. Fit only one of the two RF selector sets; both paths together create an invalid RF network.

The inactive branch starts at its open selector pad. Inspect actual copper for residual stubs before release. R605/R609 and R610 allow path isolation for conducted measurement without adding a permanent RF tee.
