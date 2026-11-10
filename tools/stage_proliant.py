"""Create a credential-free deployment archive; upload/install after the host returns."""

from hashlib import sha256
import json
from pathlib import Path
import tarfile


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / "artifacts" / "proliant-deploy"
    output.mkdir(parents=True, exist_ok=True)
    archive = output / "live-explain-recruitment.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:

        def clean(info):
            return (
                None
                if any(p in {"__pycache__", ".pytest_cache", ".ruff_cache"} for p in Path(info.name).parts)
                else info
            )

        for name in (
            "pyproject.toml",
            "uv.lock",
            "README.md",
            "RECRUITMENT.md",
            "DESIGN_REVIEW.md",
            "src",
            "deploy",
            "tests",
            "tools",
            "run",
            "start-recruitment",
        ):
            tar.add(root / name, arcname=name, filter=clean)
    digest = sha256(archive.read_bytes()).hexdigest()
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "archive": archive.name,
                "sha256": digest,
                "target": "/opt/live-explain-recruitment",
                "unit": "live-explain-recruitment.service",
                "audience_url": "https://prol.aridlin.pl/live-explain/",
                "presenter_url": "https://prol.aridlin.pl/live-explain/presenter/",
                "status": "prepared; server upload, portal integration and WAN verification pending",
            },
            indent=2,
        )
        + "\n"
    )
    print(archive)
    print(digest)


if __name__ == "__main__":
    main()
