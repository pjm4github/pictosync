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


# ---- Line Alignment Functions ----


def create_color_mask(
    img: np.ndarray,
    pen_color_bgr: Tuple[int, int, int],
    hue_tol: int = 15
) -> np.ndarray:
    """
    Create a color mask for the given pen color.

    Uses strict color matching to avoid picking up other colored items.

    Args:
        img: BGR image
        pen_color_bgr: Pen color in BGR format
        hue_tol: Hue tolerance for color matching (OpenCV hue is 0-179)

    Returns:
        Binary mask where pen color pixels are white
    """
    pen_hsv = bgr_to_hsv(pen_color_bgr)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Tighter tolerances to avoid color leakage from other items
    s_tol = 50  # Reduced from 80
    v_tol = 50  # Reduced from 80

    h_target = pen_hsv[0]
    h_low = h_target - hue_tol
    h_high = h_target + hue_tol

    s_low = max(0, pen_hsv[1] - s_tol)
    s_high = min(255, pen_hsv[1] + s_tol)
    v_low = max(0, pen_hsv[2] - v_tol)
    v_high = min(255, pen_hsv[2] + v_tol)

    # For low saturation colors (grays/blacks), use BGR matching with tight tolerance
    if pen_hsv[1] < 30:
        bgr_tol = hue_tol * 2  # Reduced from hue_tol * 4
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
    elif h_high > 179:
        # Hue wraps around 179 (red colors)
        lower1 = np.array([h_low, s_low, v_low], dtype=np.uint8)
        upper1 = np.array([179, s_high, v_high], dtype=np.uint8)
        lower2 = np.array([0, s_low, v_low], dtype=np.uint8)
        upper2 = np.array([h_high - 180, s_high, v_high], dtype=np.uint8)
        mask1 = cv2.inRange(img_hsv, lower1, upper1)
        mask2 = cv2.inRange(img_hsv, lower2, upper2)
        color_mask = cv2.bitwise_or(mask1, mask2)
    else:
        lower = np.array([h_low, s_low, v_low], dtype=np.uint8)
        upper = np.array([h_high, s_high, v_high], dtype=np.uint8)
        color_mask = cv2.inRange(img_hsv, lower, upper)

    return color_mask


def find_text_in_image(
    img: np.ndarray,
    search_text: str
) -> Optional[Tuple[float, float]]:
    """
    Find text in an image using OCR and return its center position.

    Args:
        img: BGR image
        search_text: Text to search for

    Returns:
        (cx, cy) center position of the text if found, None otherwise
    """
    if not search_text or not search_text.strip():
        return None

    try:
        import pytesseract
    except ImportError:
        print("[LINE_ALIGN] pytesseract not installed, skipping text search")
        return None

    try:
        # Convert to grayscale for OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Get OCR data with bounding boxes
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

        search_lower = search_text.lower().strip()

        # Search for exact or partial match
        for i, text in enumerate(data['text']):
            if not text:
                continue

            text_lower = text.lower().strip()
            if search_lower in text_lower or text_lower in search_lower:
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]

                cx = x + w / 2
                cy = y + h / 2

                print(f"[LINE_ALIGN] Found text '{text}' at ({cx:.1f}, {cy:.1f})")
                return (cx, cy)

        # Try matching multiple words
        words = search_lower.split()
        if len(words) > 1:
            # Look for first word
            for i, text in enumerate(data['text']):
                if not text:
                    continue
                if words[0] in text.lower():
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]

                    cx = x + w / 2
                    cy = y + h / 2

                    print(f"[LINE_ALIGN] Found partial text '{text}' at ({cx:.1f}, {cy:.1f})")
                    return (cx, cy)

    except Exception as e:
        print(f"[LINE_ALIGN] OCR error: {e}")

    return None


def is_line_segment(
    contour: np.ndarray,
    min_aspect_ratio: float = 2.0
) -> bool:
    """
    Check if a contour represents a line segment (not an enclosed shape).

    A line has a high aspect ratio (length >> width) and low area-to-perimeter ratio.

    Args:
        contour: OpenCV contour
        min_aspect_ratio: Minimum ratio of length to width to be considered a line

    Returns:
        True if the contour looks like a line segment
    """
    # Fit a rotated rectangle
    if len(contour) < 5:
        return True  # Small contours are likely lines

    rect = cv2.minAreaRect(contour)
    (cx, cy), (w, h), angle = rect

    if w == 0 or h == 0:
        return True

    # Calculate aspect ratio (larger dimension / smaller dimension)
    aspect_ratio = max(w, h) / min(w, h)

    # Lines have high aspect ratio (lowered to 2.0 to accept shorter segments)
    if aspect_ratio < min_aspect_ratio:
        return False

    # Check area vs perimeter ratio (lines have low fill)
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)

    if perimeter > 0:
        compactness = 4 * np.pi * area / (perimeter * perimeter)
        # Circles have compactness ~1.0, lines have compactness close to 0
        # Increased threshold to 0.4 to be more tolerant
        if compactness > 0.4:  # Too compact to be a line
            return False

    return True


def merge_collinear_segments(
    lines: List[Dict],
    angle_tolerance: float = 15.0,
    distance_tolerance: float = 50.0
) -> List[Dict]:
    """
    Merge collinear line segments that are close together (handles dashed lines).

    Args:
        lines: List of line dicts with x1, y1, x2, y2, angle, etc.
        angle_tolerance: Maximum angle difference to consider collinear (degrees)
        distance_tolerance: Maximum perpendicular distance to consider collinear

    Returns:
        List of merged line dicts
    """
    if not lines:
        return lines

    merged = []
    used = set()

    for i, line in enumerate(lines):
        if i in used:
            continue

        # Start a group with this line
        group = [line]
        used.add(i)

        # Find all collinear segments
        for j, other in enumerate(lines):
            if j in used:
                continue

            # Check angle similarity
            angle_diff = min(
                abs(line["angle"] - other["angle"]),
                180 - abs(line["angle"] - other["angle"])
            )
            if angle_diff > angle_tolerance:
                continue

            # Check if endpoints are close to the line defined by the first segment
            # Use perpendicular distance from other's midpoint to this line
            lx1, ly1 = line["x1"], line["y1"]
            lx2, ly2 = line["x2"], line["y2"]
            ox, oy = other["midpoint"]

            # Perpendicular distance from point to line
            line_len = line["length"]
            if line_len > 0:
                perp_dist = abs((ly2 - ly1) * ox - (lx2 - lx1) * oy + lx2 * ly1 - ly2 * lx1) / line_len
            else:
                perp_dist = float('inf')

            if perp_dist <= distance_tolerance:
                group.append(other)
                used.add(j)

        # Merge all segments in the group by finding the extreme endpoints
        if len(group) == 1:
            merged.append(line)
        else:
            # Collect all endpoints
            all_points = []
            for seg in group:
                all_points.append((seg["x1"], seg["y1"]))
                all_points.append((seg["x2"], seg["y2"]))

            # Find the two points that are furthest apart
            max_dist = 0
            best_p1, best_p2 = all_points[0], all_points[1]
            for pi, p1 in enumerate(all_points):
                for p2 in all_points[pi+1:]:
                    dist = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                    if dist > max_dist:
                        max_dist = dist
                        best_p1, best_p2 = p1, p2

            # Create merged line
            mx1, my1 = best_p1
            mx2, my2 = best_p2
            merged.append({
                "x1": float(mx1),
                "y1": float(my1),
                "x2": float(mx2),
                "y2": float(my2),
                "length": float(max_dist),
                "angle": float(np.degrees(np.arctan2(my2 - my1, mx2 - mx1)) % 180),
                "midpoint": ((mx1 + mx2) / 2, (my1 + my2) / 2),
                "is_dashed": len(group) > 1  # Flag if this was merged from multiple segments
            })
            print(f"[LINE_ALIGN] Merged {len(group)} collinear segments into one line (length={max_dist:.1f})")

    return merged


