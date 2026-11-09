# vendor/

Copias locales de lo que el explorador antes cargaba de internet. `14_explorador` las
pega dentro de `outputs/explorador.html`, así la página no depende de CDN ni de Google
Fonts. Lo único externo que queda es el mapa base (teselas de Esri). Bajadas el 2026-11-09.

| Archivo | Versión y origen | Licencia |
|---|---|---|
| `leaflet.min.js` | Leaflet 1.9.4, cdnjs | BSD-2-Clause |
| `graphology.umd.min.js` | graphology 0.25.4, cdnjs | MIT |
| `graphology-library.min.js` | graphology-library 0.8.0, jsDelivr (npm) | MIT |
| `sigma.min.js` | sigma.js 2.4.0, cdnjs | MIT |
| `ibmplexsans-latin.woff2` | IBM Plex Sans (variable, subconjunto latino), Google Fonts | OFL 1.1 |
| `newsreader-latin.woff2`, `newsreader-italic-latin.woff2` | Newsreader (variable, subconjunto latino), Google Fonts | OFL 1.1 |

El CSS de Leaflet está un nivel más arriba (`plantillas/leaflet-1.9.4.css`).

