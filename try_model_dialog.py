"""
try_model_dialog.py

Self-contained "Try a Model on an Image" harness for the multi-provider
extraction seam. Lets the user:

  * pick a vision provider (Gemini / OpenAI / Anthropic),
  * point the app at the environment variable that holds that provider's
    API key (the name is editable and persisted),
  * pick / fetch / type a model id,
  * run extraction on a chosen image, and
  * view, copy, save, or send the returned schema JSON to the canvas.

It reuses the provider-neutral :class:`gemini.worker.ExtractWorker`, so the
API call, prompt and validation are identical to the main canvas flow.
"""

from __future__ import annotations

import json
import os
import tempfile
from typing import Callable, Optional

from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QFont
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QAbstractItemView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gemini import ExtractWorker, FocusedAlignWorker
from providers import (
    all_specs,
    classify_provider_error,
    get_provider,
    get_spec,
    resolve_api_key,
)
from providers.base import ProviderError

_IMAGE_FILTER = "Images (*.png *.jpg *.jpeg *.webp *.gif);;All files (*)"

# Shape kinds whose placement a focused ROI pass can meaningfully refine.
_REFINABLE_KINDS = {"rect", "roundedrect", "ellipse", "hexagon", "cylinder",
                    "blockarrow", "polygon", "line"}

# Recommended extra-instructions prefilled into the context box in Plain mode.
# Pairs with the "plain" prompt framing + 15° angle snapping.
_PLAIN_DEFAULT_CONTEXT = '''This is an architectural FLOOR PLAN. Extract EVERY element you can see — do not stop early and do not summarize. Work in this order:

1. TEXT — capture all text first so none is missed: room names/labels, and especially dimension strings (e.g. "16 x 8' DOOR", 12'-6", scale notes). Put text inside a room as that rectangle's meta.label. NEVER discard a dimension string, note, or callout: if a piece of text is NOT inside a shape (a freestanding dimension, door/window callout, title block, or scale note), you MUST still emit it as its own standalone "text" item at its pixel location — do not drop it and do not force it into an unrelated room's label. Every readable string in the image must appear exactly once in the output, either as a shape's meta.label or as a "text" item.

2. RECTANGLES — every room, wall block, and panel as a "rect". Many are drawn at an angle: set geom.angle (degrees clockwise). The plan is on a 15° grid, so angles will be near 0/15/30/45/… — report your best estimate and it will be snapped. geom.w and geom.h are the room's own upright side lengths; x,y is the top-left of that upright box at the room's center.

3. LINES — walls, partitions, and connectors as "line" at the same 15° angles. Only add arrowheads if they are actually drawn.

Rules:
- Trace what is literally drawn. Do NOT invent software/architecture meaning.
- Ignore furniture, fixtures, hatching/shading, shadows, and dimension arrows.
- Prefer accurate edges over guessing: a rectangle's bounding box must overlay the real walls exactly.
- Be exhaustive — include small rooms, closets, and porches too.'''


class _RefineBatchWorker(QObject):
    """Refines several annotations one-by-one via :class:`FocusedAlignWorker`.

    Runs on its own thread and drives each per-shape worker synchronously, so a
    whole extraction can be re-aligned against the source image with a single
    background task and a running progress count.

    Signals:
        progress(int, int, str): (completed, total, message).
        shape_done(int, dict): (annotation index, refined record).
        finished(int, int): (refined_count, failed_count).
    """

    progress = pyqtSignal(int, int, str)
    shape_done = pyqtSignal(int, dict)
    finished = pyqtSignal(int, int)

    def __init__(self, png_path: str, model: str, provider_id: str,
                 env_key: str, records: list, indices: list,
                 max_iterations: int = 1):
        super().__init__()
        self._png = png_path
        self._model = model
        self._pid = provider_id
        self._env = env_key
        self._records = records
        self._indices = indices
        self._iters = max_iterations
        self._cancel = False

    def cancel(self) -> None:
        """Request a stop after the in-flight shape finishes."""
        self._cancel = True

    def run(self) -> None:
        refined = 0
        failed = 0
        total = len(self._indices)
        for pos, idx in enumerate(self._indices):
            if self._cancel:
                break
            rec = self._records[idx]
            kind = rec.get("kind", "shape")
            self.progress.emit(pos, total, f"Refining {kind} {pos + 1}/{total}…")
            try:
                worker = FocusedAlignWorker(
                    self._png, self._model, rec,
                    max_iterations=self._iters,
                    provider_id=self._pid, env_key=self._env)
                worker.run()  # synchronous in this thread
                if worker.error or not worker.result:
                    failed += 1
                    continue
                self.shape_done.emit(idx, worker.result)
                refined += 1
            except Exception:
                failed += 1
        self.progress.emit(total, total, "Refinement complete.")
        self.finished.emit(refined, failed)