def detect_lines_in_region(
    img: np.ndarray,
    pen_color_bgr: Tuple[int, int, int],
    min_length: int = 20,
    filter_enclosed: bool = True
) -> List[Dict]:
    """
    Detect line segments (including dashed lines) in an image region.

    Uses Hough Line Transform with increased maxLineGap for dashed lines,
    then merges collinear segments that may be parts of the same dashed line.

    Args:
        img: BGR image region
        pen_color_bgr: Expected pen color in BGR format
        min_length: Minimum line length in pixels
        filter_enclosed: If True, filter out lines that are part of enclosed shapes

    Returns:
        List of detected lines, each with keys:
        - x1, y1: Start point
        - x2, y2: End point
        - length: Line length in pixels
        - angle: Line angle in degrees (0-180)
        - midpoint: (cx, cy) tuple
        - is_dashed: True if detected as dashed line (optional)
    """
    print(f"[LINE_ALIGN] detect_lines_in_region: img size={img.shape}, min_length={min_length}")
    print(f"[LINE_ALIGN] Pen color BGR: {pen_color_bgr}")

    lines_found = []

    # Use a single strict hue tolerance to avoid color leakage from other items
    # Start with tight tolerance, only expand if no lines found
    hue_tolerances = [10, 15, 20]

    for hue_tol in hue_tolerances:
        color_mask = create_color_mask(img, pen_color_bgr, hue_tol)

        # If filtering enclosed shapes, check contours
        if filter_enclosed:
            # Find contours to identify enclosed shapes
            contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Create a mask of only line-like contours
            line_mask = np.zeros_like(color_mask)
            for contour in contours:
                if is_line_segment(contour):
                    cv2.drawContours(line_mask, [contour], 0, 255, -1)

            # Use line_mask for edge detection
            edges = cv2.Canny(line_mask, 50, 150, apertureSize=3)
        else:
            # Apply Canny edge detection directly on the color mask
            edges = cv2.Canny(color_mask, 50, 150, apertureSize=3)

        # Use Hough Line Transform (probabilistic)
        # Large maxLineGap to bridge text in the middle of lines
        detected = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=15,  # Lower threshold for broken lines
            minLineLength=max(10, min_length // 4),  # Shorter min for segments
            maxLineGap=100  # Large gap to bridge text blocks in lines
        )

        if detected is not None and len(detected) > 0:
            print(f"[LINE_ALIGN] Hue tolerance {hue_tol}: found {len(detected)} line segments")
            for line in detected:
                lx1, ly1, lx2, ly2 = line[0]
                length = np.sqrt((lx2 - lx1)**2 + (ly2 - ly1)**2)
                angle = np.degrees(np.arctan2(ly2 - ly1, lx2 - lx1)) % 180
                midpoint = ((lx1 + lx2) / 2, (ly1 + ly2) / 2)

                lines_found.append({
                    "x1": float(lx1),
                    "y1": float(ly1),
                    "x2": float(lx2),
                    "y2": float(ly2),
                    "length": float(length),
                    "angle": float(angle),
                    "midpoint": midpoint
                })
            # Found lines with this tolerance - don't try wider tolerances
            break
        else:
            print(f"[LINE_ALIGN] Hue tolerance {hue_tol}: no lines found, trying wider tolerance")

    # Remove duplicates (lines with very similar endpoints)
    unique_lines = []
    for line in lines_found:
        is_duplicate = False
        for existing in unique_lines:
            # Check if midpoints and angles are similar
            mid_dist = np.sqrt(
                (line["midpoint"][0] - existing["midpoint"][0])**2 +
                (line["midpoint"][1] - existing["midpoint"][1])**2
            )
            angle_diff = min(
                abs(line["angle"] - existing["angle"]),
                180 - abs(line["angle"] - existing["angle"])
            )
            if mid_dist < 15 and angle_diff < 10:
                is_duplicate = True
                # Keep the longer line
                if line["length"] > existing["length"]:
                    unique_lines.remove(existing)
                    unique_lines.append(line)
                break
        if not is_duplicate:
            unique_lines.append(line)

    print(f"[LINE_ALIGN] Unique lines before merge: {len(unique_lines)}")

    # Merge collinear segments (handles dashed lines)
    merged_lines = merge_collinear_segments(unique_lines)

    # Filter by minimum total length
    final_lines = [l for l in merged_lines if l["length"] >= min_length]

    print(f"[LINE_ALIGN] Final lines after merge and filter: {len(final_lines)}")
    return final_lines


def detect_arrowhead_at_endpoint(
    img: np.ndarray,
    endpoint: Tuple[float, float],
    line_angle: float,
    pen_color_bgr: Tuple[int, int, int],
    search_radius: int = 40
) -> Optional[Tuple[Tuple[float, float], float]]:
    """
    Detect if there's a triangular arrowhead at a line endpoint.

    Args:
        img: BGR image
        endpoint: (x, y) coordinates of the endpoint
        line_angle: Angle of the line in degrees (0-180)
        pen_color_bgr: Expected pen color in BGR
        search_radius: Radius to search around the endpoint

    Returns:
        ((tip_x, tip_y), arrow_size) where tip is the arrowhead tip coordinates
        and arrow_size is the length of the arrowhead in pixels,
        or None if no arrowhead detected
    """
    ex, ey = int(endpoint[0]), int(endpoint[1])
    img_h, img_w = img.shape[:2]

    # Extract region around endpoint - larger for vertical lines
    x1 = max(0, ex - search_radius)
    y1 = max(0, ey - search_radius)
    x2 = min(img_w, ex + search_radius)
    y2 = min(img_h, ey + search_radius)

    if x2 - x1 < 10 or y2 - y1 < 10:
        return None

    region = img[y1:y2, x1:x2]

    # Create color mask with slightly wider tolerance for arrowheads
    color_mask = create_color_mask(region, pen_color_bgr, hue_tol=20)

    # Morphological operations to clean up the mask and connect nearby pixels
    kernel = np.ones((3, 3), np.uint8)
    color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print(f"[LINE_ALIGN] Arrow detection at ({ex}, {ey}): found {len(contours)} contours")

    best_arrow = None
    best_arrow_size = 0

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 20 or area > 3000:  # Adjusted area bounds for various arrow sizes
            continue

        # Approximate to polygon with more aggressive simplification
        epsilon = 0.06 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check for triangular shape (3-6 vertices to handle anti-aliasing and filled arrows)
        num_vertices = len(approx)
        if 3 <= num_vertices <= 6:
            # Calculate centroid of shape
            M = cv2.moments(contour)
            if M["m00"] > 0:
                cx = M["m10"] / M["m00"]
                cy = M["m01"] / M["m00"]

                # Check if shape is near the endpoint (within search area)
                local_endpoint = (ex - x1, ey - y1)
                dist_to_endpoint = np.sqrt((cx - local_endpoint[0])**2 + (cy - local_endpoint[1])**2)

                print(f"[LINE_ALIGN]   Contour: area={area:.0f}, vertices={num_vertices}, "
                      f"centroid=({cx:.1f}, {cy:.1f}), dist_to_endpoint={dist_to_endpoint:.1f}")

                if dist_to_endpoint < search_radius * 0.9:  # Increased from 0.8
                    # Find the tip of the arrowhead (vertex furthest from line endpoint)
                    vertices = approx.reshape(-1, 2)
                    max_dist = 0
                    tip_local = vertices[0]
                    tip_idx = 0
                    for i, vertex in enumerate(vertices):
                        dist = np.sqrt((vertex[0] - local_endpoint[0])**2 + (vertex[1] - local_endpoint[1])**2)
                        if dist > max_dist:
                            max_dist = dist
                            tip_local = vertex
                            tip_idx = i

                    # Get the base vertices (all vertices except the tip)
                    base_vertices = [v for i, v in enumerate(vertices) if i != tip_idx]

                    # Calculate arrow size as distance from tip to centroid of base vertices
                    if len(base_vertices) >= 2:
                        base_mid_x = sum(v[0] for v in base_vertices) / len(base_vertices)
                        base_mid_y = sum(v[1] for v in base_vertices) / len(base_vertices)
                        arrow_size = np.sqrt((tip_local[0] - base_mid_x)**2 +
                                             (tip_local[1] - base_mid_y)**2)
                    else:
                        # Fallback: use bounding rect
                        _, _, w, h = cv2.boundingRect(contour)
                        arrow_size = max(w, h)

                    # Keep track of best arrow (largest size that's reasonable)
                    if arrow_size > best_arrow_size and arrow_size < search_radius:
                        best_arrow_size = arrow_size
                        tip_x = float(tip_local[0] + x1)
                        tip_y = float(tip_local[1] + y1)
                        best_arrow = ((tip_x, tip_y), float(arrow_size))
                        print(f"[LINE_ALIGN]   -> Best arrow candidate: tip=({tip_x:.1f}, {tip_y:.1f}), size={arrow_size:.1f}px")

    if best_arrow:
        print(f"[LINE_ALIGN] Arrowhead detected at endpoint ({ex}, {ey}), "
              f"tip at ({best_arrow[0][0]:.1f}, {best_arrow[0][1]:.1f}), size={best_arrow[1]:.1f}px")
        return best_arrow

    return None


