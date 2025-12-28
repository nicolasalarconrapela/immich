# 🎁 Immich Wrapped

Genera un resumen anual de tus fotos estilo "Spotify Wrapped" usando la API de Immich.

## ✨ Características

- **📊 Estadísticas completas**: Total de fotos, videos y favoritos del año
- **📅 Análisis mensual**: Distribución de fotos por mes con gráfico visual
- **👥 Personas detectadas**: Top personas más fotografiadas
- **🌍 Lugares visitados**: Ciudades y países más frecuentes
- **⭐ Mejores fotos**: Selección automática de las mejores fotos
- **📄 Reporte HTML**: Genera un bonito reporte visual
- **📚 Crear álbum**: Opcionalmente crea un álbum en Immich

## 🚀 Instalación

```bash
cd scripts/wrapped
pip install -r requirements.txt
```

## 📖 Uso

### Obtener API Key

1. Abre Immich en tu navegador
2. Ve a **Configuración** (icono de engranaje)
3. Selecciona **API Keys**
4. Haz clic en **New API Key**
5. Copia la clave generada

### Ejecutar el script

```bash
# Generar Wrapped del año anterior
python wrapped.py --api-key TU_API_KEY

# Generar Wrapped de un año específico
python wrapped.py --year 2024 --api-key TU_API_KEY

# Con URL personalizada de Immich
python wrapped.py --year 2024 --api-key TU_API_KEY --url http://mi-servidor:2283

# Generar y crear álbum automáticamente
python wrapped.py --year 2024 --api-key TU_API_KEY --create-album

# Exportar estadísticas a JSON
python wrapped.py --year 2024 --api-key TU_API_KEY --json stats.json

# Especificar nombre del reporte HTML
python wrapped.py --year 2024 --api-key TU_API_KEY --output mi_wrapped.html
```

## 🎨 Ejemplo de salida

```
╔═══════════════════════════════════════════╗
║         🎁 IMMICH WRAPPED 🎁              ║
║      Tu resumen anual de fotos            ║
╚═══════════════════════════════════════════╝

🔌 Conectando a http://localhost:2283...
✅ Conectado como: Usuario (email@example.com)

🎁 Generando Wrapped 2024...
==================================================

📸 Descargando fotos del año...
  📥 Total descargado: 3482 assets

📊 Calculando estadísticas...
  📷 Fotos: 3200
  🎬 Videos: 282
  ⭐ Favoritos: 156

📅 Analizando por meses...
  Enero: 234 fotos
  Febrero: 189 fotos
  ...

👥 Analizando personas...
  1. María: 892 fotos
  2. Juan: 567 fotos
  3. Carlos: 234 fotos

🌍 Analizando lugares...
  🏙️ Top ciudades:
     1. Madrid: 1234 fotos
     2. Barcelona: 456 fotos

📄 Reporte generado: wrapped_2024.html

🎉 ¡Wrapped 2024 completado!
```

## 📁 Archivos generados

- `wrapped_YEAR.html` - Reporte visual HTML
- `stats.json` (opcional) - Estadísticas en formato JSON

## 🛠️ Opciones

| Opción | Descripción | Default |
|--------|-------------|---------|
| `--year, -y` | Año para generar | Año anterior |
| `--api-key, -k` | API Key de Immich | **Requerido** |
| `--url, -u` | URL de Immich | http://localhost:2283 |
| `--output, -o` | Archivo HTML de salida | wrapped_YEAR.html |
| `--create-album, -a` | Crear álbum en Immich | No |
| `--json` | Exportar estadísticas a JSON | No |

## 📷 Vista previa del reporte

El reporte HTML generado incluye:
- Banner con el año
- Tarjetas de estadísticas (fotos, videos, favoritos)
- Gráfico de barras por mes
- Lista de personas más fotografiadas
- Lista de lugares más visitados
- Diseño responsive y moderno

## 🔒 Seguridad

- La API Key nunca se almacena en disco
- Se recomienda usar variables de entorno para la API Key:

```bash
export IMMICH_API_KEY="tu_api_key"
python wrapped.py --api-key $IMMICH_API_KEY
```

## 📝 Licencia

MIT - Libre para uso personal y comercial.
