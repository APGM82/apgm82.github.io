# tools

Utilidades para generar recursos del sitio. No forman parte de la web; no se enlazan desde ninguna página.

## video-poster.swift

Genera el póster vertical del vídeo (`../video-poster.jpg`): fondo degradado, el icono de la app,
el título "MANA / MTG ARCHIVE" y las pastillas de plataforma. Formato 9:16 (720×1280) para el
marco vertical del reproductor en `index.html`.

Uso (macOS, con Swift instalado):

```sh
swift tools/video-poster.swift poster.png
# convertir a JPG (más ligero) y colocar en la raíz del repo:
sips -s format jpeg -s formatOptions 82 poster.png --out video-poster.jpg
```

Nota: el script lee el icono desde una ruta ABSOLUTA al repo de la app
(`~/Developer/ManaMTGArchive-KMP/iosApp/iosApp/Assets.xcassets/AppIcon.appiconset/icon-1024.png`).
Si el icono se mueve, actualiza `iconPath` dentro del script.
