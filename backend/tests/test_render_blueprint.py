"""render.yaml, the one-click free deploy, only names settings and routes that exist."""

import re

from app.config import REPO_ROOT, Settings

BLUEPRINT = (REPO_ROOT / "render.yaml").read_text()
# Read by the platform or the image build, not by Settings.
PLATFORM_KEYS = {"PORT", "DEMO_DB_URL"}


def test_every_env_var_is_a_setting_the_app_reads():
    keys = re.findall(r"^\s*- key: (\w+)$", BLUEPRINT, re.MULTILINE)

    assert {"CALA_MODE", "LLM_MODE", "GEMINI_API_KEY", "OPENAI_COMPAT_API_KEY"} <= set(keys)
    unknown = {k for k in keys if k not in PLATFORM_KEYS and k.lower() not in Settings.model_fields}
    assert unknown == set()


def test_the_health_check_is_a_real_route(client):
    path = re.search(r"healthCheckPath: (\S+)", BLUEPRINT).group(1)

    assert client.get(path).status_code == 200


def test_the_service_listens_where_the_image_does():
    port = re.search(r'key: PORT\n\s+value: "(\d+)"', BLUEPRINT).group(1)
    dockerfile = (REPO_ROOT / "Dockerfile").read_text()

    assert f'"--port", "{port}"' in dockerfile