def detect_line_pattern_and_color(
    img: np.ndarray,
    x1: float, y1: float,
    x2: float, y2: float,
    bg_color: Tuple[int, int, int],
    pen_color_bgr: Tuple[int, int, int],
    end_sample_percent: float = 0.25
) -> Tuple[str, Tuple[int, int, int], int]:
    """
    Detect line pattern (solid or dashed) and actual line color from the PNG.

    Samples only from regions near the line endpoints to avoid text in the middle.
    For dashed lines, the color is sampled from dash pixels (not background).
    Also measures the dash pattern length for dashed lines.

    Args:
        img: BGR image
        x1, y1: Line start point
        x2, y2: Line end point
        bg_color: Background color (BGR)
        pen_color_bgr: Expected pen color (BGR) for reference
        end_sample_percent: Percentage of line length to sample from each end (default 25%)

    Returns:
        (pattern, color, dash_length) where:
        - pattern is "solid" or "dashed"
        - color is the detected BGR color tuple
        - dash_length is the pixel length of dashes (0 for solid lines)
    """
    line_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    img_h, img_w = img.shape[:2]
    bg_array = np.array(bg_color, dtype=np.int16)
    color_threshold = 40  # Difference from background to be considered line

    # Sample from the first and last 25% of the line (avoiding middle where text may be)
    sample_length = max(20, int(line_length * end_sample_percent))

    def sample_region(t_start: float, t_end: float):
        """Sample pixels along a portion of the line."""
        pixels = []
        is_line = []
        num_samples = max(10, int(abs(t_end - t_start) * line_length))

        for i in range(num_samples):
            t = t_start + (i + 0.5) / num_samples * (t_end - t_start)
            px = int(x1 + t * (x2 - x1))
            py = int(y1 + t * (y2 - y1))

            if 0 <= px < img_w and 0 <= py < img_h:
                pixel = img[py, px]
                diff = np.sum(np.abs(pixel.astype(np.int16) - bg_array))

                if diff > color_threshold:
                    is_line.append(True)
                    pixels.append(pixel)
                else:
                    is_line.append(False)

        return pixels, is_line

    # Sample from start region (0% to 25%)
    start_pixels, start_is_line = sample_region(0.0, end_sample_percent)

    # Sample from end region (75% to 100%)
    end_pixels, end_is_line = sample_region(1.0 - end_sample_percent, 1.0)

    # Combine samples from both ends
    line_pixels = start_pixels + end_pixels
    is_line_pixel = start_is_line + end_is_line

    print(f"[LINE_ALIGN] Sampling line ends: {len(start_pixels)} start pixels, {len(end_pixels)} end pixels")

    if not is_line_pixel:
        return ("solid", pen_color_bgr, 0)

    # Count transitions between line and background (check each region separately)
    def count_transitions(is_line_list):
        transitions = 0
        for i in range(1, len(is_line_list)):
            if is_line_list[i] != is_line_list[i-1]:
                transitions += 1
        return transitions

    start_transitions = count_transitions(start_is_line)
    end_transitions = count_transitions(end_is_line)
    total_transitions = start_transitions + end_transitions

    # Count line pixels vs background pixels
    line_pixel_count = sum(is_line_pixel)
    bg_pixel_count = len(is_line_pixel) - line_pixel_count
    total_samples = len(is_line_pixel)

    bg_ratio = bg_pixel_count / total_samples if total_samples > 0 else 0

    # If more than 20% of samples are background AND there are multiple transitions, it's dashed
    if bg_ratio > 0.20 and total_transitions >= 2:
        pattern = "dashed"
        print(f"[LINE_ALIGN] Line pattern: dashed (bg_ratio={bg_ratio:.2f}, transitions={total_transitions})")

        # Measure dash lengths by finding runs of line pixels (combine both regions)
        dash_lengths = []

        for is_line_list in [start_is_line, end_is_line]:
            current_run = 0
            in_dash = False

            for is_line in is_line_list:
                if is_line:
                    current_run += 1
                    in_dash = True
                else:
                    if in_dash and current_run > 0:
                        dash_lengths.append(current_run)
                    current_run = 0
                    in_dash = False

            # Don't forget the last run
            if in_dash and current_run > 0:
                dash_lengths.append(current_run)

        # Use median dash length
        if dash_lengths:
            dash_length = int(np.median(dash_lengths))
            print(f"[LINE_ALIGN] Dash lengths: {dash_lengths}, median={dash_length}")
        else:
            dash_length = 10  # Default
    else:
        pattern = "solid"
        dash_length = 0
        print(f"[LINE_ALIGN] Line pattern: solid (bg_ratio={bg_ratio:.2f}, transitions={total_transitions})")

    # Get line color from non-background pixels
    if line_pixels:
        line_pixels_array = np.array(line_pixels)
        detected_color = tuple(int(v) for v in np.median(line_pixels_array, axis=0))
        print(f"[LINE_ALIGN] Detected line color (BGR): {detected_color}")
    else:
        detected_color = pen_color_bgr
        print(f"[LINE_ALIGN] No line pixels found, using JSON pen color")

    return (pattern, detected_color, dash_length)


