---
title: Credits & licenses
description: Everything this site is built from, who made it, and the license notices that come with it.
updated: 2026-11-10
---

Robot Lantern is built from RJ's writing and photos, conversations with AI models, open-source software and open science data. This page credits all of it and carries the notices those licenses ask for.

## The writing

Unless a page says otherwise, the essays and chats are © Robot Lantern LLC and licensed under [Creative Commons Attribution-NonCommercial 4.0 International](https://creativecommons.org/licenses/by-nc/4.0/) (CC BY-NC 4.0). To credit a piece, give its title, "Robot Lantern", a link to the page and a link to the license, and say if you changed it.

Parts of the essays and chats were written by AI models: ChatGPT (OpenAI) so far. Each essay shows who wrote which words, and each chat shows who said what. Text written by a model may not be protected by copyright; the license covers the human-written text and the selection, arrangement and editing of the whole. See [Terms](/terms/) for what the license doesn't cover.

## Photos and images

- **RJ's photos.** The starry sky on the home page, the treeline (cut from his sunset photo), the home page's sunset colors (from another of his photos), the photos in "It's Always the Pleiades", and the sky photo at the center of The Sky, Unprojected were taken by RJ. © Robot Lantern LLC, all rights reserved: they aren't covered by the CC BY-NC license.
- **The annotated sky photo** in "It's Always the Pleiades" is RJ's photo with labels added by ChatGPT, published as ChatGPT returned it.
- **The generated image** in "It's Always the Pleiades", a night sky seen from a planet in the Pleiades, was made by ChatGPT (OpenAI) during the conversation and is shown as it appeared there.
- **The compass screenshot** in the same chat is from RJ's phone.

## The name and wordmark

The Robot Lantern name, the lantern wordmark and the art in the shop are Robot Lantern LLC's and aren't covered by any open license.

## The Sky, Unprojected

The interactive at [/builds/the-sky-unprojected/](/builds/the-sky-unprojected/) was built for this site with Claude (Anthropic). Its data comes from the sources below. A full list of datasets, versions and methods travels with the data as [SOURCES.md](/sky/data/SOURCES.md).

**Hipparcos.** Star positions, magnitudes, colors and parallaxes. Credit: ESA. From *The Hipparcos and Tycho Catalogues*, ESA 1997 (ESA SP-1200), and *Hipparcos, the New Reduction of the Raw Data*, van Leeuwen 2007 (A&A 474, 653), via VizieR (catalogues I/239 and I/311). Licensed under [CC BY-NC 3.0 IGO](https://creativecommons.org/licenses/by-nc/3.0/igo/).

**Gaia DR3.** Parallaxes for fainter stars, zero-point corrected after Lindegren et al. 2021 (A&A 649, A4). Credit: ESA/Gaia/DPAC. Licensed under [CC BY-NC 3.0 IGO](https://creativecommons.org/licenses/by-nc/3.0/igo/).

> This work has made use of data from the European Space Agency (ESA) mission Gaia (<https://www.cosmos.esa.int/gaia>), processed by the Gaia Data Processing and Analysis Consortium (DPAC, <https://www.cosmos.esa.int/web/gaia/dpac/consortium>). Funding for the DPAC has been provided by national institutions, in particular the institutions participating in the Gaia Multilateral Agreement.

Gaia Collaboration, Prusti et al. 2016, "The Gaia mission", A&A 595, A1. Gaia Collaboration, Vallenari et al. 2023, "Gaia Data Release 3: Summary of the content and survey properties", A&A 674, A1.

The ESA data is used here non-commercially: the interactive is free, carries no ads and isn't sold, and none of this data goes into anything in the shop. Anyone reusing it commercially needs ESA's permission.

**Open cluster distances.** Hunt & Reffert 2023, "Improving the open cluster census. II. An all-sky cluster catalogue with Gaia DR3", A&A 673, A114, via VizieR (J/A+A/673/A114). These values derive from Gaia DR3.

**Star names.** The [IAU Catalog of Star Names](https://www.iau.org/WG280/WG280/Home.aspx), IAU Working Group on Star Names (WGSN), in E. Mamajek's machine-readable edition of 2022-04-04.

**Deep-sky positions.** This research has made use of the SIMBAD database, CDS, Strasbourg Astronomical Observatory, France (Wenger et al. 2000, A&AS 143, 9).

**VizieR.** This research has made use of the VizieR catalogue access tool, CDS, Strasbourg Astronomical Observatory, France (DOI: [10.26093/cds/vizier](https://doi.org/10.26093/cds/vizier); Ochsenbein et al. 2000, A&AS 143, 23).

**Deep-sky magnitudes.** [OpenNGC](https://github.com/mattiaverga/OpenNGC) by Mattia Verga, licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The magnitudes taken from it, in `/sky/data/objects.json`, are shared under CC BY-SA 4.0 too.

**Constellation figures.** The stick figures come from [d3-celestial](https://github.com/ofrohn/d3-celestial), © 2015 Olaf Frohn, matched to Hipparcos stars. BSD 3-Clause license; the full notice is under "License texts" below.

**Distances from the literature,** where no catalogue has a good value:

- Orion Nebula Cluster: Kuhn et al. 2019, ApJ 870, 32
- Betelgeuse: Joyce et al. 2020, ApJ 902, 63
- Mintaka: Oplištilová et al. 2023, A&A 672, A31
- Alnilam and Alnitak: Oplištilová et al. 2025, A&A 704, A204
- Crab Nebula: Lin et al. 2023, ApJ, [doi:10.3847/1538-4357/acdc98](https://doi.org/10.3847/1538-4357/acdc98)

**The Milky Way model.** The view of the galaxy from above is a model, not a measurement. Its spiral arms and the distance to the Galactic Center follow Reid et al. 2019, "Trigonometric Parallaxes of High-mass Star-forming Regions: Our View of the Milky Way", ApJ 885, 131. The Sun's height above the disc is from Bennett & Bovy 2019, MNRAS 482, 1417. The bar is drawn after Wegg, Gerhard & Portail 2015, MNRAS 450, 4050. The rest of that picture is illustrative.

**3D drawing.** [three.js](https://threejs.org), © 2010–2026 three.js authors, MIT License. The notice ships with the code as [THIRD-PARTY-LICENSES.txt](/sky/assets/THIRD-PARTY-LICENSES.txt) and is repeated below.

## Software

**Sent to your browser:**

- [KaTeX](https://katex.org), for math. © 2013–2020 Khan Academy and other contributors, MIT License (full text below).
- KaTeX's fonts. © 2009–2010 Design Science, Inc., © 2014–2018 Khan Academy, licensed under the [SIL Open Font License 1.1](https://openfontlicense.org), with Reserved Font Names KaTeX_AMS, KaTeX_Main and the other KaTeX_ family names. The license is also embedded in each font file.
- three.js, in The Sky, Unprojected (above).
- The site's own scripts, written for this site.

**Used to build the site** (nothing from these runs in your browser):

- [Astro](https://astro.build), © 2021 Fred K. Schott, MIT License.
- [unified](https://unifiedjs.com), remark-parse, remark-gfm, remark-math, remark-rehype, rehype-raw, rehype-katex, rehype-stringify and hast-util-to-html, from the unified collective, MIT License.
- [yaml](https://eemeli.org/yaml/) by Eemeli Aro, ISC License.

**Services:** Stripe takes payment for the shop, and Cloudflare hosts the site and its order service.

## AI models

Essays and chats are written with ChatGPT (OpenAI). The site's code and The Sky, Unprojected are written with Claude (Anthropic), and Claude proposes the editor's links in the chats for RJ to review. The people and models who write here are on the [authors](/authors/) page. OpenAI and Anthropic assign their users whatever rights they hold in what their models write, and neither endorses this site.

## Links

Chats link to the sources the models cited and, where marked, to Wikipedia articles chosen by the editor. Those pages are linked, not copied, and belong to their authors.

## License texts

**KaTeX (MIT License)**

> Copyright (c) 2013-2020 Khan Academy and other contributors
>
> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**three.js (MIT License)**

> Copyright © 2010-2026 three.js authors
>
> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**d3-celestial (BSD 3-Clause License)**

> Copyright (c) 2015, Olaf Frohn
> All rights reserved.
>
> Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
>
> 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
> 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
> 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
>
> THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The SIL Open Font License 1.1 for KaTeX's fonts is at [openfontlicense.org](https://openfontlicense.org/open-font-license-official-text/) and inside each font file. The Creative Commons licenses are linked where they apply.
