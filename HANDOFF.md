# PictoSync — Session Handoff

## Goal (this phase)

Make the AI diagram-extraction pipeline **provider-agnostic** so the user can
drop in whatever vision model is currently "best of the best" (across Gemini,
OpenAI/GPT, and Anthropic/Claude) without hand-coding a new integration each
time, and give them a self-contained harness to run a chosen model on an image
and inspect the returned schema. Chosen slice: **Step 1 (provider seam) + thin
Step 3 (Try-a-Model dialog)**. Key handling: keep env-vars, but make the env
**variable name** editable per provider so a key can be dedicated to
PictoSync + that provider (e.g. `PICTOSYNC_OPENAI_KEY`).

## What shipped

- **`providers/` package (new seam)** — one thin adapter per vendor. Each does
  only the raw vision call (`extract`) and model discovery (`list_models`);
  prompt-building + schema validation stay provider-neutral in the worker.
  - `providers/base.py` — `BaseVisionProvider`, `ProviderSpec`, `ModelInfo`,
    `VisionResponse`, `ProviderError`, `resolve_api_key(env_name)`,
    `image_to_base64`.
  - `providers/gemini_provider.py` — wraps `google-genai`; REST discovery.
  - `providers/openai_provider.py` — `openai` chat-completions + image part.
  - `providers/anthropic_provider.py` — `anthropic` Messages + image block.
  - `providers/__init__.py` — registry: `get_provider`, `get_spec`,
    `provider_ids`, `all_specs`.
- **`gemini/worker.py`** — `ExtractWorker.__init__` now takes
  `(png_path, model, provider_id="gemini", env_key=None)`; `run()` resolves the
  key by the configured env-var name and delegates the API call to the seam.
  Backward-compatible: `main.auto_extract()` still constructs it with two args
  and keeps hitting Gemini. (`FocusedAlignWorker` is now also seam-aware — see
  the focused-refinement entry below.)
- **`settings.py`** — new `AIProviderConfig` (stores `env_key` *name*, `models`,
  `default_model`) and `AIProvidersSettings` (`active`, `providers` map), wired
  into `AppSettings.ai_providers`, `_apply_toml`, and `_to_toml_dict` under an
  `ai_providers` TOML section. Unknown provider ids round-trip safely.
- **`try_model_dialog.py` (new, thin Step 3)** — `TryModelDialog`: provider
  picker, editable API-key env-var name with live set/not-set indicator,
  model combo with "Fetch models…", image browser, Run (via `ExtractWorker` on
  a `QThread`), schema viewer with Copy / Save / "Send to Canvas". Persists
  env-name/model choices to settings on close.
- **`main.py`** — `_build_model_menu` now appends "Try a model on an image…"
  and "Set up a provider (keys & libraries)…"; new `open_try_model_dialog()`
  and `open_provider_setup_wizard()`. "Send to Canvas" wires to the existing
  draft-dock import path.
- **`provider_setup_wizard.py` (new, Step 2 helper)** — `ProviderSetupWizard`,
  a 3-page QWizard: (1) **Library** — detect SDK via `providers.sdk_installed`,
  install with `pip install <pkg>` streamed through `QProcess` into
  `sys.executable`; (2) **API key** — editable env-var *name* + password key
  field, "Save key" sets `os.environ` now and persists durably via
  `key_store.py` (3) **Verify** — live `list_models` call. Reachable from the
  model dropdown and from a "Set up / Connect…" button in the Try dialog.
  `providers/base.py` gained `pip_package`, `import_module`, `api_keys_url` on
  `ProviderSpec` plus `sdk_installed(spec)`.
