# Contribuir paquetes a VANTOR

¡Cualquier persona puede proponer paquetes! No necesitas ser colaborador del repositorio ni tener permisos de escritura.

## Método oficial: Pull Request

1. Haz un fork de `Reaccionador2Jeje/vantor-linux`.
2. Prepara tu paquete como archivo `.tar.gz`. Su contenido debe usar rutas relativas a la raíz de VANTOR, por ejemplo `usr/bin/hola` o `usr/share/doc/hola/README`.
3. Añade el archivo a `incoming/<arquitectura>/<nombre>-<version>.tar.gz`.
4. Añade junto a él un archivo JSON con el mismo nombre base: `incoming/<arquitectura>/<nombre>-<version>.json`.
5. Abre un Pull Request hacia `main). GitHub Actions comprobará automáticamente el paquete.
6. Tras la revisión y aceptación del PR, el flujo de publicación subirá el archivo a GitHub Releases y actualizará el índice Nyan.

Ejemplo de metadatos JSON:

```json
{
  "name": "hello",
  "version": "1.0.0",
  "architecture": "x86_64",
  "description": "Un paquete de ejemplo"
}
```

La arquitectura del JSON debe coincidir con el directorio: `x86_64`, `aarch64` o `all`. El nombre y versión deben coincidir con el nombre del archivo. No incluyas scripts de instalación que se ejecuten automáticamente.

## Reglas de seguridad y calidad

- Solo paquetes legales, respetuosos y relacionados con el sistema.
- No incluyas malware, spyware, credenciales, datos personales ni contenido dañino.
- No uses rutas absolutas, `..`, enlaces simbólicos peligrosos ni archivos que sobrescriban componentes críticos sin justificación.
- El paquete debe incluir solo los archivos necesarios y una descripción clara.
- El autor debe tener derecho a distribuir todo el contenido incluido.
- No subas secretos, claves privadas ni tokens.
- Los paquetes se revisan antes de incorporarse al repositorio oficial.

## Límites iniciales

Para evitar que el repositorio se convierta en un almacén gigante, los archivos de contribución deben pesar como máximo 20 MiB cada uno. El equipo puede cambiar este límite cuando el sistema de distribución madure.

La aceptación de un Pull Request no significa que el paquete sea seguro para todos los usos. Nyan sigue en desarrollo y aún necesita firmas criptográficas, aislamiento, resolución de dependencias y transacciones seguras.
