import json
import os
import sys

class MapValidator:
    def __init__(self, directory):
        self.dir = directory
        self.errors = []
        self.warnings = []
        self.info = []

    def err(self, msg):
        self.errors.append(f"  [ERRO] {msg}")

    def warn(self, msg):
        self.warnings.append(f"  [AVISO] {msg}")

    def ok(self, msg):
        self.info.append(f"  [OK] {msg}")

    def find_files(self):
        json_files = [f for f in os.listdir(self.dir) if f.endswith('.json') and not f.endswith('.wam')]
        wam_files = [f for f in os.listdir(self.dir) if f.endswith('.wam')]
        png_files = [f for f in os.listdir(self.dir) if f.endswith('.png')]
        tsx_files = [f for f in os.listdir(self.dir) if f.endswith('.tsx')]
        return json_files, wam_files, png_files, tsx_files

    def validate_wam(self, wam_path):
        print(f"\n[2] Validando WAM: {os.path.basename(wam_path)}")
        with open(wam_path, 'r') as f:
            wam = json.load(f)

        if wam.get('version') != '1.0.0':
            self.err(f"WAM version={wam.get('version')}, esperado '1.0.0'")
        else:
            self.ok("WAM version 1.0.0")

        map_url = wam.get('mapUrl')
        if not map_url:
            self.err("WAM sem mapUrl")
        else:
            map_path = os.path.join(self.dir, map_url)
            if os.path.exists(map_path):
                self.ok(f"mapUrl '{map_url}' existe")
            else:
                self.err(f"mapUrl '{map_url}' NAO encontrado")
            if '/' in map_url or '\\' in map_url:
                self.err(f"mapUrl deve ser relativo sem subdiretorios: '{map_url}'")

        if wam.get('areas') is not None:
            self.ok(f"WAM tem {len(wam['areas'])} areas")

    def validate_json(self, json_path, png_files):
        print(f"\n[3] Validando JSON: {os.path.basename(json_path)}")
        with open(json_path, 'r') as f:
            data = json.load(f)

        required = ['width', 'height', 'layers', 'tilesets', 'orientation', 'type', 'version']
        for key in required:
            if key in data:
                self.ok(f"Campo '{key}' presente")
            else:
                self.err(f"Campo '{key}' AUSENTE")

        if data.get('orientation') != 'orthogonal':
            self.err(f"orientation='{data.get('orientation')}', esperado 'orthogonal'")
        else:
            self.ok("orientation = orthogonal")

        if data.get('infinite') is True:
            self.err("Mapa infinite=true NAO suportado pelo WA")
        else:
            self.ok("infinite = false")

        width = data.get('width', 0)
        height = data.get('height', 0)
        print(f"  [INFO] Mapa {width}x{height} ({width*height} tiles)")

        self.validate_tilesets(data.get('tilesets', []), png_files)
        self.validate_layers(data.get('layers', []), data.get('tilesets', []))

    def validate_tilesets(self, tilesets, png_files):
        print(f"\n[4] Validando Tilesets ({len(tilesets)} encontrados)")
        if not tilesets:
            self.err("Nenhum tileset encontrado")
            return

        prev_gid = 1
        for i, ts in enumerate(tilesets):
            name = ts.get('name', f'tileset_{i}')
            firstgid = ts.get('firstgid')
            tilecount = ts.get('tilecount', 0)
            image = ts.get('image', '')
            columns = ts.get('columns', 0)

            print(f"\n  Tileset: '{name}' (firstgid={firstgid}, {tilecount} tiles)")

            if firstgid != prev_gid:
                self.warn(f"firstgid={firstgid}, esperado {prev_gid} (gap entre tilesets)")

            if not image:
                self.err(f"Tileset '{name}' sem campo 'image'")
                continue

            if image.startswith('data:'):
                self.err(f"Tileset '{name}' usa BASE64! Use PNG externo.")
                continue

            if image in png_files:
                self.ok(f"Tileset '{name}': imagem '{image}' existe")
            else:
                self.err(f"Tileset '{name}': imagem '{image}' NAO encontrada no diretorio")
                print(f"  PNGs disponiveis: {png_files}")

            img_w = ts.get('imagewidth', 0)
            img_h = ts.get('imageheight', 0)
            tw = ts.get('tilewidth', 32)
            th = ts.get('tileheight', 32)

            expected_cols = img_w // tw if tw > 0 else 0
            expected_rows = img_h // th if th > 0 else 0
            expected_count = expected_cols * expected_rows

            if columns != expected_cols:
                self.warn(f"columns={columns}, esperado {expected_cols} (imagewidth/{tw})")

            if tilecount != expected_count:
                self.warn(f"tilecount={tilecount}, esperado {expected_count} ({expected_cols}x{expected_rows})")

            tiles = ts.get('tiles', [])
            collides_count = sum(1 for t in tiles if any(
                p.get('name') == 'collides' and p.get('value') == True
                for p in t.get('properties', [])
            ))
            if collides_count > 0:
                self.ok(f"  {collides_count} tiles com colisao")

            animated_count = sum(1 for t in tiles if 'animation' in t)
            if animated_count > 0:
                self.ok(f"  {animated_count} tiles animados")
            elif tilecount > 0:
                self.warn(f"  Nenhum tile animado (se esperado, adicione 'animation' no build)")

            prev_gid = firstgid + tilecount

    def validate_layers(self, layers, tilesets):
        print(f"\n[5] Validando Layers ({len(layers)} encontrados)")
        if not layers:
            self.err("Nenhuma layer encontrada")
            return

        has_spawn = False
        tile_layer_count = 0
        object_layer_count = 0

        for i, layer in enumerate(layers):
            name = layer.get('name', f'layer_{i}')
            ltype = layer.get('type', 'unknown')

            if ltype == 'tilelayer':
                tile_layer_count += 1
                data = layer.get('data', [])
                non_zero = sum(1 for x in data if x != 0)
                expected = layer.get('width', 0) * layer.get('height', 0)
                if len(data) != expected:
                    self.err(f"Layer '{name}': data tem {len(data)} tiles, esperado {expected}")
                else:
                    self.ok(f"Layer '{name}' (tilelayer): {non_zero}/{expected} tiles usados")

            elif ltype == 'objectgroup':
                object_layer_count += 1
                objects = layer.get('objects', [])
                print(f"  Layer '{name}' (objectgroup): {len(objects)} objetos")

                for obj in objects:
                    if obj.get('type') == 'spawn':
                        has_spawn = True
                        x = obj.get('x', 0)
                        y = obj.get('y', 0)
                        self.ok(f"Spawn point encontrado em ({x}, {y})")

                    if 'gid' in obj:
                        gid = obj['gid']
                        x = obj.get('x', 0)
                        y = obj.get('y', 0)
                        w = obj.get('width', 0)
                        h = obj.get('height', 0)
                        if w == 0 or h == 0:
                            self.warn(f"Objeto gid={gid} em ({x},{y}) com width=0 ou height=0")
            else:
                self.warn(f"Layer '{name}' tipo desconhecido: '{ltype}'")

        if not has_spawn:
            self.err("Nenhum spawn point encontrado (layer 'start' com tipo='spawn')")

        print(f"\n  Resumo: {tile_layer_count} tilelayers, {object_layer_count} objectlayers")

    def run(self):
        print("=" * 60)
        print("VALIDADOR DE MAPAS WORKADVENTURE")
        print("=" * 60)
        print(f"Diretorio: {self.dir}")

        if not os.path.isdir(self.dir):
            print(f"\n[ERRO] Diretorio nao existe: {self.dir}")
            return False

        json_files, wam_files, png_files, tsx_files = self.find_files()

        print(f"\n[1] Arquivos encontrados:")
        print(f"  JSON: {json_files or 'nenhum'}")
        print(f"  WAM:  {wam_files or 'nenhum'}")
        print(f"  PNG:  {png_files or 'nenhum'}")
        print(f"  TSX:  {tsx_files or 'nenhum'}")

        if not wam_files:
            self.err("Nenhum arquivo .wam encontrado")
        if not json_files:
            self.err("Nenhum arquivo .json encontrado")

        for wam_file in wam_files:
            self.validate_wam(os.path.join(self.dir, wam_file))

        for json_file in json_files:
            self.validate_json(os.path.join(self.dir, json_file), png_files)

        print("\n" + "=" * 60)
        print("RESULTADO")
        print("=" * 60)

        if self.info:
            print("\n--- OK ---")
            for msg in self.info:
                print(msg)

        if self.warnings:
            print("\n--- AVISOS ---")
            for msg in self.warnings:
                print(msg)

        if self.errors:
            print("\n--- ERROS ---")
            for msg in self.errors:
                print(msg)

        print(f"\nTotal: {len(self.info)} OK, {len(self.warnings)} avisos, {len(self.errors)} erros")

        if self.errors:
            print("\n>> FALHOU - Corrija os erros antes de subir pro servidor")
            return False
        else:
            print("\n>> TUDO CERTO - Pode subir pro servidor!")
            return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python validate_map.py <diretorio_do_mapa>")
        print("Ex:  python validate_map.py D:\\Projetos\\VPS do Toreh\\work3")
        sys.exit(1)

    validator = MapValidator(sys.argv[1])
    success = validator.run()
    sys.exit(0 if success else 1)
