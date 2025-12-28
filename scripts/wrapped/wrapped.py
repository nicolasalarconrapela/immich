#!/usr/bin/env python3
"""
🎁 Immich Wrapped - Resumen Anual de Fotos
==========================================
Este script genera un resumen anual estilo "Spotify Wrapped" de tus fotos en Immich.

Características:
- Estadísticas del año (total fotos, videos, favoritos)
- Mejores fotos por mes
- Personas más fotografiadas
- Lugares más visitados
- Genera un álbum automático con las mejores fotos
- Crea un reporte HTML visual

Uso:
    python wrapped.py --year 2024 --api-key TU_API_KEY

Autor: Generado para Immich
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests


# ============================================================================
# CARGA DE .ENV
# ============================================================================

def load_dotenv(env_path: Path = None) -> dict:
    """
    Carga variables de entorno desde un archivo .env
    """
    env_vars = {}

    # Buscar .env en el directorio del script
    if env_path is None:
        script_dir = Path(__file__).parent
        env_path = script_dir / '.env'

    if not env_path.exists():
        return env_vars

    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Ignorar comentarios y líneas vacías
            if not line or line.startswith('#'):
                continue

            # Parsear KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Remover comillas si existen
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]

                env_vars[key] = value
                # También establecer en os.environ
                os.environ[key] = value

    return env_vars


# Cargar .env al importar el módulo
_env_vars = load_dotenv()


# ============================================================================
# MAPEO DE RUTAS (Docker -> Local)
# ============================================================================

def load_path_mappings(mappings_path: Path = None) -> dict:
    """
    Carga mapeos de rutas desde un archivo JSON.
    Formato: { "/mnt/docker-path": "C:/local/path" }
    """
    if mappings_path is None:
        script_dir = Path(__file__).parent
        mappings_path = script_dir / 'path_mappings.json'

    if not mappings_path.exists():
        return {}

    try:
        with open(mappings_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error cargando path_mappings.json: {e}")
        return {}


def translate_docker_path(docker_path: str, mappings: dict) -> str:
    """
    Traduce una ruta de Docker a la ruta local equivalente.
    Ejemplo: /mnt/fotos-papa/2009/foto.jpg -> E:/2TB/FotosPapa_Origin/Nico - copia/2009/foto.jpg
    """
    if not docker_path or not mappings:
        return docker_path

    for docker_root, local_root in mappings.items():
        if docker_path.startswith(docker_root):
            # Reemplazar la raíz de Docker con la raíz local
            relative_path = docker_path[len(docker_root):]
            # Asegurar que no haya doble slash
            if relative_path.startswith('/'):
                relative_path = relative_path[1:]
            # Construir ruta local
            local_path = os.path.join(local_root, relative_path)
            # Normalizar para Windows
            local_path = local_path.replace('/', '\\')
            return local_path

    return docker_path


# Cargar mapeos de rutas
_path_mappings = load_path_mappings()

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

DEFAULT_BASE_URL = "http://localhost:2283"
PHOTOS_PER_MONTH = 3  # Fotos destacadas por mes
MAX_TOP_PEOPLE = 10   # Top personas a mostrar
MAX_TOP_PLACES = 10   # Top lugares a mostrar


# ============================================================================
# MODELOS DE DATOS
# ============================================================================

@dataclass
class Asset:
    """Representa un asset (foto/video) de Immich"""
    id: str
    type: str  # IMAGE or VIDEO
    originalFileName: str
    fileCreatedAt: str
    isFavorite: bool
    city: Optional[str] = None
    country: Optional[str] = None
    people: list = field(default_factory=list)
    thumbhash: Optional[str] = None

    @property
    def date(self) -> datetime:
        return datetime.fromisoformat(self.fileCreatedAt.replace('Z', '+00:00'))

    @property
    def month(self) -> int:
        return self.date.month


@dataclass
class WrappedStats:
    """Estadísticas del Wrapped"""
    year: int
    total_photos: int = 0
    total_videos: int = 0
    total_favorites: int = 0
    photos_by_month: dict = field(default_factory=dict)
    top_people: list = field(default_factory=list)
    top_cities: list = field(default_factory=list)
    top_countries: list = field(default_factory=list)
    top_tags: list = field(default_factory=list)  # Etiquetas más usadas
    best_photos: list = field(default_factory=list)
    monthly_highlights: dict = field(default_factory=dict)


# ============================================================================
# CLIENTE API DE IMMICH
# ============================================================================

class ImmichClient:
    """Cliente para la API de Immich"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Realiza una petición a la API"""
        url = f"{self.base_url}/api{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json() if response.text else {}

    def get(self, endpoint: str, **kwargs) -> dict:
        return self._request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> dict:
        return self._request('POST', endpoint, **kwargs)

    def validate_connection(self) -> bool:
        """Valida la conexión con Immich"""
        try:
            user = self.get('/users/me')
            print(f"✅ Conectado como: {user.get('name', 'Usuario')} ({user.get('email', '')})")
            return True
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False

    def get_server_info(self) -> dict:
        """Obtiene información del servidor"""
        return self.get('/server/about')

    def search_assets(
        self,
        taken_after: Optional[str] = None,
        taken_before: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        asset_type: Optional[str] = None,
        city: Optional[str] = None,
        size: int = 1000,
        page: int = 1,
        with_people: bool = False
    ) -> dict:
        """Busca assets con filtros"""
        payload = {
            'size': size,
            'page': page,
            'withPeople': with_people,
            'withExif': True
        }

        if taken_after:
            payload['takenAfter'] = taken_after
        if taken_before:
            payload['takenBefore'] = taken_before
        if is_favorite is not None:
            payload['isFavorite'] = is_favorite
        if asset_type:
            payload['type'] = asset_type
        if city:
            payload['city'] = city

        return self.post('/search/metadata', json=payload)

    def get_all_assets_for_year(self, year: int, with_people: bool = False) -> list:
        """Obtiene todos los assets de un año"""
        all_assets = []
        page = 1

        taken_after = f"{year}-01-01T00:00:00.000Z"
        taken_before = f"{year}-12-31T23:59:59.999Z"

        while True:
            print(f"  📥 Descargando página {page}...", end='\r')
            result = self.search_assets(
                taken_after=taken_after,
                taken_before=taken_before,
                size=1000,
                page=page,
                with_people=with_people
            )

            assets = result.get('assets', {}).get('items', [])
            if not assets:
                break

            all_assets.extend(assets)
            page += 1

        print(f"  📥 Total descargado: {len(all_assets)} assets")
        return all_assets

    def get_all_people(self) -> list:
        """Obtiene todas las personas"""
        result = self.get('/people')
        return result.get('people', [])

    def get_person_assets(self, person_id: str) -> list:
        """Obtiene assets de una persona"""
        result = self.search_assets()
        # La API de búsqueda no filtra directamente por persona,
        # pero podemos obtener esto de otras formas
        return []

    def get_cities(self) -> list:
        """Obtiene ciudades con assets"""
        return self.get('/search/cities')

    def get_all_tags(self) -> list:
        """Obtiene todas las etiquetas"""
        try:
            return self.get('/tags')
        except Exception as e:
            print(f"  ⚠️ No se pudieron obtener tags: {e}")
            return []

    def create_album(self, name: str, description: str = "", asset_ids: list = None) -> dict:
        """Crea un nuevo álbum"""
        payload = {
            'albumName': name,
            'description': description,
            'assetIds': asset_ids or []
        }
        return self.post('/albums', json=payload)

    def add_assets_to_album(self, album_id: str, asset_ids: list) -> dict:
        """Añade assets a un álbum existente"""
        payload = {'ids': asset_ids}
        return self._request('PUT', f'/albums/{album_id}/assets', json=payload)

    def get_asset_thumbnail_url(self, asset_id: str) -> str:
        """Genera URL del thumbnail de un asset"""
        return f"{self.base_url}/api/assets/{asset_id}/thumbnail"