- **`vault.py` (new) — single-key encrypted vault for all API keys.** One
  master secret, the `PICTOSYNC_VAULT_KEY` env var, unlocks one encrypted file
  `<user_settings_dir>/vault.dat` holding every key as `{env_name: value}`.
  Every read/save/delete decrypts → edits → re-encrypts with it. Stdlib-only
  crypto (no dependency): **scrypt** KDF → 32B enc + 32B MAC keys; HMAC-SHA256
  CTR keystream for confidentiality; encrypt-then-MAC (HMAC-SHA256) for
  integrity — a wrong key fails the MAC (`VaultKeyError`) vs `VaultLocked` when
  the key is absent. The master key is optionally "remembered" on the machine
  via DPAPI in `vault_key.dat` and reloaded at startup. `main()` calls
  `load_vault_key_into_env()` then `load_keys_into_env()` (after
  `get_settings()`, before `MainWindow`); a real env var of the same name wins.
  Verified: plaintext never hits disk, keys restore in a fresh process, wrong
  key rejected, delete works, DPAPI remember round-trips.
- **`vault_wizard.py` (new) — `VaultSetupDialog` + `ensure_unlocked()`.**
  State-aware: **create** (choose key twice, optional "remember on this
  machine", offer to import legacy keys via `key_store.export_all`), **unlock**
  (verify existing key, "Reset vault…" if forgotten), **unlocked** (change key
  / toggle remember). Reachable from the model dropdown ("Set up key vault…",
  `MainWindow.open_vault_wizard`). The provider wizard's "Save key" now writes
  to the vault and calls `ensure_unlocked()` first.
- **`key_store.py`** — now legacy-only: `export_all()` / `legacy_file_exists()`
  let the vault import keys saved by the old per-key DPAPI store. No longer
  loaded at startup.
- **Actionable error help** — `providers/base.py` gained `ErrorHelp` +
  `classify_provider_error(spec, text)`, which reads an error string and
  returns a kind (`modality` / `billing` / `auth` / `rate_limit` /
  `not_found` / `network` / `unknown`) with a one-click URL. `modality` =
  the chosen model can't accept images (e.g. Gemini "Image input modality is
  not enabled"); the dialog then lists the provider's recommended image-capable
  models and offers "Fetch models…" + "Use <recommended>" buttons that set the
  model combo inline. `ProviderSpec.billing_url` added for all
  three vendors. The Try dialog's `_on_failed` now shows a dialog with "Open
  billing page" / "Open API keys page" / "Set up / Connect…" buttons instead
  of a raw stack trace (raw text still in the output box). A `429 no credits`
  is correctly surfaced as billing (valid key, empty balance), not a dead key.

## Decisions + rationale

- **Seam = raw call only.** Keeping prompt + `validate_and_fix_annotations` in
  the worker means adding a vendor never touches extraction logic. Adapters
  import their SDK lazily so missing SDKs don't break app startup.
- **Key by env-var NAME, not stored key.** Satisfies the user's request and
  avoids storing secrets on disk. Each provider has a vendor-default name,
  overridable in the dialog.
- **Parallel `ai_providers` config** rather than rewriting the existing
  `gemini` settings tab — keeps this phase bounded and the current Gemini
  toolbar/settings UI untouched and working.

- **Prompt context + history** — `ExtractWorker` gained `extra_context`, a
  free-text block appended to the prompt under "ADDITIONAL INSTRUCTIONS FROM
  THE USER" (takes priority over the general guidance). The Try dialog has an
  "Extra instructions" box and a "History…" button. New `prompt_log.py`
  (`PromptLog`) persists every run to `extraction_prompts.json` in the user
  settings dir (newest first, max 500; each entry has a unique `id`, ts,
  provider, model, image, context, status, annotations, tokens, error). The
  History dialog lists past runs and loads one back into the form ("Load into
  form" sets provider/model/image/context; "Load instructions only" keeps the
  text) so the same prompt can be retried on a different model or refined.
  Note: entry identity is the uuid `id`, not `ts` (two runs can share a
  second). `ExtractWorker` emits a `prompt_built(str)` signal with the **full
  assembled prompt** (base + user instructions) just before the API call —
  captured even on failure — and the log stores it as `full_prompt`; History
  has a "View full prompt…" viewer with Copy.

- **Parse-failure diagnostics.** `VisionResponse` gained `stop_reason` +
  `truncated`; all three adapters set them (Anthropic `max_tokens`, OpenAI
  `length`, Gemini `MAX_TOKENS`). Anthropic output budget raised 8192→16384.
  The worker now distinguishes empty / truncated / non-JSON replies with
  specific messages. The Try dialog's `_on_failed` detects parse errors and —
  instead of burying the payload under a traceback — shows the **raw model
  response** plus the problem, enables Copy, and offers an "Add 'JSON only'
  instruction" button that appends a firm JSON-only directive to the context
  for a one-click retry. (`extract_first_json_object` already strips markdown
  fences, so the usual cause is truncation or prose/refusal, not fencing.)

- **Geometry/rotation mapping shim** (`schema_shim.py`). Models express
  geometry inconsistently (notably `rot` vs the schema's `angle`; also
  `left/top/right/bottom`, `width/height`, centre-based `cx/cy`, radians,
  start/end line dicts, geometry at the top level). `coerce_annotations(data)`
  maps all of these onto PictoSync canonical geom — box: `{x,y,w,h[,angle]}`
  (x,y = top-left of the UNROTATED box, `angle` = degrees CLOCKWISE about the
  CENTRE, matching `mixins.setTransformOriginPoint(center)`+`setRotation`);
  line: `{x1,y1,x2,y2}` — strips consumed aliases, preserves `adjust1/2/3`.
  Applied in `worker.run()` BEFORE `validate_and_fix_annotations` (so shapes
  that used `left/right` instead of `w` are no longer dropped for `w<=0`);
  notes merged into `_extraction_warnings`. The extraction prompt gained a
  ROTATION section telling models to use the key `angle` (not rot/rotation/
  theta), degrees clockwise, with w/h as the shape's own upright side lengths.
  Root cause the user reported: the prompt never asked for rotation and `rot`
  was never mapped to `angle`.

- **Accuracy measure** (`accuracy.py`). Scores an extraction against its source
  image with **no ground truth** — the image is the reference. Reduces the PNG
  to a Canny edge map + distance transform; each predicted shape outline is
  rasterised (rotated boxes via `_rotated_box_corners`, matching the canvas
  rotation convention) and its mean distance-to-nearest-edge is the chamfer
  error, while `-grad(dt)` under the outline is the *signed* nudge toward real
  structure. Four decomposed, signed components for a future gradient-descent
  optimiser: **rect** / **line** (error 0-1 + `(dx,dy)` pixel nudge, per shape),
  **color** (mean sampled pixel under each rotated fill mask vs declared hex →
  signed `(dr,dg,db)`), **text** (pytesseract OCR recall + signed count delta;
  gracefully marked unavailable if the Tesseract binary is missing — it IS
  installed on this machine). One `composite` 0-1 = weighted complement of the
  measurable component errors (rect .35 / line .25 / text .20 / color .20,
  renormalised). `measure_accuracy(data, png, overlay_path=…)` returns an
  `AccuracyReport` (`.summary()`, `.to_dict()`); also a CLI
  (`python accuracy.py result.json image.png --overlay out.png`) and a
  "Measure accuracy…" button in the Try dialog that shows per-category scores
  and opens a diagnostic overlay (real edges green, predicted rects red, lines
  blue). Geometry runs through `schema_shim.coerce_annotations` first, so raw
  model output is accepted too. Verified on synthetic cases: aligned rect ≈89%
  with ~0 nudge; +15,+12 offset → rect 0% with nudge pointing back; wrong fill
  → colour direction lands on the true colour.

- **Prompt modes + angle snapping.** `ExtractWorker` gained
  `extraction_mode` ("c4" default | "plain") and `snap_angles_to` (0 = off).
  `_build_extraction_prompt(w, h, mode)` now swaps three pieces by mode: the
  intro, the per-shape text hint (`<C4 format: Label [Tech] Description>` vs
  `<any text that appears inside or on the shape>`), and the DETECTION
  GUIDELINES block (module consts `_C4_DETECTION` / `_PLAIN_DETECTION`). Plain
  mode tells the model it's a floor-plan/sketch/flowchart, not software
  architecture — no invented tech/protocols, capture ALL text incl. dimension
  strings, prefer fewer well-placed shapes, ignore furniture/hatching.
  `schema_shim.snap_angles(data, inc)` rounds every box `angle` to the nearest
  multiple (drops 0) — applied in `run()` after validation when enabled; notes
  merged into `_extraction_warnings`. The Try dialog got a **Mode** combo + a
  **"Snap angles to 15°"** checkbox (passed through to the worker), and its
  example-prompt placeholder now explicitly asks for text + dimension labels.
  The main toolbar auto-extract is untouched (defaults: c4, no snap).
  Selecting **Plain** mode auto-fills the context box with a recommended
  floor-plan prompt (`_PLAIN_DEFAULT_CONTEXT`: text-first, all rects incl.
  angled on a 15° grid, lines, exhaustive, ignore furniture). `_on_mode_changed`
  only replaces the box when it's empty or still holds that autofill (tracked in
  `self._autofilled_context`), so it never clobbers the user's own text;
  switching back to C4 clears the autofill. The default prompt forcefully
  forbids dropping freestanding text (dimension strings, callouts, title
  blocks): every readable string must appear once, as a shape's meta.label or a
  standalone "text" item. A **"Reset to recommended"** button next to the Mode
  selector (`_reset_recommended_prompt`) force-loads that prompt (switching to
  Plain), confirming first only if the box holds user-typed text.

