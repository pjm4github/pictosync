"""
plantuml/renderer.py

Render .puml files to PNG or SVG using a local PlantUML Java JAR.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def find_plantuml_jar() -> str | None:
    """Find the PlantUML JAR file.

    Search order:
        1. PictoSync settings (external_tools.plantuml_jar_path)
        2. PLANTUML_JAR environment variable
        3. plantuml.jar in the PictoSync project directory
        4. plantuml.jar on system PATH

    Returns:
        Path to plantuml.jar if found, None otherwise.
    """
    # 1. PictoSync settings
    try:
        from settings import get_settings
        configured = get_settings().settings.external_tools.plantuml_jar_path
        if configured and os.path.isfile(configured):
            return configured
    except Exception:
        pass

    # 2. Environment variable
    env_jar = os.environ.get("PLANTUML_JAR")
    if env_jar and os.path.isfile(env_jar):
        return env_jar

    # 3. Project directory (next to main.py)
    project_dir = Path(__file__).resolve().parent.parent
    local_jar = project_dir / "plantuml.jar"
    if local_jar.is_file():
        return str(local_jar)

    # 4. On system PATH
    path_jar = shutil.which("plantuml.jar")
    if path_jar:
        return path_jar

    return None


def _render_puml(puml_path: str, fmt: str, output_path: str | None = None) -> str:
    """Render a .puml file to the specified format using PlantUML.

    Args:
        puml_path: Path to the .puml source file.
        fmt: Output format flag for PlantUML (e.g. ``png``, ``svg``).
        output_path: Optional explicit output path.  If None, the output is
            placed next to the .puml file using the file stem as name.

    Returns:
        Path to the generated output file.

    Raises:
        RuntimeError: If Java or the PlantUML JAR cannot be found,
            or if rendering fails.
    """
    jar = find_plantuml_jar()
    if jar is None:
        raise RuntimeError(
            "PlantUML JAR not found.\n\n"
            "Place plantuml.jar in the PictoSync directory, or set the\n"
            "PLANTUML_JAR environment variable to its path.\n\n"
            "Download from: https://github.com/plantuml/plantuml/releases\n\n"
            "Save the file (something like plantuml-1.2026.1.jar) as plantuml.jar"
        )

    # Verify Java is available (settings → PATH)
    java = None
    try:
        from settings import get_settings
        configured = get_settings().settings.external_tools.java_path
        if configured and os.path.isfile(configured):
            java = configured
    except Exception:
        pass
    if java is None:
        java = shutil.which("java")
    if java is None:
        raise RuntimeError(
            "Java not found on PATH.\n\n"
            "PlantUML requires a Java runtime (JRE 8+).\n"
            "Install from: https://adoptium.net/"
        )

    puml = Path(puml_path).resolve()
    if not puml.is_file():
        raise RuntimeError(f"PUML file not found: {puml}")

    # Render into a temp directory so we don't have to guess the output
    # filename — PlantUML uses the @startuml diagram name, not the file stem.
    tmp_dir = tempfile.mkdtemp(prefix="pictosync_puml_")

    cmd = [
        java, "-jar", jar,
        f"-t{fmt}",
        "-o", tmp_dir,
        str(puml),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise RuntimeError(
            f"PlantUML rendering failed (exit {result.returncode}):\n"
            f"{result.stderr.strip()}"
        )

    # Find whatever file of the target format was generated
    generated_files = list(Path(tmp_dir).glob(f"*.{fmt}"))
    if not generated_files:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise RuntimeError(
            f"PlantUML ran successfully but produced no {fmt.upper()} output.\n"
            f"Command: {' '.join(cmd)}\n"
            f"stdout: {result.stdout.strip()}\n"
            f"stderr: {result.stderr.strip()}"
        )

    generated = generated_files[0]

    # Decide final destination
    if output_path:
        final = Path(output_path).resolve()
    else:
        final = puml.with_suffix(f".{fmt}")

    shutil.copy2(str(generated), str(final))
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return str(final)


def render_puml_to_png(puml_path: str, output_png: str | None = None) -> str:
    """Render a .puml file to PNG using PlantUML.

    Args:
        puml_path: Path to the .puml source file.
        output_png: Optional explicit output path.  If None, the PNG is
            placed next to the .puml file using the file stem as name.

    Returns:
        Path to the generated PNG file.

    Raises:
        RuntimeError: If Java or the PlantUML JAR cannot be found,
            or if rendering fails.
    """
    return _render_puml(puml_path, "png", output_png)


def render_puml_to_svg(puml_path: str, output_svg: str | None = None) -> str:
    """Render a .puml file to SVG using PlantUML.

    Args:
        puml_path: Path to the .puml source file.
        output_svg: Optional explicit output path.  If None, the SVG is
            placed next to the .puml file using the file stem as name.

    Returns:
        Path to the generated SVG file.

    Raises:
        RuntimeError: If Java or the PlantUML JAR cannot be found,
            or if rendering fails.
    """
    return _render_puml(puml_path, "svg", output_svg)