def find_closest_line(
    detected_lines: List[Dict],
    target_x1: float,
    target_y1: float,
    target_x2: float,
    target_y2: float
) -> Optional[Dict]:
    """
    Find the detected line that best matches the target line.

    Uses a combined score:
    - 40% midpoint distance (normalized)
    - 35% angle similarity (0-180 degrees)
    - 25% length similarity

    Args:
        detected_lines: List of detected line dicts
        target_x1, target_y1: Target line start point
        target_x2, target_y2: Target line end point

    Returns:
        Best matching line dict, or None if no suitable match
    """
    if not detected_lines:
        return None

    # Calculate target properties
    target_length = np.sqrt((target_x2 - target_x1)**2 + (target_y2 - target_y1)**2)
    target_midpoint = ((target_x1 + target_x2) / 2, (target_y1 + target_y2) / 2)
    target_angle = np.degrees(np.arctan2(target_y2 - target_y1, target_x2 - target_x1)) % 180

    print(f"[LINE_ALIGN] Target line: midpoint=({target_midpoint[0]:.1f}, {target_midpoint[1]:.1f}), "
          f"length={target_length:.1f}, angle={target_angle:.1f}")

    best_line = None
    best_score = float('inf')

    # Normalize distances based on search area
    max_dist = max(100, target_length)  # Max expected distance
    max_angle_diff = 180.0  # Max angle difference
    max_length_diff = max(50, target_length)  # Max length difference

    for line in detected_lines:
        # Midpoint distance
        mid_dist = np.sqrt(
            (line["midpoint"][0] - target_midpoint[0])**2 +
            (line["midpoint"][1] - target_midpoint[1])**2
        )

        # Angle difference (handle wraparound at 180)
        angle_diff = min(
            abs(line["angle"] - target_angle),
            180 - abs(line["angle"] - target_angle)
        )

        # Length difference
        length_diff = abs(line["length"] - target_length)

        # Normalize and compute combined score (lower is better)
        norm_dist = mid_dist / max_dist
        norm_angle = angle_diff / max_angle_diff
        norm_length = length_diff / max_length_diff

        score = 0.40 * norm_dist + 0.35 * norm_angle + 0.25 * norm_length

        print(f"[LINE_ALIGN] Line at ({line['x1']:.0f},{line['y1']:.0f})->({line['x2']:.0f},{line['y2']:.0f}): "
              f"dist={mid_dist:.1f}, angle_diff={angle_diff:.1f}, len_diff={length_diff:.1f}, score={score:.4f}")

        if score < best_score:
            best_score = score
            best_line = line

    if best_line:
        print(f"[LINE_ALIGN] Best match score: {best_score:.4f}")

    return best_line


def sample_line_pen_color(
    img: np.ndarray,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    pen_color_bgr: Tuple[int, int, int],
    end_sample_percent: float = 0.25
) -> Tuple[int, int, int]:
    """
    Sample the pen color from pixels near the ends of the detected line.

    Samples only from regions near the line endpoints to avoid text in the middle.

    Args:
        img: BGR image
        x1, y1: Line start point
        x2, y2: Line end point
        pen_color_bgr: Expected pen color for filtering
        end_sample_percent: Percentage of line to sample from each end (default 25%)

    Returns:
        Sampled BGR color tuple
    """
    samples = []
    num_samples_per_end = 10

    # Sample from start region (0% to 25%)
    for i in range(num_samples_per_end):
        t = (i + 1) / (num_samples_per_end + 1) * end_sample_percent
        px = int(x1 + t * (x2 - x1))
        py = int(y1 + t * (y2 - y1))
        if 0 <= px < img.shape[1] and 0 <= py < img.shape[0]:
            samples.append(img[py, px])

    # Sample from end region (75% to 100%)
    for i in range(num_samples_per_end):
        t = (1.0 - end_sample_percent) + (i + 1) / (num_samples_per_end + 1) * end_sample_percent
        px = int(x1 + t * (x2 - x1))
        py = int(y1 + t * (y2 - y1))
        if 0 <= px < img.shape[1] and 0 <= py < img.shape[0]:
            samples.append(img[py, px])

    if not samples:
        return pen_color_bgr

    samples = np.array(samples)

    # Filter samples by hue similarity to expected color
    pen_hsv = bgr_to_hsv(pen_color_bgr)
    target_hue = pen_hsv[0]

    samples_reshaped = samples.reshape(-1, 1, 3).astype(np.uint8)
    samples_hsv = cv2.cvtColor(samples_reshaped, cv2.COLOR_BGR2HSV).reshape(-1, 3)

    hue_diff = np.abs(samples_hsv[:, 0].astype(np.int16) - target_hue)
    hue_diff = np.minimum(hue_diff, 180 - hue_diff)

    matching_mask = hue_diff < 30

    if np.sum(matching_mask) > 0:
        matching_samples = samples[matching_mask]
        sampled_color = tuple(int(v) for v in np.median(matching_samples, axis=0))
    else:
        sampled_color = tuple(int(v) for v in np.median(samples, axis=0))

    return sampled_color


def optimize_line_pen_width(
    img: np.ndarray,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    pen_color_bgr: Tuple[int, int, int],
    current_width: int = 2,
    end_sample_percent: float = 0.25
) -> int:
    """
    Estimate the pen width of the detected line by analyzing the color mask.

    Samples only from regions near the line endpoints to avoid text in the middle.

    Args:
        img: BGR image
        x1, y1: Line start point
        x2, y2: Line end point
        pen_color_bgr: Pen color in BGR
        current_width: Current pen width as fallback
        end_sample_percent: Percentage of line to sample from each end (default 25%)

    Returns:
        Estimated pen width in pixels
    """
    # Create color mask
    color_mask = create_color_mask(img, pen_color_bgr, hue_tol=25)

    # Sample perpendicular widths at points near the ends of the line
    widths = []
    num_samples_per_end = 5
    line_len = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    if line_len < 1:
        return current_width

    # Unit vector along line
    ux = (x2 - x1) / line_len
    uy = (y2 - y1) / line_len

    # Perpendicular unit vector
    px = -uy
    py = ux

    # Sample from start region (0% to 25%)
    for i in range(num_samples_per_end):
        t = (i + 1) / (num_samples_per_end + 1) * end_sample_percent
        cx = int(x1 + t * (x2 - x1))
        cy = int(y1 + t * (y2 - y1))

        # Count pixels along perpendicular
        width = 0
        for d in range(-20, 21):
            sx = int(cx + d * px)
            sy = int(cy + d * py)
            if 0 <= sx < color_mask.shape[1] and 0 <= sy < color_mask.shape[0]:
                if color_mask[sy, sx] > 0:
                    width += 1

        if width > 0:
            widths.append(width)

    # Sample from end region (75% to 100%)
    for i in range(num_samples_per_end):
        t = (1.0 - end_sample_percent) + (i + 1) / (num_samples_per_end + 1) * end_sample_percent
        cx = int(x1 + t * (x2 - x1))
        cy = int(y1 + t * (y2 - y1))

        # Count pixels along perpendicular
        width = 0
        for d in range(-20, 21):
            sx = int(cx + d * px)
            sy = int(cy + d * py)
            if 0 <= sx < color_mask.shape[1] and 0 <= sy < color_mask.shape[0]:
                if color_mask[sy, sx] > 0:
                    width += 1

        if width > 0:
            widths.append(width)

    if widths:
        estimated_width = int(np.median(widths))
        print(f"[LINE_ALIGN] Estimated pen width: {estimated_width}px (samples from ends: {widths})")
        return max(1, min(estimated_width, 20))

    return current_width


def calculate_line_search_region(
    x1: float, y1: float, x2: float, y2: float,
    expand_percent: float = 0.20
) -> Tuple[int, int, int, int]:
    """
    Calculate the search region as the line's bounding box expanded by a percentage.

    Note: Does NOT clamp to image bounds - caller should handle padding.

    Args:
        x1, y1: Line start point
        x2, y2: Line end point
        expand_percent: Percentage to expand the bounding box (default 20%)

    Returns:
        (search_x1, search_y1, search_x2, search_y2) region bounds (may be negative or exceed image)
    """
    # Get line bounding box
    min_x = min(x1, x2)
    max_x = max(x1, x2)
    min_y = min(y1, y2)
    max_y = max(y1, y2)

    # Calculate bounding box dimensions
    width = max_x - min_x
    height = max_y - min_y

    # Expand by percentage (minimum 20 pixels to handle very short lines)
    expand_x = max(20, width * expand_percent)
    expand_y = max(20, height * expand_percent)

    # Calculate search region with expansion (no clamping)
    search_x1 = int(min_x - expand_x)
    search_y1 = int(min_y - expand_y)
    search_x2 = int(max_x + expand_x)
    search_y2 = int(max_y + expand_y)

    return search_x1, search_y1, search_x2, search_y2


