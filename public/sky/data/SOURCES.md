# Sources

Every dataset used in this directory, with its version and licence. The scripts that fetch and
build them are in `scripts/`. Downloads are cached in `.cache/`, which git ignores, and nothing
is fetched while the page runs.

## ESA licence: non-commercial use

Hipparcos and Gaia data come from the ESA space science archives, which distribute them under
**CC BY-NC 3.0 IGO**. ESA's terms say that any commercial use, "including uses that directly or
indirectly generate financial gain," needs prior written authorisation, requested from
data.licences@esa.int ([ESA terms](https://www.cosmos.esa.int/web/esdc/terms-and-conditions),
[Gaia licence](https://www.cosmos.esa.int/web/gaia-users/license)). This page is free and
meant to bring people to the content, so it's treated as non-commercial use. Ask ESA before
this data goes into anything that earns money, such as a product, or a monetised video made
from the animations. Everything below that says "ESA" is affected, and so are the
Gaia-derived cluster distances.

## Files

| File | What | Built by |
| --- | --- | --- |
| `solution.json`, `solution.wcs.txt` | Plate solution for the photo | `scripts/solve/fit.py` ([docs/PLATE-SOLVE.md](../docs/PLATE-SOLVE.md)) |
| `objects.json` | Objects, their stars, constellation figures, references | `scripts/catalog/build_objects.py` |
| `field-stars.bin` | 2,429 stars in the photo's frame at their distances | `scripts/catalog/build_star_tables.py` |
| `near-stars.bin` | 60,196 Hipparcos stars with parallax better than 20% | `scripts/catalog/build_star_tables.py` |
| `galaxy.json` | **A model** of the Milky Way: spiral arms, the Sun's place, bar | `scripts/galaxy/build_galaxy.py` |

The `.bin` files are little-endian Float32, five values per star: x, y, z in parsecs
(heliocentric Galactic: +x toward the Galactic Centre, +y toward l = 90°, +z toward the North
Galactic Pole), then V magnitude and B−V colour. Stars are sorted brightest first.

## Datasets

| Dataset | Version | Used for | Licence and credit |
| --- | --- | --- | --- |
| **Hipparcos, the New Reduction** (van Leeuwen 2007, A&A 474, 653), VizieR I/311 | 2007 reduction, as served by VizieR in September 2026 | Positions, proper motions and parallaxes for stars; the plate solve | ESA archive data: CC BY-NC 3.0 IGO (see above). Credit ESA; cite van Leeuwen 2007 |
| **The Hipparcos Catalogue** (ESA 1997, SP-1200), VizieR I/239 | 1997 | V magnitudes, B−V, spectral types | As above. Cite ESA 1997 |
| **Gaia DR3** (Gaia Collaboration, Vallenari et al. 2023, A&A 674, A1), with its Hipparcos-2 cross-match `gaiadr3.hipparcos2_best_neighbour`, from the ESA Gaia archive | DR3 | Parallaxes for stars fainter than G = 4 when better than Hipparcos, zero-point corrected by +0.017 mas (Lindegren et al. 2021, A&A 649, A4) | CC BY-NC 3.0 IGO. Credit "ESA/Gaia/DPAC" |
| **Hunt & Reffert 2023**, "Improving the open cluster census II" (A&A 673, A114), VizieR J/A+A/673/A114 | As published | Distances, sizes, member counts and ages for M34–M38, the Pleiades, Hyades, α Persei, λ Orionis, NGC 1342, 1528, 1647, 2068 (M78) and IC 348 | Published in A&A, cite the paper. Values derive from Gaia DR3 (see above) |
| **IAU Catalog of Star Names** (IAU WGSN), E. Mamajek's machine-readable edition `IAU-CSN.txt` | Edition of 2022-04-04 | Star names | IAU products are released under Creative Commons Attribution; cite the IAU |
| **SIMBAD** (Wenger et al. 2000, A&AS 143, 9), CDS | Queried September 2026 | Positions of deep-sky objects | CDS: cite SIMBAD, CDS, Strasbourg |
| **OpenNGC** (M. Verga), `NGC.csv` and `addendum.csv` | GitHub `master`, September 2026 | Integrated V magnitudes of deep-sky objects | **CC BY-SA 4.0**. Share-alike applies to the magnitudes taken from it |
| **d3-celestial** constellation lines (O. Frohn), `constellations.lines.json` | GitHub `master`, September 2026 | Constellation stick figures, matched to Hipparcos stars within 0.3° | BSD-3-Clause. Keep the copyright notice: © 2015 Olaf Frohn |
| **Tycho-2 index files 4112–4119** for astrometry.net | data.astrometry.net `4100` series | Local plate solve only; not published | astrometry.net, BSD-3-Clause; Tycho-2 is ESA data |

## Literature values

Used where no catalogue has a good value. Each object's record says which applies.

| Object | Distance | Reference | Why not a catalogue |
| --- | --- | --- | --- |
| Orion Nebula Cluster (M42, M43) | 403 +7/−6 pc | Kuhn et al. 2019, ApJ 870, 32 (Gaia DR2, 378 members). VLBA gives 388 ± 5 pc (Kounkel et al. 2017) and 414 ± 7 pc (Menten et al. 2007) | Not in Hunt & Reffert 2023 |
| Betelgeuse | 168 +27/−15 pc | Joyce et al. 2020, ApJ 902, 63 (from its pulsations) | Parallaxes of this huge, variable star disagree |
| Mintaka (δ Ori) | 381 pc | Oplištilová et al. 2023, A&A 672, A31 (Orion OB1b from Gaia DR3) | Hipparcos (212 pc) is unreliable for these bright multiples |
| Alnilam (ε Ori) | 384 ± 8 pc | Oplištilová et al. 2025, A&A 704, A204 (median of Orion OB1b, Gaia DR3) | Hipparcos (606 pc) is unreliable |
| Alnitak (ζ Ori) | 386 pc | Oplištilová et al. 2025, as above | Hipparcos (226 pc) is unreliable |
| Crab Nebula (M1) | 1.90 +0.22/−0.18 kpc | Lin et al. 2023, ApJ, doi:10.3847/1538-4357/acdc98 (VLBI parallax of the pulsar) | Not a star cluster |

For Mintaka and Alnitak the papers give no uncertainty. The data uses ±8 pc, the value the
same method gives for Alnilam, and the cards say so.

## The Milky Way model (`galaxy.json`)

This is a model, not a measurement, and the page says so wherever it shows it.

| What | Value | Source |
| --- | --- | --- |
| Spiral arms | Log-periodic spirals with a kink: Table 2 of the paper, all seven arms (3-kpc, Norma, Scutum–Centaurus, Sagittarius–Carina, Local, Perseus, Outer), with the paper's arm-width law (42 pc per kpc of radius) | **Reid et al. 2019**, ApJ 885, 131, "Trigonometric Parallaxes of High-mass Star-forming Regions: Our View of the Milky Way"; values read from the arXiv source (1910.03357), September 2026 |
| Arms beyond their data | Drawn fainter and flagged `fitted: false`. Each extension follows the paper's section 3.2: Scutum–Centaurus continues past the centre as the Outer Scutum–Centaurus arm; Sagittarius–Carina drops to a 10° pitch past its tangency and reaches the bar near (−3, −3) kpc; Perseus continues inward at about 9°; the Outer arm wraps round to meet the Norma arm | As above |
| Distance to the Galactic Centre | R₀ = 8.15 ± 0.15 kpc (26,600 ly), the value the arm fits assume | Reid et al. 2019, fit A5 |
| The Sun's height above the mid-plane | 20.8 ± 0.3 pc | **Bennett & Bovy 2019**, MNRAS 482, 1417 |
| The bar | Illustrative: half-length 5.0 kpc at 30° to the Sun–centre line, near end at positive longitude | After **Wegg, Gerhard & Portail 2015**, MNRAS 450, 4050 (5.0 ± 0.2 kpc, 28–33°) |
| Bulge and disc glow | Illustrative | — |

`tests/galaxy.test.js` checks the arms against the paper: the fitted Norma, Scutum–Centaurus,
Sagittarius–Carina and 3-kpc arms reproduce Table 2's tangent longitudes to within 0.3°, and
the extensions end where section 3.2 says. Papers are © their authors and publishers; the
model uses only their published parameters.

## Rules

- **Star distances:** a literature value if listed above. Otherwise Gaia DR3 if the star is
  fainter than G = 4, has RUWE < 1.4 and a 5- or 6-parameter solution, and has a more precise
  parallax than Hipparcos. Otherwise Hipparcos 2007. The distance is 1/parallax, and the range
  is 1/(parallax ± error). A star is marked "poorly measured" when its error is over 20%.
- **Named Pleiades stars** (Alcyone, Atlas, Electra, Maia, Merope, Taygeta, Pleione, Celaeno,
  Asterope) take the cluster's distance, which is far better measured than any one bright
  member's.
- **Cluster distances** are Hunt & Reffert's median, with a floor of ±0.015 mas for Gaia's
  zero-point systematics added in quadrature to their statistical range.
- **Constellations and the Belt** give the range of their stars' distances. Each star keeps its
  own.

## Known soft spots

- **Hatysa (ι Ori)** sits in front of the Orion Nebula and is often associated with the young
  cluster NGC 1980 at about 400 pc. Its Hipparcos parallax (1.40 ± 0.22 mas) gives about
  710 pc, and Gaia can't measure a star this bright. The data keeps the measured value.
- **Almaaz (ε Aur)** has a Hipparcos parallax with a large error, and is marked "poorly
  measured".
