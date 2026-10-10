import json
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def test_project_urls_apontam_para_o_repositorio_do_server_json():
    projeto = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    repositorio = json.loads((RAIZ / "server.json").read_text(encoding="utf-8"))["repository"][
        "url"
    ]

    assert projeto["urls"]
    for url in projeto["urls"].values():
        assert url == repositorio or url.startswith(f"{repositorio}/")