def detect_background_color(img: np.ndarray) -> Tuple[int, int, int]:
    """
    Detect the background color from image corners.

    Args:
        img: BGR image

    Returns:
        Background color as BGR tuple
    """
    img_h, img_w = img.shape[:2]
    corners = [
        img[0, 0],
        img[0, img_w - 1],
        img[img_h - 1, 0],
        img[img_h - 1, img_w - 1]
    ]
    bg_color = tuple(int(v) for v in np.median(corners, axis=0))
    return bg_color


def pad_image_for_search(
    img: np.ndarray,
    search_x1: int, search_y1: int,
    search_x2: int, search_y2: int,
    bg_color: Tuple[int, int, int]
) -> Tuple[np.ndarray, int, int]:
    """
    Pad image with background color to ensure search region fits.

    Args:
        img: Original BGR image
        search_x1, search_y1: Search region top-left (may be negative)
        search_x2, search_y2: Search region bottom-right (may exceed image)
        bg_color: Background color for padding

    Returns:
        (padded_image, offset_x, offset_y) - the padded image and the offset
        to convert original coordinates to padded coordinates
    """
    img_h, img_w = img.shape[:2]

    # Calculate required padding
    pad_left = max(0, -search_x1)
    pad_top = max(0, -search_y1)
    pad_right = max(0, search_x2 - img_w)
    pad_bottom = max(0, search_y2 - img_h)

    if pad_left == 0 and pad_top == 0 and pad_right == 0 and pad_bottom == 0:
        # No padding needed
        return img, 0, 0

    # Pad the image
    padded = cv2.copyMakeBorder(
        img,
        pad_top, pad_bottom, pad_left, pad_right,
        cv2.BORDER_CONSTANT,
        value=bg_color
    )

    return padded, pad_left, pad_top


def detect_line_color_from_region(
    region: np.ndarray,
    bg_color: Tuple[int, int, int],
    color_threshold: int = 30
) -> Optional[Tuple[int, int, int]]:
    """
    Detect the line color in a region by finding non-background pixels.

    Useful for dashed lines where we need to find the actual line color.

    Args:
        region: BGR image region
        bg_color: Background color to exclude
        color_threshold: Minimum difference from background to be considered line

    Returns:
        Detected line color as BGR tuple, or None if not found
    """
    # Calculate difference from background for each pixel
    bg_array = np.array(bg_color, dtype=np.int16)
    diff = np.abs(region.astype(np.int16) - bg_array)
    total_diff = np.sum(diff, axis=2)  # Sum across BGR channels

    # Find pixels that are significantly different from background
    non_bg_mask = total_diff > color_threshold

    if np.sum(non_bg_mask) < 10:
        return None

    # Get the non-background pixels
    non_bg_pixels = region[non_bg_mask]

    # Use median to get the most common line color
    line_color = tuple(int(v) for v in np.median(non_bg_pixels, axis=0))

    return line_color


def search_for_nearby_line(
    img: np.ndarray,
    x1: float, y1: float, x2: float, y2: float,
    pen_bgr: Tuple[int, int, int],
    bg_color: Tuple[int, int, int],
    min_line_length: int,
    max_shift: int = 200,
    shift_step: int = 10,
    report: Optional[Callable[[str], None]] = None
) -> Optional[Tuple[float, float, float, float, List[Dict]]]:
    """
    Search for a nearby line when the initial position doesn't match.

    Shifts the search region left and right in increments until a line is detected,
    then picks the shift with minimum distance from the original position.

    Args:
        img: BGR image (possibly padded)
        x1, y1: Line start point in image coordinates
        x2, y2: Line end point in image coordinates
        pen_bgr: Pen color in BGR format
        bg_color: Background color for padding
        min_line_length: Minimum line length to detect
        max_shift: Maximum shift distance in pixels
        shift_step: Shift increment in pixels
        report: Optional callback for progress reporting

    Returns:
        (shifted_x1, shifted_y1, shifted_x2, shifted_y2, detected_lines)
        or None if no line found within max_shift distance
    """
    def _report(msg: str):
        if report:
            report(msg)
        print(f"[LINE_ALIGN] {msg}")

    _report(f"--- Searching for nearby line (max_shift={max_shift}, step={shift_step}) ---")

    img_h, img_w = img.shape[:2]
    line_angle = np.degrees(np.arctan2(y2 - y1, x2 - x1)) % 180

    # Determine shift direction based on line orientation
    # For horizontal lines (angle near 0 or 180), shift vertically
    # For vertical lines (angle near 90), shift horizontally
    # For diagonal lines, try both horizontal and vertical shifts
    is_mostly_horizontal = line_angle < 30 or line_angle > 150
    is_mostly_vertical = 60 < line_angle < 120

    _report(f"  Line angle: {line_angle:.1f}° (horizontal={is_mostly_horizontal}, vertical={is_mostly_vertical})")

    # Track best result for each direction
    best_results = {}  # shift_amount -> (shifted_coords, detected_lines)

    def try_shift(shift_x: float, shift_y: float) -> Optional[List[Dict]]:
        """Try detecting lines with the given shift offset."""
        shifted_x1 = x1 + shift_x
        shifted_y1 = y1 + shift_y
        shifted_x2 = x2 + shift_x
        shifted_y2 = y2 + shift_y

        # Calculate search region for shifted line
        search_x1, search_y1, search_x2, search_y2 = calculate_line_search_region(
            shifted_x1, shifted_y1, shifted_x2, shifted_y2, expand_percent=0.30  # Larger expansion during search
        )

        # Clamp to image bounds
        search_x1 = max(0, search_x1)
        search_y1 = max(0, search_y1)
        search_x2 = min(img_w, search_x2)
        search_y2 = min(img_h, search_y2)

        if search_x2 - search_x1 < 10 or search_y2 - search_y1 < 10:
            return None

        # Extract and search
        search_region = img[search_y1:search_y2, search_x1:search_x2]
        detected = detect_lines_in_region(
            search_region, pen_bgr,
            min_length=min_line_length,
            filter_enclosed=True
        )

        if detected:
            # Convert coordinates back to image space
            for line in detected:
                line["x1"] += search_x1
                line["y1"] += search_y1
                line["x2"] += search_x1
                line["y2"] += search_y1
                line["midpoint"] = (
                    line["midpoint"][0] + search_x1,
                    line["midpoint"][1] + search_y1
                )

        return detected if detected else None

    # Shift directions based on line orientation
    shift_directions = []

    if is_mostly_horizontal:
        # For horizontal lines, primarily shift vertically (up/down)
        shift_directions.extend([
            (0, 1, "down"),
            (0, -1, "up"),
        ])
    elif is_mostly_vertical:
        # For vertical lines, primarily shift horizontally (left/right)
        shift_directions.extend([
            (1, 0, "right"),
            (-1, 0, "left"),
        ])
    else:
        # For diagonal lines, try all four directions
        shift_directions.extend([
            (1, 0, "right"),
            (-1, 0, "left"),
            (0, 1, "down"),
            (0, -1, "up"),
        ])

    # Search in each direction
    for dx, dy, direction_name in shift_directions:
        _report(f"  Searching {direction_name}...")

        for shift_amount in range(shift_step, max_shift + 1, shift_step):
            shift_x = dx * shift_amount
            shift_y = dy * shift_amount

            detected = try_shift(shift_x, shift_y)

            if detected:
                _report(f"    Found {len(detected)} line(s) at shift=({shift_x}, {shift_y})")
                # Record this result
                total_shift = abs(shift_x) + abs(shift_y)
                if total_shift not in best_results or len(detected) > len(best_results[total_shift][1]):
                    shifted_coords = (x1 + shift_x, y1 + shift_y, x2 + shift_x, y2 + shift_y)
                    best_results[total_shift] = (shifted_coords, detected)
                break  # Found a line in this direction, no need to search further

    if not best_results:
        _report("  No lines found in any direction")
        return None

    # Pick the result with minimum shift distance
    min_shift = min(best_results.keys())
    shifted_coords, detected_lines = best_results[min_shift]

    _report(f"  Best match: shift={min_shift}px, found {len(detected_lines)} lines")
    _report(f"  Shifted line: ({shifted_coords[0]:.1f}, {shifted_coords[1]:.1f}) -> ({shifted_coords[2]:.1f}, {shifted_coords[3]:.1f})")

    return (shifted_coords[0], shifted_coords[1], shifted_coords[2], shifted_coords[3], detected_lines)