- **Focused ROI refinement wired into the Try dialog.** `FocusedAlignWorker`
  is now **provider-agnostic**: `__init__` gained `provider_id` / `env_key`, and
  `run()` resolves the key via the seam and sends each ROI crop through
  `provider.extract` (crop saved to a temp PNG), so refinement works on any
  provider — not just Gemini. Backward-compatible (the main-canvas 3-arg call
  still defaults to gemini + its default key). `run()` also stashes
  `self.result` / `self.error` so it can be driven synchronously. New
  `_RefineBatchWorker` (in `try_model_dialog.py`) loops over a result's
  refinable shapes (`_REFINABLE_KINDS`), calling `FocusedAlignWorker.run()` per
  shape on one background thread, emitting `progress` / `shape_done` /
  `finished`. The Try dialog got a **"Refine placement…"** button: confirms the
  shape count / API-call cost, then re-aligns each shape, merging the refined
  `geom` back into `_last_result` in place and re-rendering, so the user can
  immediately re-run "Measure accuracy…" to compare. Cooperative cancel +
  `thread.wait()` on close so a long batch doesn't crash on dialog close.

## Remaining tasks (future phases — user picks order)

- **Step 2 — Connection Wizard** — DONE (`provider_setup_wizard.py`): library
  install + key set/persist + verify.
- **Step 4 — "What's recommended?"**: bundled, user-editable
  `recommended_models.json` + vendor doc links (the place to paste the latest
  Claude/ChatGPT verdict).
- **Step 5 — Benchmark compare**: run one image through two models side-by-side,
  diff the schemas.
- **Follow-ups**: make the main toolbar extract flow provider-aware (today it
  still uses `self.model_name` + Gemini default); relabel "Auto-Extract
  (Gemini)"; generalize the Gemini settings tab to all providers; add tests for
  `providers/` and the new settings section.

## Verification

```bash
# compile + import
python -m py_compile providers/*.py gemini/worker.py settings.py try_model_dialog.py main.py
python -c "import providers, try_model_dialog; print(providers.provider_ids())"
# settings round-trip
python -m pytest tests/test_settings_dialog.py -q
# manual: run app -> model dropdown -> "Try a model on an image…"
python main.py
```

Not yet done: no automated tests for the new `providers/` package or the
`ai_providers` settings section; OpenAI/Anthropic adapters are untested against
live APIs (no keys exercised this session).
