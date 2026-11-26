# Sala WorkAdventure via Git (GitHub Pages)

Esta sala é publicada automaticamente pelo **GitHub Pages** a cada `git push` na branch `main`, sem precisar alterar nada na VPS.

## Estrutura

- `maps/sala.tmj` — Mapa editável no **Tiled**
- `maps/sala.wam` — Wrapper WorkAdventure (áreas/entidades versionadas no Git)
- `tilesets/` — Arquivos `.tsx` e `.png` dos tilesets
- `scripts/build_map.py` — Converte `sala.tmj` → `dist/sala.json` com referências externas de PNG
- `scripts/validate_map.py` — Valida o build antes de publicar
- `.github/workflows/deploy-pages.yml` — Faz build, valida e publica `dist/` no GitHub Pages

## Como editar e testar localmente

1. Abra `maps/sala.tmj` no **Tiled**, edite e salve.
2. Rode localmente para gerar e validar `dist/`:
   ```powershell
   python scripts/build_map.py
   python scripts/validate_map.py dist
   ```
3. Faça commit e push para `main`:
   ```powershell
   git add .
   git commit -m "Atualiza sala"
   git push origin main
   ```

## Como ativar no GitHub (primeira vez)

1. Crie um repositório no GitHub (público, para o GitHub Pages gratuito) e suba este projeto.
2. No repositório do GitHub, vá em **Settings → Pages**.
3. Em **Build and deployment → Source**, selecione **GitHub Actions**.
4. Aguarde o workflow `Deploy Sala WorkAdventure (GitHub Pages)` terminar com sucesso na aba **Actions**.

## URL da sala no WorkAdventure

Depois que o GitHub Pages publicar, acesse pelo seu servidor WorkAdventure usando:

```text
https://work.kdst.com.br/_/global/<SEU-USUARIO>.github.io/<NOME-DO-REPO>/sala.wam
```

> **Dica:** Após um novo `git push`, aguarde ~30s o workflow finalizar e dê `Ctrl + Shift + R` no navegador para evitar cache antigo do mapa.