class TryModelDialog(QDialog):
    """Modeless-friendly dialog that runs one extraction and shows the schema."""

    def __init__(self, settings_manager, parent: Optional[QWidget] = None,
                 image_path: str = "",
                 on_send_to_canvas: Optional[Callable[[dict], None]] = None):
        """
        Args:
            settings_manager: The app SettingsManager (for ``ai_providers``).
            parent: Parent widget.
            image_path: Optional initial image to prefill.
            on_send_to_canvas: Optional callback invoked with the parsed schema
                dict when the user clicks "Send to Canvas".
        """
        super().__init__(parent)
        self.settings_manager = settings_manager
        self._on_send = on_send_to_canvas
        self._thread: Optional[QThread] = None
        self._worker: Optional[ExtractWorker] = None
        self._refine_thread: Optional[QThread] = None
        self._refine_worker: Optional[_RefineBatchWorker] = None
        self._last_result: Optional[dict] = None
        self._last_tokens: int = 0
        self._last_prompt: str = ""
        self._last_raw: str = ""
        self._run_meta: dict = {}
        # The exact text we last auto-filled into the context box, so a mode
        # switch only replaces its own default and never the user's own text.
        self._autofilled_context: str = ""

        from prompt_log import default_log
        self._prompt_log = default_log(settings_manager)

        self.setWindowTitle("Try a Model on an Image")
        self.resize(720, 720)
        self._build_ui()
        self._load_provider_into_ui(self._ai().active)
        if image_path:
            self.image_edit.setText(image_path)

    # ── settings helpers ──────────────────────────────────────────────────

    def _ai(self):
        return self.settings_manager.settings.ai_providers

    def _provider_cfg(self, pid: str):
        cfg = self._ai().providers.get(pid)
        if cfg is None:
            from settings import AIProviderConfig
            cfg = AIProviderConfig(env_key=get_spec(pid).default_env_key)
            self._ai().providers[pid] = cfg
        return cfg

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        intro = QLabel(
            "Pick a provider and model, point it at an image, and run. The "
            "extracted schema appears below — send it to the canvas or save "
            "it. API keys are read from an environment variable whose name "
            "you control per provider.")
        intro.setWordWrap(True)
        intro.setStyleSheet("color:#555; font-size:11px;")
        root.addWidget(intro)

        # Provider row
        prov_row = QHBoxLayout()
        prov_row.addWidget(QLabel("Provider:"))
        self.provider_combo = QComboBox()
        for spec in all_specs():
            self.provider_combo.addItem(spec.label, spec.id)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        prov_row.addWidget(self.provider_combo, 1)
        self.setup_btn = QPushButton("Set up / Connect…")
        self.setup_btn.setToolTip(
            "Walk through installing the provider library and setting its "
            "API key.")
        self.setup_btn.clicked.connect(self._open_setup_wizard)
        prov_row.addWidget(self.setup_btn)
        self.docs_btn = QPushButton("Model docs…")
        self.docs_btn.clicked.connect(self._open_docs)
        prov_row.addWidget(self.docs_btn)
        root.addLayout(prov_row)

        # Env-key-name row (the "key pattern" the user controls)
        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("API key env var:"))
        self.env_edit = QLineEdit()
        self.env_edit.setPlaceholderText("e.g. PICTOSYNC_GEMINI_KEY")
        self.env_edit.editingFinished.connect(self._on_env_edited)
        key_row.addWidget(self.env_edit, 1)
        self.env_status = QLabel("")
        self.env_status.setStyleSheet("font-size:11px;")
        key_row.addWidget(self.env_status)
        root.addLayout(key_row)

        # Model row
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        model_row.addWidget(self.model_combo, 1)
        self.fetch_btn = QPushButton("Fetch models…")
        self.fetch_btn.setToolTip(
            "Ask the provider which models your key can use.")
        self.fetch_btn.clicked.connect(self._fetch_models)
        model_row.addWidget(self.fetch_btn)
        root.addLayout(model_row)

        # Image row
        img_row = QHBoxLayout()
        img_row.addWidget(QLabel("Image:"))
        self.image_edit = QLineEdit()
        self.image_edit.setPlaceholderText("Path to a PNG/JPG diagram…")
        img_row.addWidget(self.image_edit, 1)
        self.browse_btn = QPushButton("Browse…")
        self.browse_btn.clicked.connect(self._browse_image)
        img_row.addWidget(self.browse_btn)
        root.addLayout(img_row)

        # Extra instructions / context
        ctx_head = QHBoxLayout()
        ctx_head.addWidget(QLabel("Extra instructions for the model (optional):"))
        ctx_head.addStretch()
        self.history_btn = QPushButton("History…")
        self.history_btn.setToolTip(
            "Recall, refine and reuse prompts you've run before.")
        self.history_btn.clicked.connect(self._open_history)
        ctx_head.addWidget(self.history_btn)
        root.addLayout(ctx_head)

        self.context_edit = QPlainTextEdit()
        self.context_edit.setPlaceholderText(
            "e.g. Ignore the colors. Find rectangles drawn at an angle (in 15° "
            "increments) and preserve each angle. Then find lines at those same "
            "angles. Also extract ALL text: room names and dimension labels "
            "(like \"16 x 8' DOOR\") as text items.")
        self.context_edit.setFixedHeight(80)
        root.addWidget(self.context_edit)

        # Extraction options: framing mode + angle snapping
        opt_row = QHBoxLayout()
        opt_row.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Architecture (C4)", "c4")
        self.mode_combo.addItem("Plain shapes (floor plans, sketches)", "plain")
        self.mode_combo.setToolTip(
            "Plain shapes drops the software-architecture framing (no tech "
            "tags / C4 labels) — better for floor plans, sketches and "
            "technical drawings.")
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        opt_row.addWidget(self.mode_combo)
        self.snap_cb = QCheckBox("Snap angles to 15°")
        self.snap_cb.setToolTip(
            "Round every extracted rotation to the nearest 15° after "
            "extraction — more reliable than asking the model to be exact.")
        opt_row.addWidget(self.snap_cb)
        self.reset_prompt_btn = QPushButton("Reset to recommended")
        self.reset_prompt_btn.setToolTip(
            "Load the recommended floor-plan prompt into the instructions box "
            "(switches to Plain mode).")
        self.reset_prompt_btn.clicked.connect(self._reset_recommended_prompt)
        opt_row.addWidget(self.reset_prompt_btn)
        opt_row.addStretch()
        root.addLayout(opt_row)

        # Run row
        run_row = QHBoxLayout()
        self.run_btn = QPushButton("Run Extraction")
        self.run_btn.clicked.connect(self._run)
        run_row.addWidget(self.run_btn)
        self.status = QLabel("")
        self.status.setWordWrap(True)
        self.status.setStyleSheet("font-size:11px;")
        run_row.addWidget(self.status, 1)
        root.addLayout(run_row)

        # Result
        root.addWidget(QLabel("Extracted schema:"))
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 10))
        root.addWidget(self.output, 1)

        # Result actions
        act_row = QHBoxLayout()
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.clicked.connect(self._copy)
        act_row.addWidget(self.copy_btn)
        self.save_btn = QPushButton("Save JSON…")
        self.save_btn.clicked.connect(self._save)
        act_row.addWidget(self.save_btn)
        self.accuracy_btn = QPushButton("Measure accuracy…")
        self.accuracy_btn.setToolTip(
            "Compare the extracted shapes against the source image: per-category "
            "scores (rect/line/text/colour) plus a diagnostic overlay.")
        self.accuracy_btn.clicked.connect(self._measure_accuracy)
        act_row.addWidget(self.accuracy_btn)
        self.refine_btn = QPushButton("Refine placement…")
        self.refine_btn.setToolTip(
            "Re-align each shape by sending a tight crop around it back to the "
            "model (one focused pass per shape). Costs one API call per shape.")
        self.refine_btn.clicked.connect(self._refine_placement)
        act_row.addWidget(self.refine_btn)
        act_row.addStretch()
        self.send_btn = QPushButton("Send to Canvas")
        self.send_btn.clicked.connect(self._send)
        self.send_btn.setVisible(self._on_send is not None)
        act_row.addWidget(self.send_btn)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)
        act_row.addWidget(self.close_btn)
        root.addLayout(act_row)

        self._set_result_actions_enabled(False)

    # ── provider / env / model state ──────────────────────────────────────

    def _current_pid(self) -> str:
        return self.provider_combo.currentData()

    def _load_provider_into_ui(self, pid: str) -> None:
        idx = self.provider_combo.findData(pid)
        if idx >= 0:
            self.provider_combo.blockSignals(True)
            self.provider_combo.setCurrentIndex(idx)
            self.provider_combo.blockSignals(False)
        cfg = self._provider_cfg(pid)
        self.env_edit.setText(cfg.env_key or get_spec(pid).default_env_key)
        self.model_combo.clear()
        models = cfg.models or list(get_spec(pid).starter_models)
        self.model_combo.addItems(models)
        if cfg.default_model:
            i = self.model_combo.findText(cfg.default_model)
            if i >= 0:
                self.model_combo.setCurrentIndex(i)
        self._refresh_env_status()

    def _on_provider_changed(self) -> None:
        pid = self._current_pid()
        self._ai().active = pid
        self._load_provider_into_ui(pid)

    def _on_env_edited(self) -> None:
        name = self.env_edit.text().strip()
        if name:
            self._provider_cfg(self._current_pid()).env_key = name
        self._refresh_env_status()

    def _refresh_env_status(self) -> None:
        name = self.env_edit.text().strip()
        if name and os.environ.get(name, "").strip():
            self.env_status.setText("<span style='color:#16a34a'>● key set</span>")
        else:
            self.env_status.setText("<span style='color:#dc2626'>● not set</span>")

    def _open_docs(self) -> None:
        QDesktopServices.openUrl(QUrl(get_spec(self._current_pid()).models_doc_url))

    def _open_history(self) -> None:
        """Show past prompts; let the user recall one to refine and rerun."""
        if self._prompt_log is None:
            QMessageBox.information(self, "History", "No prompt log available.")
            return
        entries = self._prompt_log.load()
        if not entries:
            QMessageBox.information(
                self, "History",
                "No prompts logged yet. Run an extraction with some extra "
                "instructions and it will appear here.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Prompt history")
        dlg.resize(820, 460)
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel(
            "Past runs (newest first). Load one back into the form to refine "
            "and rerun — try the same prompt on a different model, or tweak it."))

        cols = ["Time", "Provider", "Model", "Result", "Instructions"]
        table = QTableWidget(len(entries), len(cols), dlg)
        table.setHorizontalHeaderLabels(cols)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        for i, e in enumerate(entries):
            if e.get("status") == "ok":
                result = f"ok · {e.get('annotations', 0)} items"
            else:
                result = f"failed · {e.get('error', '')[:40]}"
            ctx = (e.get("context", "") or "").replace("\n", " ")
            vals = [
                e.get("ts", ""), e.get("provider", ""), e.get("model", ""),
                result, ctx,
            ]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(str(v))
                if j == 4:
                    item.setToolTip(e.get("context", ""))
                table.setItem(i, j, item)
        table.resizeColumnsToContents()
        table.setColumnWidth(4, 320)
        table.horizontalHeader().setStretchLastSection(True)
        lay.addWidget(table, 1)

        def selected_rows():
            return sorted({ix.row() for ix in table.selectedIndexes()})

        def load_into_form(context_only: bool):
            rows = selected_rows()
            if not rows:
                return
            e = entries[rows[0]]
            self.context_edit.setPlainText(e.get("context", ""))
            if not context_only:
                pid = e.get("provider", "")
                idx = self.provider_combo.findData(pid)
                if idx >= 0:
                    self.provider_combo.setCurrentIndex(idx)  # reloads models/env
                if e.get("model"):
                    self.model_combo.setCurrentText(e["model"])
                if e.get("image") and os.path.isfile(e["image"]):
                    self.image_edit.setText(e["image"])
            self._refresh_env_status()
            dlg.accept()

        def delete_selected():
            rows = selected_rows()
            if not rows:
                return
            ids = [entries[r].get("id", "") for r in rows]
            self._prompt_log.delete(ids)
            for r in reversed(rows):
                table.removeRow(r)
                del entries[r]

        def view_full_prompt():
            rows = selected_rows()
            if not rows:
                return
            self._show_full_prompt(entries[rows[0]])

        table.doubleClicked.connect(lambda: load_into_form(False))

        btn_row = QHBoxLayout()
        load_btn = QPushButton("Load into form")
        load_btn.clicked.connect(lambda: load_into_form(False))
        btn_row.addWidget(load_btn)
        ctx_btn = QPushButton("Load instructions only")
        ctx_btn.clicked.connect(lambda: load_into_form(True))
        btn_row.addWidget(ctx_btn)
        view_btn = QPushButton("View full prompt…")
        view_btn.clicked.connect(view_full_prompt)
        btn_row.addWidget(view_btn)
        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(delete_selected)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.reject)
        btn_row.addWidget(close_btn)
        lay.addLayout(btn_row)
        dlg.exec()

    def _show_full_prompt(self, entry: dict) -> None:
        """Show the complete assembled prompt stored for a run."""
        text = entry.get("full_prompt", "")
        if not text:
            QMessageBox.information(
                self, "Full prompt",
                "This entry has no stored prompt (it predates prompt "
                "capture, or the run failed before the prompt was built).")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle(
            f"Full prompt — {entry.get('model', '')} @ {entry.get('ts', '')}")
        dlg.resize(760, 620)
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel(
            "The complete prompt sent to the model (base prompt + your "
            "instructions):"))
        view = QPlainTextEdit()
        view.setReadOnly(True)
        view.setFont(QFont("Consolas", 10))
        view.setPlainText(text)
        lay.addWidget(view, 1)
        row = QHBoxLayout()
        copy_btn = QPushButton("Copy")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(text))
        row.addWidget(copy_btn)
        row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.reject)
        row.addWidget(close_btn)
        lay.addLayout(row)
        dlg.exec()

    def _open_setup_wizard(self) -> None:
        from provider_setup_wizard import ProviderSetupWizard

        pid = self._current_pid()
        wiz = ProviderSetupWizard(self.settings_manager, pid, parent=self)
        wiz.exec()
        # Reflect anything the wizard changed (env name, discovered models).
        self._load_provider_into_ui(pid)

    # ── actions ───────────────────────────────────────────────────────────

    def _browse_image(self) -> None:
        start = os.path.dirname(self.image_edit.text().strip()) or ""
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose an image", start, _IMAGE_FILTER)
        if path:
            self.image_edit.setText(path)

    def _fetch_models(self) -> None:
        pid = self._current_pid()
        name = self.env_edit.text().strip()
        key = resolve_api_key(name)
        if not key:
            QMessageBox.warning(
                self, "No API key",
                f"The environment variable '{name or '(unnamed)'}' is not set.\n\n"
                "Set it to your API key and restart the app, then try again.")
            return
        self.status.setText("Fetching models…")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            rows = get_provider(pid).list_models(key)
        except ProviderError as exc:
            QApplication.restoreOverrideCursor()
            self.status.setText("<span style='color:#dc2626'>Fetch failed</span>")
            QMessageBox.critical(self, "Fetch models", str(exc))
            return
        finally:
            if QApplication.overrideCursor() is not None:
                QApplication.restoreOverrideCursor()

        if not rows:
            self.status.setText("Provider returned no models.")
            return
        current = self.model_combo.currentText().strip()
        names = [r.name for r in rows]
        self.model_combo.clear()
        self.model_combo.addItems(names)
        # Persist discovered models so they survive restarts.
        self._provider_cfg(pid).models = names
        if current and current in names:
            self.model_combo.setCurrentText(current)
        self.status.setText(f"{len(names)} models available.")

    def _run(self) -> None:
        if self._thread is not None:
            return
        image = self.image_edit.text().strip()
        if not image or not os.path.isfile(image):
            QMessageBox.information(self, "No image", "Choose a valid image file first.")
            return
        model = self.model_combo.currentText().strip()
        if not model:
            QMessageBox.information(self, "No model", "Enter or pick a model id.")
            return
        env_key = self.env_edit.text().strip()
        if not resolve_api_key(env_key):
            QMessageBox.warning(
                self, "No API key",
                f"The environment variable '{env_key or '(unnamed)'}' is not set.")
            return

        pid = self._current_pid()
        # Persist the chosen model as this provider's default.
        cfg = self._provider_cfg(pid)
        cfg.default_model = model
        if model not in cfg.models:
            cfg.models.append(model)

        context = self.context_edit.toPlainText().strip()
        mode = self.mode_combo.currentData() or "c4"
        snap = 15.0 if self.snap_cb.isChecked() else 0.0
        self._run_meta = {
            "provider": pid, "model": model, "image": image,
            "context": context, "mode": mode, "snap": snap,
        }

        self._set_running(True)
        self.output.setPlainText("")
        self.status.setText(f"Sending to {get_spec(pid).label}: {model} …")

        self._last_tokens = 0
        self._last_prompt = ""
        self._last_raw = ""
        self._thread = QThread(self)
        self._worker = ExtractWorker(
            image, model, provider_id=pid, env_key=env_key,
            extra_context=context, extraction_mode=mode,
            snap_angles_to=snap)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.raw_text.connect(self._on_raw)
        self._worker.tokens_used.connect(self._on_tokens)
        self._worker.prompt_built.connect(self._on_prompt_built)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._on_thread_done)
        self._thread.start()

    def _on_raw(self, text: str) -> None:
        self.status.setText("Model responded — parsing…")
        self._last_raw = text or ""
        if text:
            self.output.setPlainText(text)

    def _on_tokens(self, count: int) -> None:
        self._last_tokens = int(count or 0)

    def _on_prompt_built(self, prompt: str) -> None:
        self._last_prompt = prompt or ""

    def _on_finished(self, data: dict) -> None:
        self._last_result = data
        pretty = json.dumps(data, indent=2)
        self.output.setPlainText(pretty)
        warnings = data.get("_extraction_warnings") if isinstance(data, dict) else None
        n = len(data.get("annotations", [])) if isinstance(data, dict) else 0
        msg = f"Done — {n} annotations."
        if warnings:
            msg += f" {len(warnings)} warning(s) — see _extraction_warnings."
        self.status.setText(msg)
        self._set_result_actions_enabled(True)
        self._log_run(status="ok", annotations=n,
                      tokens=self._last_tokens, error="")

    def _on_failed(self, err: str) -> None:
        self._last_result = None
        self._set_result_actions_enabled(False)
        first_line = (err or "").strip().splitlines()[0] if err else "Failed"
        self._log_run(status="failed", annotations=0, tokens=self._last_tokens,
                      error=first_line)

        if self._is_parse_error(err):
            self._handle_parse_failure(err, first_line)
            return

        # Provider/transport error: keep raw error visible, classify, guide.
        self.output.setPlainText(err)
        spec = get_spec(self._current_pid())
        help_ = classify_provider_error(spec, err)
        self.status.setText(
            f"<span style='color:#dc2626'>{help_.title}</span>")
        self._show_error_help(help_)

    @staticmethod
    def _is_parse_error(err: str) -> bool:
        t = (err or "").lower()
        return any(k in t for k in (
            "parseable json", "empty response (no text)",
            "cut off at the output token"))

    def _handle_parse_failure(self, err: str, first_line: str) -> None:
        """Show the model's raw reply + a targeted hint when JSON parsing fails."""
        raw = self._last_raw.strip()
        body = ["=== MODEL RAW RESPONSE (what the model actually returned) ==="]
        body.append(raw if raw else "(the model returned no text)")
        body.append("\n=== PROBLEM ===")
        body.append(first_line)
        self.output.setPlainText("\n".join(body))
        self.copy_btn.setEnabled(True)  # let the user copy the raw reply out
        self.status.setText(
            "<span style='color:#dc2626'>Model replied, but not with usable "
            "JSON</span>")

        truncated = "cut off at the output token" in err.lower()
        empty = "empty response" in err.lower()
        if truncated:
            detail = ("The reply was cut off at the model's output token "
                      "limit, so the JSON is incomplete. Try a cropped or "
                      "simpler image, ask for fewer elements, or switch to a "
                      "model with a larger output budget.")
        elif empty:
            detail = ("The model returned no text at all — it may have refused "
                      "the request or filtered the image. Try a different "
                      "model, or rephrase your extra instructions.")
        else:
            detail = ("The model replied with prose, markdown, or a refusal "
                      "instead of JSON. The raw reply is shown in the box. "
                      "Adding a firm 'JSON only' instruction often fixes it.")

        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Couldn't parse the model's reply")
        box.setText("Model replied, but not with usable JSON")
        box.setInformativeText(detail)
        json_btn = None
        if not empty:
            json_btn = box.addButton("Add 'JSON only' instruction",
                                     QMessageBox.ButtonRole.ActionRole)
        box.addButton(QMessageBox.StandardButton.Close)
        box.exec()
        if json_btn is not None and box.clickedButton() is json_btn:
            self._append_json_only_instruction()

    def _append_json_only_instruction(self) -> None:
        hint = ("Return ONLY raw JSON matching the schema. Do not include any "
                "prose, explanation, comments, or markdown code fences.")
        existing = self.context_edit.toPlainText().strip()
        if hint.lower() in existing.lower():
            self.status.setText("'JSON only' instruction already present.")
            return
        self.context_edit.setPlainText(
            (existing + "\n" + hint).strip() if existing else hint)
        self.status.setText(
            "Added a 'JSON only' instruction — click Run Extraction to retry.")

    def _log_run(self, *, status: str, annotations: int, tokens: int,
                 error: str) -> None:
        """Append the just-finished run to the prompt log."""
        if self._prompt_log is None or not self._run_meta:
            return
        try:
            self._prompt_log.add(
                provider=self._run_meta.get("provider", ""),
                model=self._run_meta.get("model", ""),
                image=self._run_meta.get("image", ""),
                context=self._run_meta.get("context", ""),
                full_prompt=self._last_prompt,
                status=status, annotations=annotations, tokens=tokens,
                error=error)
        except Exception:
            pass  # logging must never break a run

    def _show_error_help(self, help_) -> None:
        """Show an actionable dialog for a classified provider error."""
        spec = get_spec(self._current_pid())
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Extraction failed")
        box.setText(help_.title)
        detail = help_.detail
        recommended = list(spec.starter_models or [])
        if help_.kind in ("modality", "not_found") and recommended:
            detail += ("\n\nRecommended image-capable models for "
                       f"{spec.label}:\n  • " + "\n  • ".join(recommended))
        box.setInformativeText(detail)

        open_btn = setup_btn = fetch_btn = rec_btn = None
        if help_.action_url:
            open_btn = box.addButton(
                help_.action_label or "Open page",
                QMessageBox.ButtonRole.ActionRole)
        if help_.kind in ("auth", "billing"):
            setup_btn = box.addButton(
                "Set up / Connect…", QMessageBox.ButtonRole.ActionRole)
        if help_.kind in ("modality", "not_found"):
            fetch_btn = box.addButton(
                "Fetch models…", QMessageBox.ButtonRole.ActionRole)
            if recommended:
                rec_btn = box.addButton(
                    f"Use {recommended[0]}", QMessageBox.ButtonRole.ActionRole)
        box.addButton(QMessageBox.StandardButton.Close)
        box.exec()

        clicked = box.clickedButton()
        if open_btn is not None and clicked is open_btn:
            QDesktopServices.openUrl(QUrl(help_.action_url))
        elif setup_btn is not None and clicked is setup_btn:
            self._open_setup_wizard()
        elif fetch_btn is not None and clicked is fetch_btn:
            self._fetch_models()
        elif rec_btn is not None and clicked is rec_btn:
            self.model_combo.setCurrentText(recommended[0])
            self.status.setText(
                f"Model set to {recommended[0]} — click Run Extraction.")

    def _on_thread_done(self) -> None:
        if self._thread is not None:
            self._thread.deleteLater()
        self._thread = None
        self._worker = None
        self._set_running(False)

    def _set_running(self, running: bool) -> None:
        self.run_btn.setEnabled(not running)
        self.run_btn.setText("Running…" if running else "Run Extraction")
        self.fetch_btn.setEnabled(not running)
        self.provider_combo.setEnabled(not running)

    def _set_result_actions_enabled(self, enabled: bool) -> None:
        self.copy_btn.setEnabled(enabled)
        self.save_btn.setEnabled(enabled)
        self.accuracy_btn.setEnabled(enabled)
        self.refine_btn.setEnabled(enabled and self._refine_thread is None)
        self.send_btn.setEnabled(enabled and self._on_send is not None)

    def _measure_accuracy(self) -> None:
        """Score the current extraction against the source image."""
        if not self._last_result:
            return
        image = self.image_edit.text().strip()
        if not image or not os.path.isfile(image):
            QMessageBox.warning(self, "No image",
                                "Set a valid image path to measure accuracy "
                                "against.")
            return
        overlay = os.path.join(tempfile.gettempdir(),
                               "pictosync_accuracy_overlay.png")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            from accuracy import measure_accuracy
            report = measure_accuracy(self._last_result, image,
                                      overlay_path=overlay)
        except Exception as exc:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Accuracy measurement failed",
                                 f"{type(exc).__name__}: {exc}")
            return
        QApplication.restoreOverrideCursor()

        box = QMessageBox(self)
        box.setWindowTitle("Extraction accuracy")
        box.setIcon(QMessageBox.Icon.Information)
        box.setText(f"Composite accuracy: {report.composite * 100:.1f}%")
        box.setInformativeText(report.summary())
        box.setDetailedText(json.dumps(report.to_dict(), indent=2))
        open_btn = None
        if os.path.isfile(overlay):
            open_btn = box.addButton("Open overlay…",
                                     QMessageBox.ButtonRole.ActionRole)
        box.addButton(QMessageBox.StandardButton.Close)
        box.exec()
        if open_btn is not None and box.clickedButton() is open_btn:
            QDesktopServices.openUrl(QUrl.fromLocalFile(overlay))
        self.status.setText(
            f"Accuracy: {report.composite * 100:.1f}% "
            f"(rect {self._fmt_acc(report, 'rect')}, "
            f"line {self._fmt_acc(report, 'line')}, "
            f"text {self._fmt_acc(report, 'text')}, "
            f"color {self._fmt_acc(report, 'color')})")

    @staticmethod
    def _fmt_acc(report, key: str) -> str:
        c = report.components.get(key)
        if c is None or not c.available or c.n == 0:
            return "n/a"
        return f"{c.accuracy * 100:.0f}%"

    def _reset_recommended_prompt(self) -> None:
        """Force-load the recommended floor-plan prompt (switching to Plain),
        confirming first if the box holds text the user typed."""
        cur = self.context_edit.toPlainText()
        if cur.strip() and cur != self._autofilled_context:
            ok = QMessageBox.question(
                self, "Reset instructions",
                "Replace the current instructions with the recommended "
                "floor-plan prompt?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if ok != QMessageBox.StandardButton.Yes:
                return
        idx = self.mode_combo.findData("plain")
        if idx >= 0 and self.mode_combo.currentIndex() != idx:
            self.mode_combo.blockSignals(True)
            self.mode_combo.setCurrentIndex(idx)
            self.mode_combo.blockSignals(False)
        self.context_edit.setPlainText(_PLAIN_DEFAULT_CONTEXT)
        self._autofilled_context = _PLAIN_DEFAULT_CONTEXT
        self.status.setText("Loaded the recommended floor-plan prompt.")

    def _on_mode_changed(self, _index: int) -> None:
        """Prefill the recommended Plain-mode instructions (without clobbering
        anything the user typed)."""
        current = self.context_edit.toPlainText()
        # Only touch the box when it's empty or still holds our own autofill.
        if current.strip() and current != self._autofilled_context:
            return
        if (self.mode_combo.currentData() or "c4") == "plain":
            self.context_edit.setPlainText(_PLAIN_DEFAULT_CONTEXT)
            self._autofilled_context = _PLAIN_DEFAULT_CONTEXT
        else:
            # Leaving Plain: clear the default we inserted.
            self.context_edit.setPlainText("")
            self._autofilled_context = ""

    # ── focused placement refinement ──────────────────────────────────────
    def _refine_placement(self) -> None:
        """Re-align every refinable shape via a per-shape focused ROI pass."""
        if self._refine_thread is not None:
            return
        if not self._last_result:
            return
        anns = self._last_result.get("annotations") \
            if isinstance(self._last_result, dict) else None
        if not isinstance(anns, list):
            QMessageBox.information(self, "Nothing to refine",
                                   "The result has no annotations.")
            return
        image = self.image_edit.text().strip()
        if not image or not os.path.isfile(image):
            QMessageBox.warning(self, "No image",
                                "A valid source image is required to refine.")
            return
        model = self.model_combo.currentText().strip()
        env_key = self.env_edit.text().strip()
        pid = self._current_pid()
        if not model or not resolve_api_key(env_key):
            QMessageBox.warning(
                self, "Not ready",
                "Pick a model and make sure the API key env var is set.")
            return

        indices = [i for i, a in enumerate(anns)
                   if isinstance(a, dict)
                   and a.get("kind") in _REFINABLE_KINDS
                   and isinstance(a.get("geom"), dict)]
        if not indices:
            QMessageBox.information(self, "Nothing to refine",
                                   "No shapes with geometry to refine.")
            return

        ok = QMessageBox.question(
            self, "Refine placement",
            f"Refine {len(indices)} shape(s) by sending a focused crop of each "
            f"back to {get_spec(pid).label} ({model})?\n\n"
            f"This makes {len(indices)} API call(s) and updates each shape's "
            f"geometry in place.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if ok != QMessageBox.StandardButton.Yes:
            return

        self._set_running(True)
        self.refine_btn.setEnabled(False)
        self.status.setText(f"Refining 0/{len(indices)} shapes…")

        self._refine_thread = QThread(self)
        self._refine_worker = _RefineBatchWorker(
            image, model, pid, env_key, anns, indices, max_iterations=1)
        self._refine_worker.moveToThread(self._refine_thread)
        self._refine_thread.started.connect(self._refine_worker.run)
        self._refine_worker.progress.connect(self._on_refine_progress)
        self._refine_worker.shape_done.connect(self._on_refine_shape)
        self._refine_worker.finished.connect(self._on_refine_finished)
        self._refine_worker.finished.connect(self._refine_thread.quit)
        self._refine_thread.finished.connect(self._on_refine_thread_done)
        self._refine_thread.start()

    def _on_refine_progress(self, done: int, total: int, msg: str) -> None:
        self.status.setText(f"{msg} ({done}/{total})")

    def _on_refine_shape(self, index: int, refined: dict) -> None:
        """Merge one shape's refined geometry back into the result."""
        if not isinstance(self._last_result, dict):
            return
        anns = self._last_result.get("annotations")
        if not isinstance(anns, list) or not (0 <= index < len(anns)):
            return
        new_geom = refined.get("geom")
        if isinstance(new_geom, dict) and new_geom:
            anns[index]["geom"] = new_geom

    def _on_refine_finished(self, refined: int, failed: int) -> None:
        # Re-render the (now updated) result and let the user re-measure.
        if isinstance(self._last_result, dict):
            self.output.setPlainText(json.dumps(self._last_result, indent=2))
        note = f"Refined {refined} shape(s)"
        if failed:
            note += f", {failed} failed"
        note += ". Re-run “Measure accuracy…” to compare."
        self.status.setText(note)

    def _on_refine_thread_done(self) -> None:
        if self._refine_thread is not None:
            self._refine_thread.deleteLater()
        self._refine_thread = None
        self._refine_worker = None
        self._set_running(False)
        self._set_result_actions_enabled(self._last_result is not None)

    def _copy(self) -> None:
        QApplication.clipboard().setText(self.output.toPlainText())
        self.status.setText("Copied schema to clipboard.")

    def _save(self) -> None:
        if not self._last_result:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save schema JSON", "extracted_schema.json",
            "JSON (*.json);;All files (*)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self._last_result, fh, indent=2)
        self.status.setText(f"Saved to {path}")

    def _send(self) -> None:
        if self._last_result and self._on_send is not None:
            self._on_send(self._last_result)
            self.status.setText("Sent to canvas draft.")

    def closeEvent(self, event) -> None:
        # Stop an in-flight batch refine cleanly (it can be long-running).
        if self._refine_thread is not None:
            if self._refine_worker is not None:
                self._refine_worker.cancel()
            self._refine_thread.quit()
            self._refine_thread.wait(10000)
        # Persist any env-key / model changes made in this dialog.
        try:
            self.settings_manager.save()
        except Exception:
            pass
        super().closeEvent(event)
