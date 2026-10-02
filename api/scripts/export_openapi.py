"""Export the API's OpenAPI schema to a JSON file.

Used by the web client to generate TypeScript types (see `npm run gen:api`).
Usage: uv run python -m scripts.export_openapi <output-path>
"""

import json
import sys
from pathlib import Path

from app.main import app


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m scripts.export_openapi <output-path>")

    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(app.openapi(), indent=2) + "\n")
    print(f"OpenAPI schema written to {output}")


if __name__ == "__main__":
    main()
