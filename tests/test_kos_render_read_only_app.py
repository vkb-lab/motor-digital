from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_app_render_exists_and_is_read_only_safe():
    path = ROOT / "app_render.py"
    assert path.exists()

    text = path.read_text(encoding="utf-8")
    lower = text.lower()

    assert "subprocess" not in lower
    assert "local_runtime" not in lower
    assert "token_gmail" not in lower
    assert "client_secret" not in lower
    assert ".env" not in lower
    assert "K-OS Cloud Status" in text


def test_render_yaml_points_to_read_only_app():
    text = (ROOT / "render.yaml").read_text(encoding="utf-8")

    assert "app_render.py" in text
    assert "requirements-render.txt" in text
    assert "streamlit run app_render.py --server.port $PORT --server.address 0.0.0.0" in text


def test_requirements_render_is_minimal():
    path = ROOT / "requirements-render.txt"
    assert path.exists()

    deps = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    assert deps == ["streamlit"]
