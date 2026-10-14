# Motion references

The current `web/` interface bundles React and **GSAP 3.15.0 Core/Flip** through npm. GSAP is governed by its [Standard License](https://gsap.com/standard-license/), not the Hairline MIT license. Its original copyright/license banners are retained in the distributed bundle. React, Vite and supporting build tools retain their package licenses. No Base44 template source or assets were copied.

The archived Streamlit UI uses independently authored local CSS/JavaScript, Streamlit v2 components and native Streamlit widgets. Its folder ripple, layered details and execution relay are inspired by [Hairline](https://github.com/lucasmarkes/hairline), specifically Riffle, Exploded and Relay. It is an adaptation of the interaction ideas for readable, functional controls, not the original isometric SVG renderer. No Hairline JavaScript or TypeScript runtime is bundled, and no external CDN is required.

The upstream MIT notice is retained here for attribution and reference:

MIT License

Copyright (c) 2026 Lucas Marques

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## Additional design references

GSAP Timeline sequencing, Motion, Anime.js and AutoAnimate informed timing and transition ideas. The React transitions use bundled GSAP Core/Flip. The archived Streamlit sequences use browser-native animation APIs. Motion, Anime.js and AutoAnimate are references only; their runtimes are not bundled. React Bits, Motion Primitives and Uiverse were evaluated as design references; no components from those projects are included.

## Noto Sans SC

Bundled WOFF2 files derive from the official Google Fonts Noto Sans SC variable font. They retain the source font's complete character coverage, divided into Unicode-range subsets. The SIL Open Font License and copyright notices are included in `web/public/fonts/OFL.txt`; source provenance and checksums are in `web/public/fonts/manifest.json`. Font preparation uses fontTools and Brotli only during development, not application runtime.

## Original product assets

The optical welcome illustration, command palette, inquiry-lens presentation and printable review packet are independently authored for this project. They use local SVG, CSS and native browser APIs; no external CDN is required. Existing Hairline and font notices above remain applicable.