def align_line_element(
    png_path: str,
    geom: Dict[str, float],
    pen_color: str = "#000000",
    pen_width: int = 2,
    note_text: str = "",
    label_text: str = "",
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Dict:
    """
    Align a line element to match the corresponding visual line in the PNG.

    Uses text matching from note_text or label_text to find the initial center
    of the line, then detects line segments (including dashed lines) in the
    search region.

    The search region is calculated as 2x line dimensions in each direction:
    - X: from min_x - dx to max_x + dx (3x total width)
    - Y: from min_y - dy to max_y + dy (3x total height)

    Args:
        png_path: Path to the PNG file
        geom: Current geometry dict {x1, y1, x2, y2}
        pen_color: Hex color of the line
        pen_width: Current pen width
        note_text: Text from meta.note to search for in the PNG
        label_text: Text from meta.label to search for in the PNG
        progress_callback: Optional callback for progress updates

    Returns:
        Dict with aligned geometry and style:
        {x1, y1, x2, y2, pen_width, pen_color, arrow_mode}
    """
    x1 = float(geom["x1"])
    y1 = float(geom["y1"])
    x2 = float(geom["x2"])
    y2 = float(geom["y2"])

    iteration = 0

    def report(msg: str):
        nonlocal iteration
        iteration += 1
        print(f"[LINE_ALIGN] {msg}")
        if progress_callback:
            progress_callback(iteration, msg)

    report("=== LINE ALIGNMENT START ===")
    report(f"Input: ({x1:.1f}, {y1:.1f}) -> ({x2:.1f}, {y2:.1f})")
    if note_text:
        report(f"Note text for matching: '{note_text}'")
    if label_text:
        report(f"Label text for matching: '{label_text}'")

    # Load image
    img = cv2.imread(png_path)
    if img is None:
        report("Error: Could not load image")
        return geom

    img_h, img_w = img.shape[:2]
    report(f"PNG size: {img_w}x{img_h}")

    # Convert pen color to BGR
    pen_bgr = hex_to_bgr(pen_color)
    report(f"Pen color: {pen_color} -> BGR{pen_bgr}")

    # Calculate line properties
    dx = x2 - x1
    dy = y2 - y1
    line_length = np.sqrt(dx**2 + dy**2)
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    report(f"Line: dx={dx:.1f}, dy={dy:.1f}, length={line_length:.1f}, midpoint=({mid_x:.1f}, {mid_y:.1f})")

    # Step 0: Try to find text in the image to use as initial line center
    # Try label_text first (usually more specific), then note_text
    text_center = None
    search_texts = []
    if label_text:
        search_texts.append(("label", label_text))
    if note_text:
        search_texts.append(("note", note_text))

    if search_texts:
        report("--- Step 0: Searching for meta text in image ---")
        for text_type, search_text in search_texts:
            report(f"  Searching for {text_type}: '{search_text}'")
            text_center = find_text_in_image(img, search_text)
            if text_center:
                report(f"  Found '{search_text}' at ({text_center[0]:.1f}, {text_center[1]:.1f})")
                # Use text center as the new midpoint for search
                mid_x, mid_y = text_center
                break
        if not text_center:
            report("  No matching text found, using original line position")

    # Detect background color from image corners
    bg_color = detect_background_color(img)
    report(f"Background color (BGR): {bg_color}")

    # Calculate search region: line bounding box + 20% expansion
    # Note: search region may extend beyond image bounds
    search_x1, search_y1, search_x2, search_y2 = calculate_line_search_region(
        x1, y1, x2, y2, expand_percent=0.20
    )

    # Calculate centers for verification
    line_center_x = (x1 + x2) / 2
    line_center_y = (y1 + y2) / 2
    search_center_x = (search_x1 + search_x2) / 2
    search_center_y = (search_y1 + search_y2) / 2

    # Line bounding box dimensions
    bbox_width = abs(x2 - x1)
    bbox_height = abs(y2 - y1)
    expand_x = max(20, bbox_width * 0.20)
    expand_y = max(20, bbox_height * 0.20)

    report("--- Search Region Calculation ---")
    report(f"  Line endpoints: ({x1:.1f}, {y1:.1f}) -> ({x2:.1f}, {y2:.1f})")
    report(f"  Line center: ({line_center_x:.1f}, {line_center_y:.1f})")
    report(f"  Line bounding box: [{min(x1,x2):.1f}, {min(y1,y2):.1f}] to [{max(x1,x2):.1f}, {max(y1,y2):.1f}]")
    report(f"  Bounding box size: {bbox_width:.1f} x {bbox_height:.1f}")
    report(f"  Expansion (20%, min 20px): x={expand_x:.1f}, y={expand_y:.1f}")
    report(f"  Search region (before padding): ({search_x1}, {search_y1}) -> ({search_x2}, {search_y2})")
    report(f"  Search region center: ({search_center_x:.1f}, {search_center_y:.1f})")
    report(f"  Center offset from line: ({search_center_x - line_center_x:.1f}, {search_center_y - line_center_y:.1f})")

    # Pad image if search region extends beyond image bounds
    padded_img, pad_offset_x, pad_offset_y = pad_image_for_search(
        img, search_x1, search_y1, search_x2, search_y2, bg_color
    )

    if pad_offset_x > 0 or pad_offset_y > 0:
        report(f"  Image padded: offset=({pad_offset_x}, {pad_offset_y})")
        padded_h, padded_w = padded_img.shape[:2]
        report(f"  Padded image size: {padded_w}x{padded_h}")

    # Adjust search region coordinates for padded image
    padded_search_x1 = search_x1 + pad_offset_x
    padded_search_y1 = search_y1 + pad_offset_y
    padded_search_x2 = search_x2 + pad_offset_x
    padded_search_y2 = search_y2 + pad_offset_y

    report(f"  Initial search region: ({padded_search_x1}, {padded_search_y1}) -> ({padded_search_x2}, {padded_search_y2})")
    report(f"  Search region size: {padded_search_x2 - padded_search_x1} x {padded_search_y2 - padded_search_y1}")
    report(f"Using pen color for matching (BGR): {pen_bgr}")

    # Calculate target line position in local (search region) coordinates
    # Account for any padding offset
    local_x1 = x1 + pad_offset_x - padded_search_x1
    local_y1 = y1 + pad_offset_y - padded_search_y1
    local_x2 = x2 + pad_offset_x - padded_search_x1
    local_y2 = y2 + pad_offset_y - padded_search_y1

    # Detect lines in the search region (filtering out enclosed shapes)
    report("--- Step 1: Detecting lines (with edge expansion) ---")
    min_line_length = int(line_length * 0.3)  # Allow shorter detected lines

    # Helper function to check if a line touches the edge of the region
    def line_touches_edge(line: Dict, region_w: int, region_h: int, edge_margin: int = 5) -> Dict[str, bool]:
        """Check which edges a line touches."""
        touches = {"left": False, "right": False, "top": False, "bottom": False}
        lx1, ly1, lx2, ly2 = line["x1"], line["y1"], line["x2"], line["y2"]

        if min(lx1, lx2) <= edge_margin:
            touches["left"] = True
        if max(lx1, lx2) >= region_w - edge_margin:
            touches["right"] = True
        if min(ly1, ly2) <= edge_margin:
            touches["top"] = True
        if max(ly1, ly2) >= region_h - edge_margin:
            touches["bottom"] = True

        return touches

    # Iteratively expand the search region if detected lines touch the edges
    max_expansion_iterations = 5
    expansion_amount = 30  # pixels to expand each iteration

    for expansion_iter in range(max_expansion_iterations + 1):
        # Extract search region
        search_region = padded_img[padded_search_y1:padded_search_y2, padded_search_x1:padded_search_x2]
        if search_region.size == 0:
            report("Search region is empty")
            return geom

        region_h, region_w = search_region.shape[:2]

        # Detect lines
        detected_lines = detect_lines_in_region(
            search_region, pen_bgr,
            min_length=min_line_length,
            filter_enclosed=True
        )

        if not detected_lines:
            report(f"Found 0 line segments (iteration {expansion_iter})")
            break

        report(f"Found {len(detected_lines)} line segments (iteration {expansion_iter})")

        # Check if any detected line touches the edge
        needs_expansion = {"left": False, "right": False, "top": False, "bottom": False}
        for line in detected_lines:
            touches = line_touches_edge(line, region_w, region_h)
            for edge, val in touches.items():
                if val:
                    needs_expansion[edge] = True

        # If no edges touched, we're done
        if not any(needs_expansion.values()):
            report(f"Lines contained within region, no expansion needed")
            break

        if expansion_iter >= max_expansion_iterations:
            report(f"Max expansion iterations reached, proceeding with current detection")
            break

        # Expand the search region in the needed directions
        expand_str = ", ".join(k for k, v in needs_expansion.items() if v)
        report(f"Line touches edge(s): {expand_str}, expanding region...")

        padded_h, padded_w = padded_img.shape[:2]
        if needs_expansion["left"]:
            padded_search_x1 = max(0, padded_search_x1 - expansion_amount)
        if needs_expansion["right"]:
            padded_search_x2 = min(padded_w, padded_search_x2 + expansion_amount)
        if needs_expansion["top"]:
            padded_search_y1 = max(0, padded_search_y1 - expansion_amount)
        if needs_expansion["bottom"]:
            padded_search_y2 = min(padded_h, padded_search_y2 + expansion_amount)

        report(f"  New search region: ({padded_search_x1}, {padded_search_y1}) -> ({padded_search_x2}, {padded_search_y2})")

        # Update local coordinates for the expanded region
        local_x1 = x1 + pad_offset_x - padded_search_x1
        local_y1 = y1 + pad_offset_y - padded_search_y1
        local_x2 = x2 + pad_offset_x - padded_search_x1
        local_y2 = y2 + pad_offset_y - padded_search_y1

    # Update search_x1/y1 to reflect any expansion (for coordinate conversion later)
    search_x1 = padded_search_x1 - pad_offset_x
    search_y1 = padded_search_y1 - pad_offset_y
    search_x2 = padded_search_x2 - pad_offset_x
    search_y2 = padded_search_y2 - pad_offset_y

    # Re-extract final search region for debug output
    search_region = padded_img[padded_search_y1:padded_search_y2, padded_search_x1:padded_search_x2]

    # DEBUG: Save color mask and search region for visualization
    try:
        # Save color mask showing what the threshold matching sees
        color_mask = create_color_mask(search_region, pen_bgr, hue_tol=25)
        cv2.imwrite("debug_line_color_mask.png", color_mask)
        report(f"DEBUG: Saved color mask to debug_line_color_mask.png")

        # Save full image with search region rectangle drawn (cyan)
        # Use padded image to show the full search region even if it extends beyond original
        debug_full = padded_img.copy()
        cv2.rectangle(debug_full, (padded_search_x1, padded_search_y1),
                      (padded_search_x2, padded_search_y2), (255, 255, 0), 2)  # Cyan rectangle
        # Draw original line position (magenta) - adjusted for padding
        cv2.line(debug_full, (int(x1 + pad_offset_x), int(y1 + pad_offset_y)),
                 (int(x2 + pad_offset_x), int(y2 + pad_offset_y)), (255, 0, 255), 2)
        # Draw line center (magenta filled circle)
        cv2.circle(debug_full, (int(line_center_x + pad_offset_x), int(line_center_y + pad_offset_y)),
                   6, (255, 0, 255), -1)
        # Draw search region center (cyan filled circle)
        padded_center_x = (padded_search_x1 + padded_search_x2) / 2
        padded_center_y = (padded_search_y1 + padded_search_y2) / 2
        cv2.circle(debug_full, (int(padded_center_x), int(padded_center_y)), 6, (255, 255, 0), -1)
        # Draw crosshairs at search region center
        cv2.line(debug_full, (int(padded_center_x) - 15, int(padded_center_y)),
                 (int(padded_center_x) + 15, int(padded_center_y)), (255, 255, 0), 1)
        cv2.line(debug_full, (int(padded_center_x), int(padded_center_y) - 15),
                 (int(padded_center_x), int(padded_center_y) + 15), (255, 255, 0), 1)
        cv2.imwrite("debug_line_full_image.png", debug_full)
        report(f"DEBUG: Saved full image with search region to debug_line_full_image.png")
        report(f"DEBUG: Cyan rect/crosshair = search region center, Magenta line/dot = original line & center")

        # Save search region with boundary box drawn
        debug_region = search_region.copy()
        region_h, region_w = debug_region.shape[:2]
        region_center_x = region_w // 2
        region_center_y = region_h // 2

        # Draw the search region boundary (green)
        cv2.rectangle(debug_region, (0, 0),
                      (region_w - 1, region_h - 1),
                      (0, 255, 0), 2)

        # Draw crosshairs at region center (green)
        cv2.line(debug_region, (region_center_x - 20, region_center_y),
                 (region_center_x + 20, region_center_y), (0, 255, 0), 1)
        cv2.line(debug_region, (region_center_x, region_center_y - 20),
                 (region_center_x, region_center_y + 20), (0, 255, 0), 1)

        # Draw the target line position (yellow)
        cv2.line(debug_region, (int(local_x1), int(local_y1)),
                 (int(local_x2), int(local_y2)), (0, 255, 255), 2)
        # Draw target line midpoint (yellow filled circle)
        local_mid_x_draw = (local_x1 + local_x2) / 2
        local_mid_y_draw = (local_y1 + local_y2) / 2
        cv2.circle(debug_region, (int(local_mid_x_draw), int(local_mid_y_draw)), 5, (0, 255, 255), -1)

        # Draw all detected lines (red)
        for line in detected_lines:
            lx1, ly1 = int(line["x1"]), int(line["y1"])
            lx2, ly2 = int(line["x2"]), int(line["y2"])
            cv2.line(debug_region, (lx1, ly1), (lx2, ly2), (0, 0, 255), 2)

        cv2.imwrite("debug_line_search_region.png", debug_region)
        report(f"DEBUG: Saved search region to debug_line_search_region.png")
        report(f"DEBUG: Green = boundary & center crosshairs, Yellow = target line & center, Red = detected lines")
        report(f"DEBUG: Target line local coords: ({local_x1:.1f}, {local_y1:.1f}) -> ({local_x2:.1f}, {local_y2:.1f})")
        report(f"DEBUG: Target line local center: ({local_mid_x_draw:.1f}, {local_mid_y_draw:.1f})")
        report(f"DEBUG: Region center: ({region_center_x}, {region_center_y})")
    except Exception as e:
        report(f"DEBUG: Could not save debug images: {e}")

    if not detected_lines:
        report("No lines detected, keeping original position")
        return {
            "x1": round(x1, 1),
            "y1": round(y1, 1),
            "x2": round(x2, 1),
            "y2": round(y2, 1),
            "pen_width": pen_width,
            "pen_color": pen_color,
            "arrow_mode": "none",
        }

    # Find the best matching line
    report("--- Step 2: Finding closest line ---")
    best_line = find_closest_line(detected_lines, local_x1, local_y1, local_x2, local_y2)

    if best_line is None:
        report("No matching line found")
        return {
            "x1": round(x1, 1),
            "y1": round(y1, 1),
            "x2": round(x2, 1),
            "y2": round(y2, 1),
            "pen_width": pen_width,
            "pen_color": pen_color,
            "arrow_mode": "none",
        }

    # Convert detected line back to image coordinates
    new_x1 = best_line["x1"] + search_x1
    new_y1 = best_line["y1"] + search_y1
    new_x2 = best_line["x2"] + search_x1
    new_y2 = best_line["y2"] + search_y1

    report(f"Detected line: ({new_x1:.1f}, {new_y1:.1f}) -> ({new_x2:.1f}, {new_y2:.1f})")

    # Match endpoint order: original p1 should be closer to detected p1
    dist_p1_to_det_p1 = np.sqrt((x1 - new_x1)**2 + (y1 - new_y1)**2)
    dist_p1_to_det_p2 = np.sqrt((x1 - new_x2)**2 + (y1 - new_y2)**2)

    if dist_p1_to_det_p2 < dist_p1_to_det_p1:
        # Swap endpoints
        new_x1, new_x2 = new_x2, new_x1
        new_y1, new_y2 = new_y2, new_y1
        report("Swapped endpoints to match original orientation")

    # Detect arrowheads (use padded image to handle lines near edges)
    report("--- Step 3: Detecting arrowheads ---")
    line_angle = best_line["angle"]
    # Convert coordinates to padded image space for arrow detection
    padded_new_x1 = new_x1 + pad_offset_x
    padded_new_y1 = new_y1 + pad_offset_y
    padded_new_x2 = new_x2 + pad_offset_x
    padded_new_y2 = new_y2 + pad_offset_y

    # Arrow detection now returns ((tip_x, tip_y), arrow_size) or None
    arrow_result_start = detect_arrowhead_at_endpoint(padded_img, (padded_new_x1, padded_new_y1), line_angle, pen_bgr)
    arrow_result_end = detect_arrowhead_at_endpoint(padded_img, (padded_new_x2, padded_new_y2), line_angle, pen_bgr)

    if arrow_result_start and arrow_result_end:
        arrow_mode = "both"
    elif arrow_result_start:
        arrow_mode = "start"
    elif arrow_result_end:
        arrow_mode = "end"
    else:
        arrow_mode = "none"
    report(f"Arrow mode: {arrow_mode}")

    # Collect arrow sizes for averaging
    arrow_sizes = []

    # Extend line endpoints to arrowhead tips
    if arrow_result_start:
        arrow_tip_start, arrow_size_start = arrow_result_start
        arrow_sizes.append(arrow_size_start)
        # Convert tip from padded to original coords
        tip_x = arrow_tip_start[0] - pad_offset_x
        tip_y = arrow_tip_start[1] - pad_offset_y
        report(f"  Start arrow: tip=({tip_x:.1f}, {tip_y:.1f}), size={arrow_size_start:.1f}px")
        report(f"  Extending start point: ({new_x1:.1f}, {new_y1:.1f}) -> ({tip_x:.1f}, {tip_y:.1f})")
        new_x1, new_y1 = tip_x, tip_y

    if arrow_result_end:
        arrow_tip_end, arrow_size_end = arrow_result_end
        arrow_sizes.append(arrow_size_end)
        # Convert tip from padded to original coords
        tip_x = arrow_tip_end[0] - pad_offset_x
        tip_y = arrow_tip_end[1] - pad_offset_y
        report(f"  End arrow: tip=({tip_x:.1f}, {tip_y:.1f}), size={arrow_size_end:.1f}px")
        report(f"  Extending end point: ({new_x2:.1f}, {new_y2:.1f}) -> ({tip_x:.1f}, {tip_y:.1f})")
        new_x2, new_y2 = tip_x, tip_y

    # Calculate average arrow size (or use default if no arrows)
    if arrow_sizes:
        detected_arrow_size = sum(arrow_sizes) / len(arrow_sizes)
        report(f"  Detected arrow size: {detected_arrow_size:.1f}px")
    else:
        detected_arrow_size = None

    # Detect line pattern (solid/dashed) and actual line color from PNG
    report("--- Step 4: Detecting line pattern and color ---")
    # Use padded image coordinates for detection
    padded_new_x1 = new_x1 + pad_offset_x
    padded_new_y1 = new_y1 + pad_offset_y
    padded_new_x2 = new_x2 + pad_offset_x
    padded_new_y2 = new_y2 + pad_offset_y

    line_pattern, detected_line_bgr, dash_length = detect_line_pattern_and_color(
        padded_img,
        padded_new_x1, padded_new_y1,
        padded_new_x2, padded_new_y2,
        bg_color, pen_bgr
    )
    report(f"Line pattern: {line_pattern}")
    if line_pattern == "dashed":
        report(f"Dash pattern length: {dash_length}px")
    detected_line_hex = bgr_to_hex(detected_line_bgr)
    report(f"Detected line color: {detected_line_hex} (BGR{detected_line_bgr})")

    # Estimate pen width (use padded image and detected color)
    report("--- Step 5: Estimating pen width ---")
    estimated_width = optimize_line_pen_width(
        padded_img,
        padded_new_x1, padded_new_y1,
        padded_new_x2, padded_new_y2,
        detected_line_bgr, pen_width
    )
    report(f"Estimated pen width: {estimated_width}px")

    # Build result
    result = {
        "x1": round(new_x1, 1),
        "y1": round(new_y1, 1),
        "x2": round(new_x2, 1),
        "y2": round(new_y2, 1),
        "pen_width": estimated_width,
        "pen_color": detected_line_hex,  # Use detected color from PNG
        "arrow_mode": arrow_mode,
    }

    # Add arrow size if arrows were detected
    if detected_arrow_size is not None:
        result["arrow_size"] = round(detected_arrow_size, 1)

    # Add dash properties if line is dashed
    if line_pattern == "dashed":
        result["dash"] = "dashed"
        result["dash_pattern_length"] = dash_length
        result["dash_solid_percent"] = 50.0

    report("=== LINE ALIGNMENT COMPLETE ===")
    report(f"Output: ({result['x1']}, {result['y1']}) -> ({result['x2']}, {result['y2']})")
    style_info = f"pen_width={result['pen_width']}, pen_color={result['pen_color']}, arrow={result['arrow_mode']}"
    if detected_arrow_size is not None:
        style_info += f", arrow_size={result['arrow_size']}px"
    if line_pattern == "dashed":
        style_info += f", dash={result['dash']}, dash_length={result['dash_pattern_length']}, dash_solid={result['dash_solid_percent']}%"
    report(f"Style: {style_info}")

    return result
