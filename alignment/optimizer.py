"""
alignment/optimizer.py

Core alignment algorithm:
1. Extract shapes from the PNG using contour detection
2. Find the shape closest to the selected item's center
3. Fine-tune with template matching

Debug output shows each iteration's x, y, w, h values.
"""

from __future__ import annotations

from typing import Dict, Tuple, Optional, Callable, List

import cv2
import numpy as np


def hex_to_bgr(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to BGR tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 8:
        hex_color = hex_color[:6]
    if len(hex_color) != 6:
        return (128, 128, 128)
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (b, g, r)


def bgr_to_hsv(bgr: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Convert BGR color to HSV using OpenCV.

    Returns HSV where:
    - H is 0-179 (OpenCV convention, multiply by 2 for standard 0-360)
    - S is 0-255
    - V is 0-255
    """
    # Create a 1x1 pixel image with the color
    pixel = np.uint8([[list(bgr)]])
    hsv_pixel = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)
    h, s, v = hsv_pixel[0, 0]
    return (int(h), int(s), int(v))


def extract_shapes_from_region(
    img: np.ndarray,
    min_area: int = 500,
    pen_color_bgr: Optional[Tuple[int, int, int]] = None
) -> List[Dict]:
    """
    Extract shapes from an image region using HSV color matching.
    Uses Hue for color matching with tolerance, which handles similar colors better.
    """
    kernel = np.ones((3, 3), np.uint8)
    shapes = []

    print(f"[ALIGN] extract_shapes_from_region: img size={img.shape}, min_area={min_area}")

    if not pen_color_bgr:
        print(f"[ALIGN] ERROR: No pen color provided!")
        return shapes

    # Convert pen color to HSV
    pen_hsv = bgr_to_hsv(pen_color_bgr)
    print(f"[ALIGN] Pen color BGR: {pen_color_bgr} -> HSV: {pen_hsv}")

    # Convert image to HSV
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Try different hue tolerances
    # OpenCV Hue is 0-179, so hue_tol of 15 = ±30 degrees in standard 0-360 scale
    all_contours = []
    contours_by_tolerance = {}

    for hue_tol in [10, 15, 20, 25, 30]:
        # Hue tolerance (circular, 0-179 in OpenCV)
        h_target = pen_hsv[0]

        # Saturation and Value tolerance (wider)
        s_tol = 80
        v_tol = 80

        # Handle hue wraparound (red is at both 0 and 179)
        h_low = h_target - hue_tol
        h_high = h_target + hue_tol

        s_low = max(0, pen_hsv[1] - s_tol)
        s_high = min(255, pen_hsv[1] + s_tol)
        v_low = max(0, pen_hsv[2] - v_tol)
        v_high = min(255, pen_hsv[2] + v_tol)

        # For low saturation colors (grays), use BGR matching instead
        if pen_hsv[1] < 30:
            print(f"[ALIGN] Low saturation ({pen_hsv[1]}), using BGR matching for hue_tol={hue_tol}")
            # Fall back to BGR matching for grays
            bgr_tol = hue_tol * 4  # Scale tolerance
            lower = np.array([max(0, int(c) - bgr_tol) for c in pen_color_bgr], dtype=np.uint8)
            upper = np.array([min(255, int(c) + bgr_tol) for c in pen_color_bgr], dtype=np.uint8)
            color_mask = cv2.inRange(img, lower, upper)
        elif h_low < 0:
            # Hue wraps around 0 (red colors)
            lower1 = np.array([0, s_low, v_low], dtype=np.uint8)
            upper1 = np.array([h_high, s_high, v_high], dtype=np.uint8)
            lower2 = np.array([180 + h_low, s_low, v_low], dtype=np.uint8)
            upper2 = np.array([179, s_high, v_high], dtype=np.uint8)
            mask1 = cv2.inRange(img_hsv, lower1, upper1)
            mask2 = cv2.inRange(img_hsv, lower2, upper2)
            color_mask = cv2.bitwise_or(mask1, mask2)
            print(f"[ALIGN] Hue {hue_tol}: wraparound H=[{180+h_low}-179] or [0-{h_high}]")
        elif h_high > 179:
            # Hue wraps around 179 (red colors)
            lower1 = np.array([h_low, s_low, v_low], dtype=np.uint8)
            upper1 = np.array([179, s_high, v_high], dtype=np.uint8)
            lower2 = np.array([0, s_low, v_low], dtype=np.uint8)
            upper2 = np.array([h_high - 180, s_high, v_high], dtype=np.uint8)
            mask1 = cv2.inRange(img_hsv, lower1, upper1)
            mask2 = cv2.inRange(img_hsv, lower2, upper2)
            color_mask = cv2.bitwise_or(mask1, mask2)
            print(f"[ALIGN] Hue {hue_tol}: wraparound H=[{h_low}-179] or [0-{h_high-180}]")
        else:
            # Normal case - no wraparound
            lower = np.array([h_low, s_low, v_low], dtype=np.uint8)
            upper = np.array([h_high, s_high, v_high], dtype=np.uint8)
            color_mask = cv2.inRange(img_hsv, lower, upper)
            print(f"[ALIGN] Hue {hue_tol}: H=[{h_low}-{h_high}], S=[{s_low}-{s_high}], V=[{v_low}-{v_high}]")

        # Save debug mask
        try:
            cv2.imwrite(f"debug_color_mask_hue{hue_tol}.png", color_mask)
        except:
            pass

        # Clean up mask - close gaps, remove noise
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel, iterations=1)

        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print(f"[ALIGN] Hue tolerance {hue_tol}: found {len(contours)} contours")

        contours_by_tolerance[hue_tol] = contours
        all_contours.extend(contours)

    if not all_contours:
        print(f"[ALIGN] No contours found matching pen color at any hue tolerance!")
        return shapes

    print(f"[ALIGN] Total contours across all tolerances: {len(all_contours)}")

    seen_centers = set()
    skipped_area = 0
    skipped_size = 0
    skipped_duplicate = 0

    for contour in all_contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            skipped_area += 1
            continue

        x, y, w, h = cv2.boundingRect(contour)
        if w < 15 or h < 15:
            skipped_size += 1
            continue

        cx = x + w / 2
        cy = y + h / 2

        center_key = (int(cx / 10), int(cy / 10))
        if center_key in seen_centers:
            skipped_duplicate += 1
            continue
        seen_centers.add(center_key)

        rect_area = w * h
        fill_ratio = area / rect_area if rect_area > 0 else 0

        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if fill_ratio > 0.75 and fill_ratio < 0.85:
            shape_type = "ellipse"
        elif len(approx) == 4:
            shape_type = "rect"
        else:
            shape_type = "rect"

        shapes.append({
            "contour": contour,
            "bbox": (x, y, w, h),
            "center": (cx, cy),
            "area": area,
            "shape_type": shape_type,
            "fill_ratio": fill_ratio
        })
        print(f"[ALIGN]   Shape: bbox=({x},{y},{w},{h}) area={area} fill={fill_ratio:.2f}")

    print(f"[ALIGN] Filtering: skipped {skipped_area} (area<{min_area}), {skipped_size} (size<15), {skipped_duplicate} (duplicate)")
    print(f"[ALIGN] Final shapes found: {len(shapes)}")

    return shapes


def find_closest_shape(
    shapes: List[Dict],
    target_cx: float,
    target_cy: float,
    target_w: float,
    target_h: float
) -> Optional[Dict]:
    """Find the shape closest to the target center with similar size."""
    if not shapes:
        return None

    best_shape = None
    best_score = float('inf')

    for shape in shapes:
        cx, cy = shape["center"]
        x, y, w, h = shape["bbox"]

        distance = np.sqrt((cx - target_cx)**2 + (cy - target_cy)**2)
        size_diff = abs(w - target_w) / target_w + abs(h - target_h) / target_h
        score = distance + size_diff * 50

        if score < best_score:
            best_score = score
            best_shape = shape

    return best_shape


def render_template(
    kind: str,
    w: int,
    h: int,
    fill_color: Tuple[int, int, int],
    border_color: Tuple[int, int, int],
    border_width: int = 2,
    radius: int = 0
) -> np.ndarray:
    """Render a shape as a BGR image template."""
    img = np.zeros((h, w, 3), dtype=np.uint8)

    if kind == "rect":
        cv2.rectangle(img, (0, 0), (w - 1, h - 1), fill_color, -1)
        if border_width > 0:
            cv2.rectangle(img, (0, 0), (w - 1, h - 1), border_color, border_width)

    elif kind == "roundedrect":
        r = min(radius, min(w, h) // 2)
        if r <= 0:
            cv2.rectangle(img, (0, 0), (w - 1, h - 1), fill_color, -1)
            if border_width > 0:
                cv2.rectangle(img, (0, 0), (w - 1, h - 1), border_color, border_width)
        else:
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.rectangle(mask, (r, 0), (w - 1 - r, h - 1), 255, -1)
            cv2.rectangle(mask, (0, r), (w - 1, h - 1 - r), 255, -1)
            cv2.ellipse(mask, (r, r), (r, r), 180, 0, 90, 255, -1)
            cv2.ellipse(mask, (w - 1 - r, r), (r, r), 270, 0, 90, 255, -1)
            cv2.ellipse(mask, (r, h - 1 - r), (r, r), 90, 0, 90, 255, -1)
            cv2.ellipse(mask, (w - 1 - r, h - 1 - r), (r, r), 0, 0, 90, 255, -1)
            img[mask > 0] = fill_color

            if border_width > 0:
                cv2.line(img, (r, 0), (w - 1 - r, 0), border_color, border_width)
                cv2.line(img, (r, h - 1), (w - 1 - r, h - 1), border_color, border_width)
                cv2.line(img, (0, r), (0, h - 1 - r), border_color, border_width)
                cv2.line(img, (w - 1, r), (w - 1, h - 1 - r), border_color, border_width)
                cv2.ellipse(img, (r, r), (r, r), 180, 0, 90, border_color, border_width)
                cv2.ellipse(img, (w - 1 - r, r), (r, r), 270, 0, 90, border_color, border_width)
                cv2.ellipse(img, (r, h - 1 - r), (r, r), 90, 0, 90, border_color, border_width)
                cv2.ellipse(img, (w - 1 - r, h - 1 - r), (r, r), 0, 0, 90, border_color, border_width)

    elif kind == "ellipse":
        center = (w // 2, h // 2)
        axes = ((w - 1) // 2, (h - 1) // 2)
        cv2.ellipse(img, center, axes, 0, 0, 360, fill_color, -1)
        if border_width > 0:
            cv2.ellipse(img, center, axes, 0, 0, 360, border_color, border_width)

    return img


def sample_colors_at_shape(
    img: np.ndarray,
    shape: Dict
) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """Sample fill and border colors from a detected shape."""
    x, y, w, h = shape["bbox"]
    contour = shape["contour"]

    img_h, img_w = img.shape[:2]

    mask = np.zeros((img_h, img_w), dtype=np.uint8)
    cv2.drawContours(mask, [contour], 0, 255, -1)

    kernel = np.ones((5, 5), np.uint8)
    interior_mask = cv2.erode(mask, kernel, iterations=3)

    interior_pixels = img[interior_mask > 0]
    if len(interior_pixels) > 0:
        fill_color = tuple(int(v) for v in np.median(interior_pixels, axis=0))
    else:
        cx = min(max(0, x + w // 2), img_w - 1)
        cy = min(max(0, y + h // 2), img_h - 1)
        fill_color = tuple(int(v) for v in img[cy, cx])

    border_mask = cv2.dilate(mask, kernel, iterations=1) - mask
    border_pixels = img[border_mask > 0]
    if len(border_pixels) > 0:
        border_color = tuple(int(v) for v in np.median(border_pixels, axis=0))
    else:
        border_color = fill_color

    return (fill_color, border_color)


def sample_exact_pen_color(
    img: np.ndarray,
    shape: Dict,
    pen_color_bgr: Tuple[int, int, int]
) -> Tuple[int, int, int]:
    """
    Sample the exact pen/border color from the PNG at the shape's border.

    Uses the contour edge pixels and finds the color closest to the expected pen color.
    Returns the median color of border pixels that match the expected hue.
    """
    contour = shape["contour"]
    img_h, img_w = img.shape[:2]

    # Create a mask of just the contour edge (not filled)
    edge_mask = np.zeros((img_h, img_w), dtype=np.uint8)
    cv2.drawContours(edge_mask, [contour], 0, 255, 2)  # Draw contour with thickness 2

    # Get pixels along the edge
    edge_pixels = img[edge_mask > 0]

    if len(edge_pixels) == 0:
        print(f"[ALIGN] No edge pixels found, returning original pen color")
        return pen_color_bgr

    # Convert to HSV to filter by hue
    pen_hsv = bgr_to_hsv(pen_color_bgr)
    target_hue = pen_hsv[0]

    # Convert edge pixels to HSV
    edge_pixels_reshaped = edge_pixels.reshape(-1, 1, 3).astype(np.uint8)
    edge_hsv = cv2.cvtColor(edge_pixels_reshaped, cv2.COLOR_BGR2HSV).reshape(-1, 3)

    # Filter pixels that are close in hue (within ±20)
    hue_diff = np.abs(edge_hsv[:, 0].astype(np.int16) - target_hue)
    # Handle hue wraparound
    hue_diff = np.minimum(hue_diff, 180 - hue_diff)

    # Also filter by saturation (exclude very unsaturated pixels which might be background)
    sat_mask = edge_hsv[:, 1] > 30

    # Combine masks
    matching_mask = (hue_diff < 25) & sat_mask

    if np.sum(matching_mask) > 0:
        matching_pixels = edge_pixels[matching_mask]
        # Use median to get the most representative color
        sampled_color = tuple(int(v) for v in np.median(matching_pixels, axis=0))
        print(f"[ALIGN] Sampled pen color from {np.sum(matching_mask)} matching edge pixels: BGR{sampled_color}")
    else:
        # Fallback: use median of all edge pixels
        sampled_color = tuple(int(v) for v in np.median(edge_pixels, axis=0))
        print(f"[ALIGN] No hue-matching pixels, using median of all edge pixels: BGR{sampled_color}")

    return sampled_color


def bgr_to_hex(bgr: Tuple[int, int, int]) -> str:
    """Convert BGR tuple to hex color string."""
    b, g, r = bgr
    return f"#{r:02X}{g:02X}{b:02X}"


def optimize_pen_width(
    region: np.ndarray,
    kind: str,
    x: int,
    y: int,
    w: int,
    h: int,
    fill_color: Tuple[int, int, int],
    border_color: Tuple[int, int, int],
    radius: int = 0,
    current_width: int = 2,
    report: Optional[Callable[[str], None]] = None
) -> int:
    """
    Optimize pen/stroke width by comparing templates with different widths.
    Position is kept fixed.
    """
    if report:
        report(f"Optimizing pen width (current={current_width})")

    best_width = current_width
    best_score = -1.0

    # Try different pen widths
    widths_to_try = [1, 2, 3, 4, 5, 6, 8, 10]

    for test_width in widths_to_try:
        # Render template with this width
        template = render_template(kind, w, h, fill_color, border_color, test_width, radius)

        # Check if template fits in region at position (x, y)
        if x < 0 or y < 0 or x + w > region.shape[1] or y + h > region.shape[0]:
            continue

        # Extract the corresponding region from PNG
        png_patch = region[y:y+h, x:x+w]

        if png_patch.shape[0] != h or png_patch.shape[1] != w:
            continue

        # Compare using normalized cross-correlation
        # Flatten and compute correlation
        template_flat = template.astype(np.float32).flatten()
        patch_flat = png_patch.astype(np.float32).flatten()

        # Normalize
        t_mean = np.mean(template_flat)
        p_mean = np.mean(patch_flat)
        t_std = np.std(template_flat)
        p_std = np.std(patch_flat)

        if t_std > 0 and p_std > 0:
            score = np.mean((template_flat - t_mean) * (patch_flat - p_mean)) / (t_std * p_std)
        else:
            score = 0.0

        if report:
            report(f"  Width {test_width}: score={score:.4f}")

        if score > best_score:
            best_score = score
            best_width = test_width

    if report:
        report(f"Best pen width: {best_width} (score={best_score:.4f})")

    return best_width


def optimize_radius(
    region: np.ndarray,
    x: int,
    y: int,
    w: int,
    h: int,
    fill_color: Tuple[int, int, int],
    border_color: Tuple[int, int, int],
    pen_width: int = 2,
    current_radius: int = 0,
    report: Optional[Callable[[str], None]] = None
) -> int:
    """
    Optimize corner radius for rounded rectangles by comparing templates.
    Position is kept fixed.
    """
    if report:
        report(f"Optimizing radius (current={current_radius})")

    best_radius = current_radius
    best_score = -1.0

    # Maximum sensible radius is half of the smaller dimension
    max_radius = min(w, h) // 2

    # Try different radii
    radii_to_try = [0, 2, 4, 6, 8, 10, 12, 15, 20, 25, 30]
    radii_to_try = [r for r in radii_to_try if r <= max_radius]

    # Also try current radius and nearby values
    for delta in [-2, -1, 0, 1, 2]:
        r = current_radius + delta
        if 0 <= r <= max_radius and r not in radii_to_try:
            radii_to_try.append(r)

    radii_to_try = sorted(set(radii_to_try))

    for test_radius in radii_to_try:
        # Render template with this radius
        template = render_template("roundedrect", w, h, fill_color, border_color, pen_width, test_radius)

        # Check if template fits in region at position (x, y)
        if x < 0 or y < 0 or x + w > region.shape[1] or y + h > region.shape[0]:
            continue

        # Extract the corresponding region from PNG
        png_patch = region[y:y+h, x:x+w]

        if png_patch.shape[0] != h or png_patch.shape[1] != w:
            continue

        # Compare using normalized cross-correlation
        template_flat = template.astype(np.float32).flatten()
        patch_flat = png_patch.astype(np.float32).flatten()

        t_mean = np.mean(template_flat)
        p_mean = np.mean(patch_flat)
        t_std = np.std(template_flat)
        p_std = np.std(patch_flat)

        if t_std > 0 and p_std > 0:
            score = np.mean((template_flat - t_mean) * (patch_flat - p_mean)) / (t_std * p_std)
        else:
            score = 0.0

        if report:
            report(f"  Radius {test_radius}: score={score:.4f}")

        if score > best_score:
            best_score = score
            best_radius = test_radius

    if report:
        report(f"Best radius: {best_radius} (score={best_score:.4f})")

    return best_radius


def refine_with_template_matching(
    search_region: np.ndarray,
    kind: str,
    initial_w: int,
    initial_h: int,
    fill_color: Tuple[int, int, int],
    border_color: Tuple[int, int, int],
    radius: int,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Tuple[int, int, int, int, float]:
    """
    Refine position and size using template matching.
    Prints debug info for each iteration.
    """
    best_score = -1.0
    best_x = 0
    best_y = 0
    best_w = initial_w
    best_h = initial_h

    iteration = 0
    size_scales = [0.9, 0.95, 1.0, 1.05, 1.1]

    for scale_w in size_scales:
        for scale_h in size_scales:
            test_w = max(20, int(initial_w * scale_w))
            test_h = max(20, int(initial_h * scale_h))

            if test_w >= search_region.shape[1] - 1 or test_h >= search_region.shape[0] - 1:
                continue

            template = render_template(
                kind, test_w, test_h,
                fill_color, border_color,
                border_width=2, radius=int(radius * scale_w)
            )

            result = cv2.matchTemplate(search_region, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            iteration += 1

            # Debug output for each iteration
            msg = (f"Template iter {iteration}: scale=({scale_w:.2f},{scale_h:.2f}) "
                   f"size={test_w}x{test_h} loc=({max_loc[0]},{max_loc[1]}) score={max_val:.4f}")
            print(f"[ALIGN] {msg}")
            if progress_callback:
                progress_callback(iteration, msg)

            if max_val > best_score:
                best_score = max_val
                best_x = max_loc[0]
                best_y = max_loc[1]
                best_w = test_w
                best_h = test_h

                msg = f"  -> NEW BEST: x={best_x}, y={best_y}, w={best_w}, h={best_h}, score={best_score:.4f}"
                print(f"[ALIGN] {msg}")
                if progress_callback:
                    progress_callback(iteration, msg)

    return best_x, best_y, best_w, best_h, best_score


def align_element(
    png_path: str,
    geom: Dict[str, float],
    kind: str,
    pen_color: str = "#000000",
    pen_width: int = 2,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Dict[str, float]:
    """
    Align an element to match the corresponding visual element in the PNG.

    Debug output shows x, y, w, h at each iteration.
    """
    x = float(geom["x"])
    y = float(geom["y"])
    w = float(geom["w"])
    h = float(geom["h"])
    radius = int(geom.get("radius", 0)) if kind == "roundedrect" else 0

    iteration = 0

    def report(msg: str):
        nonlocal iteration
        iteration += 1
        print(f"[ALIGN] {msg}")  # Debug to terminal
        if progress_callback:
            progress_callback(iteration, msg)

    report(f"=== ALIGNMENT START ===")
    report(f"Input: x={x}, y={y}, w={w}, h={h}, kind={kind}")

    # Load image
    img = cv2.imread(png_path)
    if img is None:
        report("Error: Could not load image")
        return geom

    img_h, img_w = img.shape[:2]
    report(f"PNG size: {img_w}x{img_h}")

    # Detect background color from corners
    corners = [
        img[0, 0],
        img[0, img_w-1],
        img[img_h-1, 0],
        img[img_h-1, img_w-1]
    ]
    bg_color = tuple(int(v) for v in np.median(corners, axis=0))
    report(f"Background color (BGR): {bg_color}")

    # Add padding to the image so template matching works near edges
    pad_size = int(max(w, h))  # Pad by the size of the element
    padded_img = cv2.copyMakeBorder(
        img, pad_size, pad_size, pad_size, pad_size,
        cv2.BORDER_CONSTANT, value=bg_color
    )
    padded_h, padded_w = padded_img.shape[:2]
    report(f"Padded PNG size: {padded_w}x{padded_h} (pad={pad_size})")

    # Adjust coordinates for padded image
    padded_x = x + pad_size
    padded_y = y + pad_size

    # Calculate center of selected element (in padded coordinates)
    center_x = padded_x + w / 2
    center_y = padded_y + h / 2
    report(f"Element center (padded): ({center_x:.1f}, {center_y:.1f})")

    # Define search region: 3x width and 3x height, centered on element
    search_multiplier = 3.0
    search_w = w * search_multiplier
    search_h = h * search_multiplier
    report(f"Search region multiplier: {search_multiplier}x")
    search_x1 = int(max(0, center_x - search_w / 2))
    search_y1 = int(max(0, center_y - search_h / 2))
    search_x2 = int(min(padded_w, center_x + search_w / 2))
    search_y2 = int(min(padded_h, center_y + search_h / 2))

    report(f"Search region (padded): x1={search_x1}, y1={search_y1}, x2={search_x2}, y2={search_y2}")
    report(f"Search region size: {search_x2 - search_x1}x{search_y2 - search_y1}")

    # Extract search region from padded image
    search_region = padded_img[search_y1:search_y2, search_x1:search_x2]

    if search_region.size == 0:
        report("Search region is empty")
        return geom

    report(f"Search region actual size: {search_region.shape}")

    # Debug: sample some colors from the search region
    sr_h, sr_w = search_region.shape[:2]
    center_color = search_region[sr_h//2, sr_w//2]
    report(f"Search region center color (BGR): {tuple(int(v) for v in center_color)}")

    # Debug: save search region to file for inspection
    try:
        debug_path = "debug_search_region.png"
        cv2.imwrite(debug_path, search_region)
        report(f"DEBUG: Saved search region to {debug_path}")
    except Exception as e:
        report(f"DEBUG: Could not save search region: {e}")

    # Convert pen color to BGR
    pen_bgr = hex_to_bgr(pen_color)
    report(f"Pen color: {pen_color} -> BGR{pen_bgr}")

    # Step 1: Extract shapes from the search region
    report("--- Step 1: Extracting shapes ---")
    min_area_thresh = int(w * h * 0.1)  # Reduced from 0.3 to 0.1
    report(f"Using min_area threshold: {min_area_thresh} (element area: {int(w*h)})")
    shapes = extract_shapes_from_region(search_region, min_area=min_area_thresh, pen_color_bgr=pen_bgr)
    report(f"Found {len(shapes)} shapes")

    for i, s in enumerate(shapes):
        sx, sy, sw, sh = s["bbox"]
        scx, scy = s["center"]
        report(f"  Shape {i}: bbox=({sx},{sy},{sw},{sh}) center=({scx:.1f},{scy:.1f}) type={s['shape_type']}")

    if not shapes:
        report("No shapes found, keeping original position")
        return geom

    # Step 2: Find the shape closest to the element's center
    report("--- Step 2: Finding closest shape ---")
    local_cx = center_x - search_x1
    local_cy = center_y - search_y1
    report(f"Local center (in search region): ({local_cx:.1f}, {local_cy:.1f})")

    closest_shape = find_closest_shape(shapes, local_cx, local_cy, w, h)

    if closest_shape is None:
        report("No matching shape found")
        return geom

    shape_x, shape_y, shape_w, shape_h = closest_shape["bbox"]
    shape_cx, shape_cy = closest_shape["center"]
    report(f"Closest shape: bbox=({shape_x},{shape_y},{shape_w},{shape_h})")
    report(f"Closest shape center: ({shape_cx:.1f}, {shape_cy:.1f})")

    # Step 3: Shape matched - proceed to alignment
    report("--- Step 3: Shape matched successfully ---")
    report(f"Pen color used for detection: {pen_color} -> BGR{pen_bgr}")

    # Step 4: Center-based alignment (simpler and more reliable than template matching)
    # Match the element to the detected shape - use shape's bounding box directly
    report("--- Step 4: Center-based alignment ---")

    # The detected shape's bbox is in search region coordinates
    report(f"Detected shape center (in search region): ({shape_cx:.1f}, {shape_cy:.1f})")
    report(f"Detected shape bbox: x={shape_x}, y={shape_y}, w={shape_w}, h={shape_h}")
    report(f"Original element size: w={w}, h={h}")

    # Use the detected shape's bounding box directly
    # The shape_x, shape_y is already the top-left corner of the detected shape
    # We just need to convert from search region coords to original image coords

    # Convert to original image coordinates
    # search_x1/y1 are in padded coords, so:
    # position_in_padded = search_x1 + shape_x
    # position_in_original = position_in_padded - pad_size
    final_x = search_x1 + shape_x - pad_size
    final_y = search_y1 + shape_y - pad_size

    # Use detected shape size to match the PNG exactly
    final_w = shape_w
    final_h = shape_h

    report(f"Shape position in search region: ({shape_x}, {shape_y})")
    report(f"Shape position in padded coords: ({search_x1 + shape_x}, {search_y1 + shape_y})")

    report("--- Step 5: Final result ---")
    report(f"Coordinate transformation:")
    report(f"  search_x1={search_x1}, search_y1={search_y1} (in padded coords)")
    report(f"  pad_size={pad_size}")
    report(f"  Pos in original image: x={final_x:.1f}, y={final_y:.1f}")
    report(f"Final geometry: x={final_x:.1f}, y={final_y:.1f}, w={final_w}, h={final_h}")

    # Debug: save image showing alignment
    try:
        debug_match = search_region.copy()
        # Draw detected shape bbox (blue) - this is where the element will be placed
        cv2.rectangle(debug_match, (shape_x, shape_y), (shape_x + shape_w, shape_y + shape_h),
                      (255, 0, 0), 2)  # Blue = detected shape = new element position
        # Mark detected shape center (red dot)
        cv2.circle(debug_match, (int(shape_cx), int(shape_cy)), 5, (0, 0, 255), -1)
        cv2.imwrite("debug_match_result.png", debug_match)
        report(f"DEBUG: Saved alignment result to debug_match_result.png")
        report(f"  Blue rect = detected shape (element will match this exactly)")
    except Exception as e:
        report(f"DEBUG: Could not save alignment result: {e}")

    # Step 6: Optimize style parameters (pen width and radius)
    # Position is now fixed - we only optimize style
    report("--- Step 6: Style optimization ---")

    # Sample colors from the detected shape for template rendering
    fill_color, border_color_sampled = sample_colors_at_shape(search_region, closest_shape)
    # Use pen color from JSON for border (more accurate)
    border_color = pen_bgr
    report(f"Fill color (sampled): BGR{fill_color}")
    report(f"Border color (from JSON): BGR{border_color}")

    # Optimize pen width
    report("--- Step 6a: Optimizing pen width ---")
    optimized_pen_width = optimize_pen_width(
        search_region, kind,
        shape_x, shape_y, shape_w, shape_h,
        fill_color, border_color,
        radius=radius,
        current_width=pen_width,
        report=lambda msg: report(msg)
    )

    # Optimize radius for rounded rectangles
    optimized_radius = radius
    if kind == "roundedrect":
        report("--- Step 6b: Optimizing corner radius ---")
        optimized_radius = optimize_radius(
            search_region,
            shape_x, shape_y, shape_w, shape_h,
            fill_color, border_color,
            pen_width=optimized_pen_width,
            current_radius=radius,
            report=lambda msg: report(msg)
        )

    # Step 6c: Sample exact pen color from PNG
    report("--- Step 6c: Sampling exact pen color from PNG ---")
    sampled_pen_bgr = sample_exact_pen_color(search_region, closest_shape, pen_bgr)
    sampled_pen_hex = bgr_to_hex(sampled_pen_bgr)
    report(f"Original pen color: {pen_color} -> BGR{pen_bgr}")
    report(f"Sampled pen color:  {sampled_pen_hex} -> BGR{sampled_pen_bgr}")

    # Build result
    result = {
        "x": round(final_x, 1),
        "y": round(final_y, 1),
        "w": round(final_w, 1),
        "h": round(final_h, 1),
        "pen_width": optimized_pen_width,
        "pen_color": sampled_pen_hex,
    }
    if kind == "roundedrect":
        result["radius"] = round(optimized_radius, 1)

    report(f"=== ALIGNMENT COMPLETE ===")
    report(f"Output: x={result['x']}, y={result['y']}, w={result['w']}, h={result['h']}")
    report(f"Style: pen_width={result['pen_width']}, pen_color={result['pen_color']}")
    if kind == "roundedrect":
        report(f"       radius={result['radius']}")

    return result