# ============================================================================
# GENERADOR DE WRAPPED
# ============================================================================

class WrappedGenerator:
    """Genera el Wrapped anual"""

    def __init__(self, client: ImmichClient, year: int):
        self.client = client
        self.year = year
        self.stats = WrappedStats(year=year)
        self.assets: list[dict] = []

    def generate(self) -> WrappedStats:
        """Genera el Wrapped completo"""
        print(f"\n🎁 Generando Wrapped {self.year}...")
        print("=" * 50)

        # 1. Descargar todos los assets del año
        print("\n📸 Descargando fotos del año...")
        self.assets = self.client.get_all_assets_for_year(self.year, with_people=True)

        if not self.assets:
            print(f"❌ No se encontraron fotos para el año {self.year}")
            return self.stats

        # 2. Calcular estadísticas básicas
        print("\n📊 Calculando estadísticas...")
        self._calculate_basic_stats()

        # 3. Analizar por mes
        print("\n📅 Analizando por meses...")
        self._analyze_by_month()

        # 4. Analizar personas
        print("\n👥 Analizando personas...")
        self._analyze_people()

        # 5. Analizar lugares
        print("\n🌍 Analizando lugares...")
        self._analyze_places()

        # 6. Analizar etiquetas
        print("\n🏷️ Analizando etiquetas...")
        self._analyze_tags()

        # 7. Seleccionar mejores fotos
        print("\n⭐ Seleccionando mejores fotos...")
        self._select_best_photos()

        return self.stats

    def _calculate_basic_stats(self):
        """Calcula estadísticas básicas"""
        for asset in self.assets:
            if asset.get('type') == 'IMAGE':
                self.stats.total_photos += 1
            elif asset.get('type') == 'VIDEO':
                self.stats.total_videos += 1

            if asset.get('isFavorite'):
                self.stats.total_favorites += 1

        print(f"  📷 Fotos: {self.stats.total_photos}")
        print(f"  🎬 Videos: {self.stats.total_videos}")
        print(f"  ⭐ Favoritos: {self.stats.total_favorites}")

    def _analyze_by_month(self):
        """Analiza fotos por mes"""
        months = {i: [] for i in range(1, 13)}

        for asset in self.assets:
            try:
                date = datetime.fromisoformat(
                    asset.get('fileCreatedAt', '').replace('Z', '+00:00')
                )
                month = date.month
                months[month].append(asset)
            except:
                pass

        month_names = [
            '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]

        for month, assets in months.items():
            count = len(assets)
            self.stats.photos_by_month[month] = {
                'name': month_names[month],
                'count': count,
                'assets': assets
            }
            if count > 0:
                print(f"  {month_names[month]}: {count} fotos")

            # Seleccionar highlights del mes (favoritos primero, luego random)
            favorites = [a for a in assets if a.get('isFavorite')]
            non_favorites = [a for a in assets if not a.get('isFavorite')]

            highlights = favorites[:PHOTOS_PER_MONTH]
            if len(highlights) < PHOTOS_PER_MONTH:
                # Añadir fotos no favoritas hasta completar
                import random
                remaining = PHOTOS_PER_MONTH - len(highlights)
                if non_favorites:
                    highlights.extend(random.sample(
                        non_favorites,
                        min(remaining, len(non_favorites))
                    ))

            self.stats.monthly_highlights[month] = highlights

    def _analyze_people(self):
        """Analiza personas más fotografiadas"""
        people_count = {}

        for asset in self.assets:
            people = asset.get('people', [])
            for person in people:
                person_id = person.get('id')
                person_name = person.get('name', 'Sin nombre')

                if person_id not in people_count:
                    people_count[person_id] = {
                        'id': person_id,
                        'name': person_name,
                        'count': 0,
                        'thumbnail': person.get('thumbnailPath')
                    }
                people_count[person_id]['count'] += 1

        # Ordenar por cantidad y tomar los top
        sorted_people = sorted(
            people_count.values(),
            key=lambda x: x['count'],
            reverse=True
        )

        self.stats.top_people = sorted_people[:MAX_TOP_PEOPLE]

        for i, person in enumerate(self.stats.top_people[:5], 1):
            name = person['name'] if person['name'] else 'Sin nombre'
            print(f"  {i}. {name}: {person['count']} fotos")

    def _analyze_places(self):
        """Analiza lugares más visitados"""
        cities_count = {}
        countries_count = {}

        for asset in self.assets:
            exif = asset.get('exifInfo', {})
            city = exif.get('city')
            country = exif.get('country')

            if city:
                cities_count[city] = cities_count.get(city, 0) + 1
            if country:
                countries_count[country] = countries_count.get(country, 0) + 1

        # Ordenar ciudades
        sorted_cities = sorted(
            cities_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
        self.stats.top_cities = [
            {'name': city, 'count': count}
            for city, count in sorted_cities[:MAX_TOP_PLACES]
        ]

        # Ordenar países
        sorted_countries = sorted(
            countries_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
        self.stats.top_countries = [
            {'name': country, 'count': count}
            for country, count in sorted_countries[:MAX_TOP_PLACES]
        ]

        if self.stats.top_cities:
            print(f"  🏙️ Top ciudades:")
            for i, city in enumerate(self.stats.top_cities[:5], 1):
                print(f"     {i}. {city['name']}: {city['count']} fotos")

        if self.stats.top_countries:
            print(f"  🌍 Top países:")
            for i, country in enumerate(self.stats.top_countries[:5], 1):
                print(f"     {i}. {country['name']}: {country['count']} fotos")

    def _analyze_tags(self):
        """Analiza etiquetas más usadas"""
        tags_count = {}

        for asset in self.assets:
            tags = asset.get('tags', [])
            for tag in tags:
                tag_id = tag.get('id')
                tag_name = tag.get('value', tag.get('name', 'Sin nombre'))
                tag_color = tag.get('color', '#667eea')

                if tag_id not in tags_count:
                    tags_count[tag_id] = {
                        'id': tag_id,
                        'name': tag_name,
                        'color': tag_color,
                        'count': 0
                    }
                tags_count[tag_id]['count'] += 1

        # Ordenar por cantidad
        sorted_tags = sorted(
            tags_count.values(),
            key=lambda x: x['count'],
            reverse=True
        )

        self.stats.top_tags = sorted_tags[:10]  # Top 10 tags

        if self.stats.top_tags:
            print(f"  🏷️ Top etiquetas:")
            for i, tag in enumerate(self.stats.top_tags[:5], 1):
                print(f"     {i}. {tag['name']}: {tag['count']} fotos")
        else:
            print(f"  (No hay etiquetas en las fotos de este año)")

    def _select_best_photos(self):
        """Selecciona las mejores fotos del año"""
        # Prioridad: favoritos, luego por cantidad de personas
        favorites = [a for a in self.assets if a.get('isFavorite')]

        # Ordenar favoritos por fecha
        favorites.sort(key=lambda x: x.get('fileCreatedAt', ''), reverse=True)

        # Tomar los mejores (máximo 12, uno por mes idealmente)
        best = []
        months_covered = set()

        for asset in favorites:
            try:
                date = datetime.fromisoformat(
                    asset.get('fileCreatedAt', '').replace('Z', '+00:00')
                )
                month = date.month

                if month not in months_covered:
                    best.append(asset)
                    months_covered.add(month)
                elif len(best) < 24:  # Añadir más si hay espacio
                    best.append(asset)
            except:
                pass

        # Si no hay suficientes favoritos, completar con otros
        if len(best) < 12:
            import random
            non_favorites = [a for a in self.assets if not a.get('isFavorite')]
            remaining = 12 - len(best)
            if non_favorites:
                best.extend(random.sample(
                    non_favorites,
                    min(remaining, len(non_favorites))
                ))

        self.stats.best_photos = best[:24]  # Máximo 24 fotos
        print(f"  ⭐ Seleccionadas {len(self.stats.best_photos)} mejores fotos")


# ============================================================================
# GENERADOR DE REPORTE HTML
# ============================================================================

class HTMLReportGenerator:
    """Genera un reporte HTML visual"""

    def __init__(self, stats: WrappedStats, client: ImmichClient):
        self.stats = stats
        self.client = client

    def generate(self, output_path: str):
        """Genera el archivo HTML"""
        html = self._build_html()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"\n📄 Reporte generado: {output_path}")

    def _build_html(self) -> str:
        """Construye el HTML del reporte"""
        month_names = [
            '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]

        # Construir sección de meses
        months_html = ""
        for month in range(1, 13):
            data = self.stats.photos_by_month.get(month, {})
            count = data.get('count', 0)
            name = month_names[month]
            bar_width = min(100, (count / max(1, self.stats.total_photos + self.stats.total_videos)) * 500)

            months_html += f"""
            <div class="month-bar">
                <span class="month-name">{name}</span>
                <div class="bar" style="width: {bar_width}%"></div>
                <span class="month-count">{count}</span>
            </div>
            """

        # Construir sección de personas
        people_html = ""
        for person in self.stats.top_people[:5]:
            name = person['name'] if person['name'] else 'Sin nombre'
            people_html += f"""
            <div class="person-card">
                <div class="person-avatar">👤</div>
                <div class="person-info">
                    <div class="person-name">{name}</div>
                    <div class="person-count">{person['count']} fotos</div>
                </div>
            </div>
            """

        # Construir sección de lugares
        places_html = ""
        for city in self.stats.top_cities[:5]:
            places_html += f"""
            <div class="place-item">
                <span class="place-name">📍 {city['name']}</span>
                <span class="place-count">{city['count']}</span>
            </div>
            """

        # Construir sección de etiquetas
        tags_html = ""
        for tag in self.stats.top_tags[:10]:
            tag_name = tag['name']
            tag_color = tag.get('color', '#667eea')
            # Asegurar que el color es válido
            if not tag_color or tag_color == 'null':
                tag_color = '#667eea'
            tags_html += f"""
            <span class="tag-badge" style="background-color: {tag_color}20; border-color: {tag_color}; color: {tag_color};">
                🏷️ {tag_name} <span class="tag-count">({tag['count']})</span>
            </span>
            """

        # Construir galería de mejores fotos
        gallery_html = ""
        for i, photo in enumerate(self.stats.best_photos[:24]):
            asset_id = photo.get('id')
            filename = photo.get('originalFileName', 'Sin nombre')
            date_str = photo.get('fileCreatedAt', '')[:10]
            photo_url = f"{self.client.base_url}/photos/{asset_id}"

            # Ruta local traducida
            docker_path = photo.get('originalPath', '')
            local_path = translate_docker_path(docker_path, _path_mappings)

            # Convertir ruta local a URL file:// para el navegador
            # Reemplazar backslashes por forward slashes y añadir file:///
            file_url = "file:///" + local_path.replace("\\", "/")

            # Información adicional
            exif = photo.get('exifInfo', {})
            city = exif.get('city', '')
            country = exif.get('country', '')
            location = f"{city}, {country}" if city and country else (city or country or '')

            gallery_html += f"""
            <a href="{file_url}" target="_blank" class="photo-card" title="{local_path}">
                <img src="{file_url}" alt="{filename}" loading="lazy" />
                <div class="photo-overlay">
                    <div class="photo-filename">{filename}</div>
                    <div class="photo-date">{date_str}</div>
                    <div class="photo-path">{local_path[-40:] if len(local_path) > 40 else local_path}</div>
                </div>
            </a>
            """

        # Construir lista de archivos
        files_html = ""
        for i, photo in enumerate(self.stats.best_photos, 1):
            filename = photo.get('originalFileName', 'Sin nombre')
            docker_path = photo.get('originalPath', '')
            # Traducir ruta Docker a ruta local
            local_path = translate_docker_path(docker_path, _path_mappings)
            date_str = photo.get('fileCreatedAt', '')[:10]
            asset_id = photo.get('id', '')
            is_favorite = "⭐" if photo.get('isFavorite') else ""
            photo_url = f"{self.client.base_url}/photos/{asset_id}"

            # Mostrar ruta truncada pero con tooltip completo
            display_path = local_path if len(local_path) <= 60 else '...' + local_path[-57:]

            files_html += f"""
            <tr>
                <td class="file-num">{i}</td>
                <td class="file-fav">{is_favorite}</td>
                <td class="file-name"><a href="{photo_url}" target="_blank">{filename}</a></td>
                <td class="file-date">{date_str}</td>
                <td class="file-path" title="{local_path}">{display_path}</td>
            </tr>
            """

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Immich Wrapped {self.stats.year}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #fff;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }}

        .header {{
            text-align: center;
            margin-bottom: 60px;
        }}

        .header h1 {{
            font-size: 3.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}

        .header .year {{
            font-size: 6rem;
            font-weight: 900;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .section {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 24px;
            padding: 30px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .section-title {{
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: #a78bfa;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }}

        .stat-card {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
            border-radius: 16px;
            padding: 25px;
            text-align: center;
        }}

        .stat-number {{
            font-size: 3rem;
            font-weight: 900;
            color: #f5576c;
        }}

        .stat-label {{
            font-size: 1rem;
            color: #94a3b8;
            margin-top: 5px;
        }}

        .month-bar {{
            display: flex;
            align-items: center;
            margin-bottom: 12px;
        }}

        .month-name {{
            width: 100px;
            font-size: 0.9rem;
            color: #94a3b8;
        }}

        .bar {{
            height: 24px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            margin: 0 15px;
            min-width: 4px;
            transition: width 0.3s ease;
        }}

        .month-count {{
            font-weight: bold;
            color: #f5576c;
        }}

        .person-card {{
            display: flex;
            align-items: center;
            padding: 15px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            margin-bottom: 10px;
        }}

        .person-avatar {{
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-right: 15px;
        }}

        .person-name {{
            font-weight: bold;
        }}

        .person-count {{
            color: #94a3b8;
            font-size: 0.9rem;
        }}

        .place-item {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .place-item:last-child {{
            border-bottom: none;
        }}

        .place-count {{
            font-weight: bold;
            color: #f5576c;
        }}

        /* Etiquetas (Tags) */
        .tags-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .tag-badge {{
            display: inline-flex;
            align-items: center;
            padding: 8px 16px;
            border-radius: 20px;
            border: 1px solid;
            font-size: 0.9rem;
            font-weight: 500;
            transition: transform 0.2s ease;
        }}

        .tag-badge:hover {{
            transform: scale(1.05);
        }}

        .tag-count {{
            font-size: 0.8rem;
            opacity: 0.8;
            margin-left: 4px;
        }}

        /* Galería de fotos */
        .photo-gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }}

        .photo-card {{
            position: relative;
            border-radius: 12px;
            overflow: hidden;
            aspect-ratio: 1;
            background: rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .photo-card:hover {{
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }}

        .photo-card img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .photo-overlay {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 10px;
            background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .photo-card:hover .photo-overlay {{
            opacity: 1;
        }}

        .photo-date {{
            font-size: 0.8rem;
            color: #a78bfa;
        }}

        .photo-filename {{
            font-size: 0.85rem;
            font-weight: bold;
            color: #fff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .photo-path {{
            font-size: 0.65rem;
            color: #94a3b8;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-top: 4px;
        }}

        .photo-location {{
            font-size: 0.75rem;
            color: #94a3b8;
        }}

        /* Tabla de archivos */
        .files-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }}

        .files-table th {{
            text-align: left;
            padding: 12px 8px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.2);
            color: #a78bfa;
        }}

        .files-table td {{
            padding: 10px 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .files-table tr:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}

        .files-table a {{
            color: #667eea;
            text-decoration: none;
        }}

        .files-table a:hover {{
            color: #a78bfa;
            text-decoration: underline;
        }}

        .file-num {{
            color: #64748b;
            width: 40px;
        }}

        .file-fav {{
            width: 30px;
        }}

        .file-date {{
            color: #94a3b8;
            width: 100px;
        }}

        .file-path {{
            color: #64748b;
            font-size: 0.75rem;
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .toggle-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 15px;
            font-size: 0.9rem;
        }}

        .toggle-btn:hover {{
            opacity: 0.9;
        }}

        .collapsible {{
            display: none;
        }}

        .collapsible.show {{
            display: block;
        }}

        .footer {{
            text-align: center;
            padding: 40px;
            color: #64748b;
        }}

        @media (max-width: 600px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            .header h1 {{
                font-size: 2rem;
            }}

            .header .year {{
                font-size: 4rem;
            }}

            .photo-gallery {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🎁 Tu Immich Wrapped</h1>
            <div class="year">{self.stats.year}</div>
        </header>

        <section class="section">
            <h2 class="section-title">📊 Resumen del Año</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{self.stats.total_photos}</div>
                    <div class="stat-label">📷 Fotos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{self.stats.total_videos}</div>
                    <div class="stat-label">🎬 Videos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{self.stats.total_favorites}</div>
                    <div class="stat-label">⭐ Favoritos</div>
                </div>
            </div>
        </section>

        <section class="section">
            <h2 class="section-title">📅 Fotos por Mes</h2>
            {months_html}
        </section>

        <section class="section">
            <h2 class="section-title">👥 Personas más fotografiadas</h2>
            {people_html if people_html else '<p style="color: #94a3b8;">No se detectaron personas este año</p>'}
        </section>

        <section class="section">
            <h2 class="section-title">🌍 Lugares más visitados</h2>
            {places_html if places_html else '<p style="color: #94a3b8;">No hay información de ubicación disponible</p>'}
        </section>

        <section class="section">
            <h2 class="section-title">🏷️ Etiquetas</h2>
            <div class="tags-container">
                {tags_html if tags_html else '<p style="color: #94a3b8;">No hay etiquetas en las fotos de este año</p>'}
            </div>
        </section>

        <section class="section">
            <h2 class="section-title">⭐ Mejores Fotos del Año</h2>
            <p style="color: #94a3b8; margin-bottom: 20px;">Haz clic en una foto para verla en Immich</p>
            <div class="photo-gallery">
                {gallery_html if gallery_html else '<p style="color: #94a3b8;">No hay fotos seleccionadas</p>'}
            </div>
        </section>

        <section class="section">
            <h2 class="section-title">📁 Lista de Archivos</h2>
            <button class="toggle-btn" onclick="document.getElementById('files-table').classList.toggle('show')">
                Mostrar/Ocultar Lista de Archivos
            </button>
            <div id="files-table" class="collapsible">
                <table class="files-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>⭐</th>
                            <th>Nombre</th>
                            <th>Fecha</th>
                            <th>Ruta</th>
                        </tr>
                    </thead>
                    <tbody>
                        {files_html}
                    </tbody>
                </table>
            </div>
        </section>

        <footer class="footer">
            <p>Generado con ❤️ por Immich Wrapped</p>
            <p>Powered by Immich</p>
        </footer>
    </div>
</body>
</html>"""


# ============================================================================
# CREADOR DE ÁLBUM
# ============================================================================

class AlbumCreator:
    """Crea un álbum con las mejores fotos"""

    def __init__(self, client: ImmichClient, stats: WrappedStats):
        self.client = client
        self.stats = stats

    def create(self) -> Optional[dict]:
        """Crea el álbum del Wrapped"""
        if not self.stats.best_photos:
            print("❌ No hay fotos para crear el álbum")
            return None

        album_name = f"🎁 Wrapped {self.stats.year}"
        description = f"Las mejores {len(self.stats.best_photos)} fotos de {self.stats.year}"

        asset_ids = [photo['id'] for photo in self.stats.best_photos]

        try:
            album = self.client.create_album(
                name=album_name,
                description=description,
                asset_ids=asset_ids
            )
            print(f"\n📚 Álbum creado: {album_name}")
            print(f"   ID: {album.get('id')}")
            print(f"   Fotos: {len(asset_ids)}")
            return album
        except Exception as e:
            print(f"❌ Error creando álbum: {e}")
            return None


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='🎁 Immich Wrapped - Genera un resumen anual de tus fotos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python wrapped.py --year 2024 --api-key abc123
  python wrapped.py --year 2024 --api-key abc123 --create-album
  python wrapped.py --year 2024 --api-key abc123 --output reporte.html
        """
    )

    # Obtener valores por defecto desde .env
    default_api_key = os.environ.get('IMMICH_API_KEY', '')
    default_url = os.environ.get('IMMICH_URL', DEFAULT_BASE_URL)
    default_year = os.environ.get('WRAPPED_YEAR')

    if default_year:
        try:
            default_year = int(default_year)
        except ValueError:
            default_year = datetime.now().year - 1
    else:
        default_year = datetime.now().year - 1

    parser.add_argument(
        '--year', '-y',
        type=int,
        default=default_year,
        help=f'Año para generar el Wrapped (default: {default_year})'
    )

    parser.add_argument(
        '--api-key', '-k',
        type=str,
        default=default_api_key,
        help='API Key de Immich (obtener en Configuración > API Keys, o usar .env)'
    )

    parser.add_argument(
        '--url', '-u',
        type=str,
        default=default_url,
        help=f'URL base de Immich (default: {default_url})'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Ruta del archivo HTML de salida (default: wrapped_YEAR.html)'
    )

    parser.add_argument(
        '--create-album', '-a',
        action='store_true',
        help='Crear un álbum con las mejores fotos'
    )

    parser.add_argument(
        '--json',
        type=str,
        default=None,
        help='Exportar estadísticas a archivo JSON'
    )

    args = parser.parse_args()

    # Verificar que tenemos API key
    if not args.api_key:
        print("❌ Error: Se requiere una API Key.")
        print("   Opciones:")
        print("   1. Usar --api-key TU_API_KEY")
        print("   2. Crear un archivo .env con IMMICH_API_KEY=tu_api_key")
        print("   3. Copiar .env.example a .env y completar los valores")
        sys.exit(1)

    # Banner
    print("""
    ╔═══════════════════════════════════════════╗
    ║         🎁 IMMICH WRAPPED 🎁              ║
    ║      Tu resumen anual de fotos            ║
    ╚═══════════════════════════════════════════╝
    """)

    # Mostrar si se cargó desde .env
    if _env_vars:
        print(f"📋 Configuración cargada desde .env")

    # Crear cliente
    print(f"🔌 Conectando a {args.url}...")
    client = ImmichClient(args.url, args.api_key)

    if not client.validate_connection():
        sys.exit(1)

    # Generar Wrapped
    generator = WrappedGenerator(client, args.year)
    stats = generator.generate()

    if stats.total_photos + stats.total_videos == 0:
        print(f"\n❌ No se encontraron fotos ni videos para {args.year}")
        sys.exit(1)

    # Generar reporte HTML
    output_path = args.output or f"wrapped_{args.year}.html"
    html_generator = HTMLReportGenerator(stats, client)
    html_generator.generate(output_path)

    # Exportar JSON si se solicita
    if args.json:
        json_data = {
            'year': stats.year,
            'total_photos': stats.total_photos,
            'total_videos': stats.total_videos,
            'total_favorites': stats.total_favorites,
            'photos_by_month': {
                m: {'name': d['name'], 'count': d['count']}
                for m, d in stats.photos_by_month.items()
            },
            'top_people': stats.top_people,
            'top_cities': stats.top_cities,
            'top_countries': stats.top_countries,
            'best_photo_ids': [p['id'] for p in stats.best_photos]
        }

        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"📊 Estadísticas exportadas a: {args.json}")

    # Crear álbum si se solicita
    if args.create_album:
        album_creator = AlbumCreator(client, stats)
        album_creator.create()

    # Resumen final
    print("\n" + "=" * 50)
    print(f"🎉 ¡Wrapped {args.year} completado!")
    print(f"   📷 {stats.total_photos} fotos")
    print(f"   🎬 {stats.total_videos} videos")
    print(f"   ⭐ {stats.total_favorites} favoritos")
    print(f"   📄 Reporte: {output_path}")
    print("=" * 50)


if __name__ == '__main__':
    main()
