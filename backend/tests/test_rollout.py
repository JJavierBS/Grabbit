"""deploy/rollout.sh: blue/green switch on the EC2 host, run against fake docker and curl."""

import os
import subprocess
from pathlib import Path

import pytest

from app.config import REPO_ROOT

ROLLOUT = REPO_ROOT / "deploy" / "rollout.sh"

# Containers are files in $FAKE_STATE/containers; each reload records the upstream it saw.
FAKE_DOCKER = r"""#!/usr/bin/env bash
echo "docker $*" >> "$FAKE_STATE/log"
c="$FAKE_STATE/containers"
last="${!#}"
case "$1" in
  network)
    [ "$2" = create ] && touch "$FAKE_STATE/network"
    [ -f "$FAKE_STATE/network" ] ;;
  inspect)
    [ -f "$c/$last" ] || exit 1
    case "$3" in
      *Running*) echo true ;;
      *Health*) cat "$c/$last" ;;
    esac ;;
  run)
    name="$(sed -n 's/.*--name \([^ ]*\).*/\1/p' <<< "$*")"
    if [ "$name" = grabbit-edge ]; then echo none > "$c/$name"
    else echo "${FAKE_NEW_HEALTH:-healthy}" > "$c/$name"; fi ;;
  rm) rm -f "$c/$last" ;;
  exec) cat "$GRABBIT_ROOT/edge/upstream.caddy" >> "$FAKE_STATE/reloads" ;;
esac
exit 0
"""

FAKE_CURL = """#!/usr/bin/env bash
echo "curl $*" >> "$FAKE_STATE/log"
exit "${FAKE_CURL_EXIT:-0}"
"""


@pytest.fixture
def host(tmp_path: Path) -> dict[str, Path]:
    bin_dir, state, root = tmp_path / "bin", tmp_path / "state", tmp_path / "root"
    for path in (bin_dir, state / "containers", root):
        path.mkdir(parents=True)
    for name, body in (("docker", FAKE_DOCKER), ("curl", FAKE_CURL)):
        (bin_dir / name).write_text(body)
        (bin_dir / name).chmod(0o755)
    (root / ".env").write_text("GEMINI_API_KEY=x\n")
    return {"bin": bin_dir, "state": state, "root": root}


def rollout(host: dict[str, Path], **env: str) -> subprocess.CompletedProcess[str]:
    full_env = {
        **os.environ,
        "PATH": f"{host['bin']}{os.pathsep}{os.environ['PATH']}",
        "FAKE_STATE": str(host["state"]),
        "GRABBIT_ROOT": str(host["root"]),
        "POLL_INTERVAL": "0",
        **env,
    }
    return subprocess.run(
        ["bash", str(ROLLOUT), "ghcr.io/example/grabbit:abc"],
        env=full_env,
        capture_output=True,
        text=True,
        check=False,
    )


def running(host: dict[str, Path]) -> set[str]:
    return {p.name for p in (host["state"] / "containers").iterdir()}


def active(host: dict[str, Path]) -> str:
    return (host["root"] / "active").read_text().strip()


def upstream(host: dict[str, Path]) -> str:
    return (host["root"] / "edge" / "upstream.caddy").read_text().strip()


def log(host: dict[str, Path]) -> list[str]:
    return (host["state"] / "log").read_text().splitlines()


def test_first_deploy_starts_the_edge_and_goes_live_on_blue(host):
    result = rollout(host)

    assert result.returncode == 0, result.stderr
    assert running(host) == {"grabbit-edge", "grabbit-blue"}
    assert active(host) == "blue"
    assert upstream(host) == "reverse_proxy grabbit-blue:8000"
    assert (host["root"] / "edge" / "Caddyfile").is_file()
    run_new = next(line for line in log(host) if "--name grabbit-blue" in line)
    assert f"--env-file {host['root']}/.env -e DATABASE_PATH=/app/data/grabbit.db" in run_new
    assert f"-v {host['root']}/data:/app/data" in run_new


def test_next_deploy_switches_to_green_before_stopping_blue(host):
    rollout(host)
    result = rollout(host)

    assert result.returncode == 0, result.stderr
    assert running(host) == {"grabbit-edge", "grabbit-green"}
    assert active(host) == "green"
    reloads = (host["state"] / "reloads").read_text().splitlines()
    assert reloads[-1] == "reverse_proxy grabbit-green:8000"
    lines = log(host)
    last_reload = max(i for i, line in enumerate(lines) if line.startswith("docker exec"))
    stop_blue = lines.index("docker stop -t 30 grabbit-blue")
    assert last_reload < stop_blue
    assert sum("--name grabbit-edge" in line for line in lines) == 1


def test_unhealthy_new_container_leaves_the_live_one_serving(host):
    rollout(host)
    result = rollout(host, FAKE_NEW_HEALTH="unhealthy")

    assert result.returncode == 1
    assert running(host) == {"grabbit-edge", "grabbit-blue"}
    assert active(host) == "blue"
    assert upstream(host) == "reverse_proxy grabbit-blue:8000"
    assert "docker stop -t 30 grabbit-blue" not in log(host)


def test_failed_check_through_the_edge_rolls_traffic_back(host):
    rollout(host)
    result = rollout(host, FAKE_CURL_EXIT="7")

    assert result.returncode == 1
    assert running(host) == {"grabbit-edge", "grabbit-blue"}
    assert active(host) == "blue"
    assert upstream(host) == "reverse_proxy grabbit-blue:8000"
    reloads = (host["state"] / "reloads").read_text().splitlines()
    assert reloads[-2:] == ["reverse_proxy grabbit-green:8000", "reverse_proxy grabbit-blue:8000"]
    assert "docker stop -t 30 grabbit-blue" not in log(host)
