"""
styles.py

Application stylesheets - Foundation (dark) and Bulma (light) themes.
"""

FOUNDATION_STYLE = """
/* === Base Colors === */
QMainWindow {
    background-color: #1e1e1e;
}

QWidget {
    background-color: #252526;
    color: #cccccc;
    font-family: "Segoe UI", "SF Pro Display", sans-serif;
    font-size: 13px;
}

/* === Menu Bar === */
QMenuBar {
    background-color: #333333;
    color: #cccccc;
    border-bottom: 1px solid #404040;
    padding: 2px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #094771;
}

QMenu {
    background-color: #2d2d30;
    border: 1px solid #404040;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #094771;
}

QMenu::separator {
    height: 1px;
    background-color: #404040;
    margin: 4px 8px;
}

/* === Toolbar === */
QToolBar {
    background-color: #333333;
    border: none;
    border-bottom: 1px solid #404040;
    padding: 2px 3px;
    spacing: 1px;
}

QToolBar::separator {
    width: 1px;
    background-color: #505050;
    margin: 3px 6px;
}

QToolBar QToolButton {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #505050;
    border-radius: 3px;
    padding: 2px 4px;
    margin: 0px;
    min-width: 24px;
}

QToolBar QToolButton:hover {
    background-color: #4a4a4a;
    border-color: #606060;
}

QToolBar QToolButton:pressed {
    background-color: #094771;
}

QToolBar QToolButton:checked {
    background-color: #0e639c;
    border: 2px solid #1177bb;
    color: #ffffff;
    font-weight: bold;
}

QToolBar QToolButton:disabled {
    background-color: #2a2a2a;
    color: #666666;
    border: 1px solid #404040;
}

QToolBar QLabel {
    color: #888888;
    padding: 0 8px;
    background-color: transparent;
}

/* === Dock Widgets === */
QDockWidget {
    color: #cccccc;
    titlebar-close-icon: url(close.png);
    titlebar-normal-icon: url(float.png);
}

QDockWidget::title {
    background-color: #2d2d30;
    padding: 8px;
    border-bottom: 1px solid #404040;
    font-weight: bold;
}

QDockWidget::close-button,
QDockWidget::float-button {
    background-color: transparent;
    border: none;
    padding: 2px;
}

QDockWidget::close-button:hover,
QDockWidget::float-button:hover {
    background-color: #404040;
    border-radius: 4px;
}

/* === Tab Widget === */
QTabWidget::pane {
    background-color: #252526;
    border: 1px solid #404040;
    border-radius: 6px;
    padding: 4px;
}

QTabBar::tab {
    background-color: #2d2d30;
    color: #888888;
    border: 1px solid #404040;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #094771;
    color: #ffffff;
    border-color: #0e639c;
}

QTabBar::tab:hover:!selected {
    background-color: #3c3c3c;
    color: #cccccc;
}

/* === Scroll Area === */
QScrollArea {
    background-color: #252526;
    border: none;
}

/* === Scrollbars === */
QScrollBar:vertical {
    background-color: #252526;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #5a5a5a;
    border-radius: 5px;
    min-height: 30px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #6a6a6a;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #252526;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #5a5a5a;
    border-radius: 5px;
    min-width: 30px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #6a6a6a;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* === Form Elements === */
QLabel {
    color: #cccccc;
    background-color: transparent;
}

QLineEdit {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #505050;
    border-radius: 4px;
    padding: 6px 8px;
    selection-background-color: #094771;
}

QLineEdit:focus {
    border-color: #0e639c;
    background-color: #404040;
}

QLineEdit:disabled {
    background-color: #2d2d30;
    color: #666666;
}

QSpinBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #505050;
    border-radius: 4px;
    padding: 4px 8px;
}

QSpinBox:focus {
    border-color: #0e639c;
}

QSpinBox::up-button,
QSpinBox::down-button {
    background-color: #505050;
    border: none;
    width: 16px;
}

QSpinBox::up-button:hover,
QSpinBox::down-button:hover {
    background-color: #606060;
}

QComboBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #505050;
    border-radius: 4px;
    padding: 6px 8px;
    min-width: 80px;
}

QComboBox:hover {
    border-color: #606060;
}

QComboBox:focus {
    border-color: #0e639c;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d30;
    color: #cccccc;
    border: 1px solid #404040;
    selection-background-color: #094771;
    border-radius: 4px;
}

/* === Buttons === */
QPushButton {
    background-color: #0e639c;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-width: 70px;
}

QPushButton:hover {
    background-color: #1177bb;
}

QPushButton:pressed {
    background-color: #094771;
}

QPushButton:disabled {
    background-color: #3c3c3c;
    color: #666666;
}

/* Secondary button style for Delete */
QPushButton#delete_btn {
    background-color: #5a1d1d;
}

QPushButton#delete_btn:hover {
    background-color: #8b2d2d;
}

/* === Text Edit / Code Editor === */
QPlainTextEdit, QTextEdit {
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #404040;
    border-radius: 4px;
    font-family: "Cascadia Code", "Consolas", "Monaco", monospace;
    font-size: 13px;
    selection-background-color: #264f78;
}

QPlainTextEdit:focus, QTextEdit:focus {
    border-color: #0e639c;
}

/* === Status Bar === */
QStatusBar {
    background-color: #007acc;
    color: #ffffff;
    border: none;
    padding: 4px;
}

QStatusBar::item {
    border: none;
}

/* === Graphics View === */
QGraphicsView {
    background-color: #1e1e1e;
    border: 1px solid #404040;
}

/* === Tooltips === */
QToolTip {
    background-color: #2d2d30;
    color: #cccccc;
    border: 1px solid #505050;
    border-radius: 4px;
    padding: 6px;
}

/* === Message Box === */
QMessageBox {
    background-color: #252526;
}

QMessageBox QLabel {
    color: #cccccc;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* === File Dialog === */
QFileDialog {
    background-color: #252526;
}

QFileDialog QLabel {
    color: #cccccc;
}

QFileDialog QLineEdit {
    background-color: #3c3c3c;
}

QFileDialog QListView,
QFileDialog QTreeView {
    background-color: #1e1e1e;
    color: #cccccc;
    border: 1px solid #404040;
}

QFileDialog QListView::item:selected,
QFileDialog QTreeView::item:selected {
    background-color: #094771;
}

/* === Color Dialog === */
QColorDialog {
    background-color: #252526;
}

/* === Compact Form Elements (Property Panel) === */
QDockWidget QLineEdit, PropertyPanel QLineEdit {
    padding: 1px 4px;
}

QDockWidget QSpinBox, PropertyPanel QSpinBox {
    padding: 0px 2px;
}

QDockWidget QComboBox, PropertyPanel QComboBox {
    padding: 1px 4px;
}

QDockWidget QPushButton, PropertyPanel QPushButton {
    padding: 0px 6px;
    margin: 0px;
    min-width: 36px;
    min-height: 0px;
    max-height: 24px;
    border: none;
    border-radius: 3px;
    font-size: 10px;
    background-color: #0e639c;
    color: #ffffff;
}

QDockWidget QPushButton:hover, PropertyPanel QPushButton:hover {
    background-color: #1177bb;
}

QDockWidget QPushButton:pressed, PropertyPanel QPushButton:pressed {
    background-color: #094771;
}

QDockWidget QComboBox, PropertyPanel QComboBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #505050;
}

QDockWidget QSpinBox, PropertyPanel QSpinBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #505050;
}

/* === Splitter === */
QSplitter::handle {
    background-color: #3d8ac4;
}

QSplitter::handle:horizontal {
    width: 3px;
}

QSplitter::handle:vertical {
    height: 3px;
}

QSplitter::handle:hover {
    background-color: #1177bb;
}

/* === Dock Widget Separator === */
QMainWindow::separator {
    background-color: #3d8ac4;
    width: 3px;
    height: 3px;
}

QMainWindow::separator:hover {
    background-color: #1177bb;
}
"""

BULMA_STYLE = """
/* === Bulma-inspired Light Theme === */
/* Primary: #00d1b2 (turquoise), Link: #485fc7, Info: #3e8ed0 */

QMainWindow {
    background-color: #ffffff;
}

QWidget {
    background-color: #ffffff;
    color: #363636;
    font-family: "Nunito", "Segoe UI", "SF Pro Display", sans-serif;
    font-size: 13px;
}

/* === Menu Bar === */
QMenuBar {
    background-color: #fafafa;
    color: #363636;
    border-bottom: 1px solid #dbdbdb;
    padding: 2px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #00d1b2;
    color: #ffffff;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #dbdbdb;
    border-radius: 6px;
    padding: 8px 0;
    box-shadow: 0 8px 16px rgba(10, 10, 10, 0.1);
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 0;
}

QMenu::item:selected {
    background-color: #f5f5f5;
    color: #00d1b2;
}

QMenu::separator {
    height: 1px;
    background-color: #ededed;
    margin: 8px 12px;
}

/* === Toolbar === */
QToolBar {
    background-color: #fafafa;
    border: none;
    border-bottom: 1px solid #dbdbdb;
    padding: 2px 3px;
    spacing: 1px;
}

QToolBar::separator {
    width: 1px;
    background-color: #dbdbdb;
    margin: 3px 8px;
}

QToolBar QToolButton {
    background-color: #ffffff;
    color: #363636;
    border: 1px solid #dbdbdb;
    border-radius: 3px;
    padding: 2px 4px;
    margin: 0px;
    min-width: 24px;
}

QToolBar QToolButton:hover {
    background-color: #f5f5f5;
    border-color: #b5b5b5;
}

QToolBar QToolButton:pressed {
    background-color: #00d1b2;
    color: #ffffff;
}

QToolBar QToolButton:checked {
    background-color: #00d1b2;
    border: 2px solid #00c4a7;
    color: #ffffff;
    font-weight: bold;
}

QToolBar QToolButton:disabled {
    background-color: #f0f0f0;
    color: #b0b0b0;
    border: 1px solid #e0e0e0;
}

QToolBar QLabel {
    color: #7a7a7a;
    padding: 0 8px;
    background-color: transparent;
}

/* === Dock Widgets === */
QDockWidget {
    color: #363636;
}

QDockWidget::title {
    background-color: #f5f5f5;
    padding: 10px;
    border-bottom: 1px solid #dbdbdb;
    font-weight: 600;
}

QDockWidget::close-button,
QDockWidget::float-button {
    background-color: transparent;
    border: none;
    padding: 2px;
}

QDockWidget::close-button:hover,
QDockWidget::float-button:hover {
    background-color: #ededed;
    border-radius: 4px;
}

/* === Tab Widget === */
QTabWidget::pane {
    background-color: #ffffff;
    border: 1px solid #dbdbdb;
    border-radius: 6px;
    padding: 4px;
}

QTabBar::tab {
    background-color: #f5f5f5;
    color: #7a7a7a;
    border: 1px solid #dbdbdb;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 18px;
    margin-right: 2px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #00d1b2;
    color: #ffffff;
    border-color: #00d1b2;
}

QTabBar::tab:hover:!selected {
    background-color: #ededed;
    color: #363636;
}

/* === Scroll Area === */
QScrollArea {
    background-color: #ffffff;
    border: none;
}

/* === Scrollbars === */
QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #dbdbdb;
    border-radius: 5px;
    min-height: 30px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #b5b5b5;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #f5f5f5;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #dbdbdb;
    border-radius: 5px;
    min-width: 30px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #b5b5b5;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* === Form Elements === */
QLabel {
    color: #363636;
    background-color: transparent;
}

QLineEdit {
    background-color: #ffffff;
    color: #363636;
    border: 1px solid #dbdbdb;
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: #00d1b2;
    selection-color: #ffffff;
}

QLineEdit:focus {
    border-color: #00d1b2;
    box-shadow: 0 0 0 2px rgba(0, 209, 178, 0.25);
}

QLineEdit:disabled {
    background-color: #f5f5f5;
    color: #7a7a7a;
}

QSpinBox {
    background-color: #ffffff;
    color: #363636;
    border: 1px solid #dbdbdb;
    border-radius: 6px;
    padding: 6px 10px;
}

QSpinBox:focus {
    border-color: #00d1b2;
}

QSpinBox::up-button,
QSpinBox::down-button {
    background-color: #f5f5f5;
    border: none;
    width: 18px;
}

QSpinBox::up-button:hover,
QSpinBox::down-button:hover {
    background-color: #ededed;
}

QComboBox {
    background-color: #ffffff;
    color: #363636;
    border: 1px solid #dbdbdb;
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 80px;
}

QComboBox:hover {
    border-color: #b5b5b5;
}

QComboBox:focus {
    border-color: #00d1b2;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #363636;
    border: 1px solid #dbdbdb;
    selection-background-color: #00d1b2;
    selection-color: #ffffff;
    border-radius: 6px;
}

/* === Buttons === */
QPushButton {
    background-color: #00d1b2;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    font-weight: 600;
    min-width: 70px;
}

QPushButton:hover {
    background-color: #00c4a7;
}

QPushButton:pressed {
    background-color: #00b89c;
}

QPushButton:disabled {
    background-color: #f5f5f5;
    color: #7a7a7a;
}

/* Secondary button style for Delete */
QPushButton#delete_btn {
    background-color: #f14668;
}

QPushButton#delete_btn:hover {
    background-color: #f03a5f;
}

QPushButton#delete_btn:pressed {
    background-color: #ef2e55;
}

/* === Text Edit / Code Editor === */
QPlainTextEdit, QTextEdit {
    background-color: #ffffff;
    color: #363636;
    border: 1px solid #dbdbdb;
    border-radius: 6px;
    font-family: "Cascadia Code", "Consolas", "Monaco", monospace;
    font-size: 13px;
    selection-background-color: #00d1b2;
    selection-color: #ffffff;
}

QPlainTextEdit:focus, QTextEdit:focus {
    border-color: #00d1b2;
}

/* === Status Bar === */
QStatusBar {
    background-color: #00d1b2;
    color: #ffffff;
    border: none;
    padding: 6px;
}

QStatusBar::item {
    border: none;
}

/* === Graphics View === */
QGraphicsView {
    background-color: #f5f5f5;
    border: 1px solid #dbdbdb;
}

/* === Tooltips === */
QToolTip {
    background-color: #363636;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 8px;
}

/* === Message Box === */
QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #363636;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* === File Dialog === */
QFileDialog {
    background-color: #ffffff;
}

QFileDialog QLabel {
    color: #363636;
}

QFileDialog QLineEdit {
    background-color: #ffffff;
}

QFileDialog QListView,
QFileDialog QTreeView {
    background-color: #ffffff;
    color: #363636;
    border: 1px solid #dbdbdb;
}

QFileDialog QListView::item:selected,
QFileDialog QTreeView::item:selected {
    background-color: #00d1b2;
    color: #ffffff;
}

/* === Color Dialog === */
QColorDialog {
    background-color: #ffffff;
}

/* === Compact Form Elements (Property Panel) === */
QDockWidget QLineEdit, PropertyPanel QLineEdit {
    padding: 1px 4px;
}

QDockWidget QSpinBox, PropertyPanel QSpinBox {
    padding: 0px 2px;
}

QDockWidget QComboBox, PropertyPanel QComboBox {
    padding: 1px 4px;
}

QDockWidget QPushButton, PropertyPanel QPushButton {
    padding: 0px 6px;
    margin: 0px;
    min-width: 36px;
    min-height: 0px;
    max-height: 24px;
    border: none;
    border-radius: 3px;
    font-size: 10px;
    background-color: #00d1b2;
    color: #ffffff;
}

QDockWidget QPushButton:hover, PropertyPanel QPushButton:hover {
    background-color: #00c4a7;
}

QDockWidget QPushButton:pressed, PropertyPanel QPushButton:pressed {
    background-color: #00b89c;
}

QDockWidget QComboBox, PropertyPanel QComboBox {
    background-color: #ffffff;
    color: #363636;
    border: 1px solid #dbdbdb;
}

QDockWidget QSpinBox, PropertyPanel QSpinBox {
    background-color: #ffffff;
    color: #363636;
    border: 1px solid #dbdbdb;
}

/* === Splitter === */
QSplitter::handle {
    background-color: #4de8d4;
}

QSplitter::handle:horizontal {
    width: 3px;
}

QSplitter::handle:vertical {
    height: 3px;
}

QSplitter::handle:hover {
    background-color: #00e5c4;
}

/* === Dock Widget Separator === */
QMainWindow::separator {
    background-color: #4de8d4;
    width: 3px;
    height: 3px;
}

QMainWindow::separator:hover {
    background-color: #00e5c4;
}
"""

BAUHAUS_STYLE = """
/* === Bauhaus-inspired Theme === */
/* Primary colors: Red #e53935, Blue #1e88e5, Yellow #fdd835 */
/* Black #000000, White #ffffff, Gray #f5f5f5 */
/* Sharp geometric edges, no border-radius, bold contrast */

QMainWindow {
    background-color: #ffffff;
}

QWidget {
    background-color: #ffffff;
    color: #000000;
    font-family: "Futura", "Century Gothic", "Arial", sans-serif;
    font-size: 13px;
}

/* === Menu Bar === */
QMenuBar {
    background-color: #000000;
    color: #ffffff;
    border: none;
    padding: 0;
}

QMenuBar::item {
    background-color: transparent;
    padding: 8px 16px;
    border: none;
}

QMenuBar::item:selected {
    background-color: #e53935;
    color: #ffffff;
}

QMenu {
    background-color: #ffffff;
    border: 3px solid #000000;
    padding: 0;
}

QMenu::item {
    padding: 10px 24px;
    border: none;
}

QMenu::item:selected {
    background-color: #fdd835;
    color: #000000;
}

QMenu::separator {
    height: 3px;
    background-color: #000000;
    margin: 0;
}

/* === Toolbar === */
QToolBar {
    background-color: #f5f5f5;
    border: none;
    border-bottom: 3px solid #000000;
    padding: 2px 3px;
    spacing: 1px;
}

QToolBar::separator {
    width: 3px;
    background-color: #000000;
    margin: 0 8px;
}

QToolBar QToolButton {
    background-color: #ffffff;
    color: #000000;
    border: 2px solid #000000;
    border-radius: 0;
    padding: 2px 4px;
    margin: 0px;
    min-width: 24px;
    font-weight: bold;
}

QToolBar QToolButton:hover {
    background-color: #fdd835;
    border-color: #000000;
}

QToolBar QToolButton:pressed {
    background-color: #e53935;
    color: #ffffff;
}

QToolBar QToolButton:checked {
    background-color: #1e88e5;
    border: 3px solid #000000;
    color: #ffffff;
    font-weight: bold;
}

QToolBar QToolButton:disabled {
    background-color: #e8e8e8;
    color: #aaaaaa;
    border: 1px solid #cccccc;
}

QToolBar QLabel {
    color: #000000;
    padding: 0 8px;
    background-color: transparent;
    font-weight: bold;
}

/* === Dock Widgets === */
QDockWidget {
    color: #000000;
}

QDockWidget::title {
    background-color: #e53935;
    color: #ffffff;
    padding: 10px;
    border: none;
    font-weight: bold;
    text-transform: uppercase;
}

QDockWidget::close-button,
QDockWidget::float-button {
    background-color: #ffffff;
    border: 2px solid #000000;
    padding: 2px;
}

QDockWidget::close-button:hover,
QDockWidget::float-button:hover {
    background-color: #fdd835;
}

/* === Tab Widget === */
QTabWidget::pane {
    background-color: #ffffff;
    border: 3px solid #000000;
    border-radius: 0;
    padding: 0;
}

QTabBar::tab {
    background-color: #f5f5f5;
    color: #000000;
    border: 3px solid #000000;
    border-bottom: none;
    border-radius: 0;
    padding: 10px 20px;
    margin-right: 0;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: #1e88e5;
    color: #ffffff;
    border-color: #000000;
}

QTabBar::tab:hover:!selected {
    background-color: #fdd835;
    color: #000000;
}

/* === Scroll Area === */
QScrollArea {
    background-color: #ffffff;
    border: none;
}

/* === Scrollbars === */
QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 16px;
    border: 2px solid #000000;
    border-radius: 0;
}

QScrollBar::handle:vertical {
    background-color: #000000;
    border-radius: 0;
    min-height: 40px;
    margin: 0;
}

QScrollBar::handle:vertical:hover {
    background-color: #e53935;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #f5f5f5;
    height: 16px;
    border: 2px solid #000000;
    border-radius: 0;
}

QScrollBar::handle:horizontal {
    background-color: #000000;
    border-radius: 0;
    min-width: 40px;
    margin: 0;
}

QScrollBar::handle:horizontal:hover {
    background-color: #e53935;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* === Form Elements === */
QLabel {
    color: #000000;
    background-color: transparent;
}

QLineEdit {
    background-color: #ffffff;
    color: #000000;
    border: 3px solid #000000;
    border-radius: 0;
    padding: 8px 12px;
    selection-background-color: #1e88e5;
    selection-color: #ffffff;
}

QLineEdit:focus {
    border-color: #1e88e5;
    border-width: 4px;
}

QLineEdit:disabled {
    background-color: #f5f5f5;
    color: #888888;
}

QSpinBox {
    background-color: #ffffff;
    color: #000000;
    border: 3px solid #000000;
    border-radius: 0;
    padding: 6px 10px;
}

QSpinBox:focus {
    border-color: #1e88e5;
    border-width: 4px;
}

QSpinBox::up-button,
QSpinBox::down-button {
    background-color: #fdd835;
    border: 2px solid #000000;
    border-radius: 0;
    width: 20px;
}

QSpinBox::up-button:hover,
QSpinBox::down-button:hover {
    background-color: #e53935;
}

QComboBox {
    background-color: #ffffff;
    color: #000000;
    border: 3px solid #000000;
    border-radius: 0;
    padding: 8px 12px;
    min-width: 80px;
}

QComboBox:hover {
    border-color: #1e88e5;
}

QComboBox:focus {
    border-color: #1e88e5;
    border-width: 4px;
}

QComboBox::drop-down {
    border: none;
    border-left: 3px solid #000000;
    width: 30px;
    background-color: #fdd835;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #000000;
    border: 3px solid #000000;
    selection-background-color: #1e88e5;
    selection-color: #ffffff;
    border-radius: 0;
}

/* === Buttons === */
QPushButton {
    background-color: #1e88e5;
    color: #ffffff;
    border: 3px solid #000000;
    border-radius: 0;
    padding: 10px 20px;
    font-weight: bold;
    min-width: 70px;
    text-transform: uppercase;
}

QPushButton:hover {
    background-color: #fdd835;
    color: #000000;
}

QPushButton:pressed {
    background-color: #000000;
    color: #ffffff;
}

QPushButton:disabled {
    background-color: #f5f5f5;
    color: #888888;
    border-color: #888888;
}

/* Secondary button style for Delete */
QPushButton#delete_btn {
    background-color: #e53935;
}

QPushButton#delete_btn:hover {
    background-color: #fdd835;
    color: #000000;
}

QPushButton#delete_btn:pressed {
    background-color: #000000;
    color: #ffffff;
}

/* === Text Edit / Code Editor === */
QPlainTextEdit, QTextEdit {
    background-color: #ffffff;
    color: #000000;
    border: 3px solid #000000;
    border-radius: 0;
    font-family: "Consolas", "Monaco", monospace;
    font-size: 13px;
    selection-background-color: #1e88e5;
    selection-color: #ffffff;
}

QPlainTextEdit:focus, QTextEdit:focus {
    border-color: #1e88e5;
    border-width: 4px;
}

/* === Status Bar === */
QStatusBar {
    background-color: #000000;
    color: #ffffff;
    border: none;
    padding: 6px;
    font-weight: bold;
}

QStatusBar::item {
    border: none;
}

/* === Graphics View === */
QGraphicsView {
    background-color: #f5f5f5;
    border: 3px solid #000000;
}

/* === Tooltips === */
QToolTip {
    background-color: #fdd835;
    color: #000000;
    border: 2px solid #000000;
    border-radius: 0;
    padding: 8px;
    font-weight: bold;
}

/* === Message Box === */
QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #000000;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* === File Dialog === */
QFileDialog {
    background-color: #ffffff;
}

QFileDialog QLabel {
    color: #000000;
}

QFileDialog QLineEdit {
    background-color: #ffffff;
}

QFileDialog QListView,
QFileDialog QTreeView {
    background-color: #ffffff;
    color: #000000;
    border: 3px solid #000000;
}

QFileDialog QListView::item:selected,
QFileDialog QTreeView::item:selected {
    background-color: #1e88e5;
    color: #ffffff;
}

/* === Color Dialog === */
QColorDialog {
    background-color: #ffffff;
}

/* === Compact Form Elements (Property Panel) === */
QDockWidget QLineEdit, PropertyPanel QLineEdit {
    padding: 1px 4px;
}

QDockWidget QSpinBox, PropertyPanel QSpinBox {
    padding: 0px 2px;
}

QDockWidget QComboBox, PropertyPanel QComboBox {
    padding: 1px 4px;
}

QDockWidget QPushButton, PropertyPanel QPushButton {
    padding: 0px 6px;
    margin: 0px;
    min-width: 36px;
    min-height: 0px;
    max-height: 24px;
    border: 2px solid #000000;
    border-radius: 0;
    font-size: 10px;
    background-color: #1e88e5;
    color: #ffffff;
}

QDockWidget QPushButton:hover, PropertyPanel QPushButton:hover {
    background-color: #fdd835;
    color: #000000;
}

QDockWidget QPushButton:pressed, PropertyPanel QPushButton:pressed {
    background-color: #000000;
    color: #ffffff;
}

QDockWidget QComboBox, PropertyPanel QComboBox {
    background-color: #ffffff;
    color: #000000;
    border: 2px solid #000000;
}

QDockWidget QSpinBox, PropertyPanel QSpinBox {
    background-color: #ffffff;
    color: #000000;
    border: 2px solid #000000;
}

/* === Splitter === */
QSplitter::handle {
    background-color: #f06b68;
}

QSplitter::handle:horizontal {
    width: 3px;
}

QSplitter::handle:vertical {
    height: 3px;
}

QSplitter::handle:hover {
    background-color: #ff5252;
}

/* === Dock Widget Separator === */
QMainWindow::separator {
    background-color: #f06b68;
    width: 3px;
    height: 3px;
}

QMainWindow::separator:hover {
    background-color: #ff5252;
}
"""

NEUMORPHISM_STYLE = """
/* === Neumorphism (Soft UI) Theme === */
/* Base: #e0e5ec, Light shadow: #ffffff, Dark shadow: #a3b1c6 */
/* Soft, extruded appearance with subtle depth */

QMainWindow {
    background-color: #e0e5ec;
}

QWidget {
    background-color: #e0e5ec;
    color: #4a5568;
    font-family: "Poppins", "Segoe UI", "SF Pro Display", sans-serif;
    font-size: 13px;
}

/* === Menu Bar === */
QMenuBar {
    background-color: #e0e5ec;
    color: #4a5568;
    border: none;
    padding: 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 8px 14px;
    border-radius: 10px;
}

QMenuBar::item:selected {
    background-color: #e0e5ec;
    color: #6c5ce7;
}

QMenu {
    background-color: #e0e5ec;
    border: none;
    border-radius: 15px;
    padding: 10px;
}

QMenu::item {
    padding: 10px 24px;
    border-radius: 10px;
    margin: 2px 4px;
}

QMenu::item:selected {
    background-color: #d1d9e6;
    color: #6c5ce7;
}

QMenu::separator {
    height: 1px;
    background-color: #c8d0e0;
    margin: 8px 16px;
}

/* === Toolbar === */
QToolBar {
    background-color: #e0e5ec;
    border: none;
    padding: 2px 3px;
    spacing: 1px;
}

QToolBar::separator {
    width: 1px;
    background-color: #c8d0e0;
    margin: 5px 10px;
}

QToolBar QToolButton {
    background-color: #e0e5ec;
    color: #4a5568;
    border: none;
    border-radius: 6px;
    padding: 2px 4px;
    margin: 0px;
    min-width: 24px;
}

QToolBar QToolButton:hover {
    background-color: #d1d9e6;
    color: #6c5ce7;
}

QToolBar QToolButton:pressed {
    background-color: #c8d0e0;
}

QToolBar QToolButton:checked {
    background-color: #d1d9e6;
    color: #6c5ce7;
    font-weight: bold;
}

QToolBar QToolButton:disabled {
    background-color: #d5dbe3;
    color: #a0aab4;
    border: 1px solid #c8cfd6;
}

QToolBar QLabel {
    color: #718096;
    padding: 0 10px;
    background-color: transparent;
}

/* === Dock Widgets === */
QDockWidget {
    color: #4a5568;
}

QDockWidget::title {
    background-color: #e0e5ec;
    padding: 12px;
    border: none;
    font-weight: 600;
    color: #6c5ce7;
}

QDockWidget::close-button,
QDockWidget::float-button {
    background-color: #e0e5ec;
    border: none;
    border-radius: 8px;
    padding: 4px;
}

QDockWidget::close-button:hover,
QDockWidget::float-button:hover {
    background-color: #d1d9e6;
}

/* === Tab Widget === */
QTabWidget::pane {
    background-color: #e0e5ec;
    border: none;
    border-radius: 15px;
    padding: 10px;
}

QTabBar::tab {
    background-color: #e0e5ec;
    color: #718096;
    border: none;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    padding: 12px 20px;
    margin-right: 4px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #d1d9e6;
    color: #6c5ce7;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background-color: #d9e0ea;
    color: #4a5568;
}

/* === Scroll Area === */
QScrollArea {
    background-color: #e0e5ec;
    border: none;
    border-radius: 10px;
}

/* === Scrollbars === */
QScrollBar:vertical {
    background-color: #e0e5ec;
    width: 14px;
    border-radius: 7px;
    margin: 4px;
}

QScrollBar::handle:vertical {
    background-color: #c8d0e0;
    border-radius: 5px;
    min-height: 40px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a3b1c6;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #e0e5ec;
    height: 14px;
    border-radius: 7px;
    margin: 4px;
}

QScrollBar::handle:horizontal {
    background-color: #c8d0e0;
    border-radius: 5px;
    min-width: 40px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #a3b1c6;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* === Form Elements === */
QLabel {
    color: #4a5568;
    background-color: transparent;
}

QLineEdit {
    background-color: #e0e5ec;
    color: #4a5568;
    border: none;
    border-radius: 12px;
    padding: 10px 14px;
    selection-background-color: #6c5ce7;
    selection-color: #ffffff;
}

QLineEdit:focus {
    background-color: #d9e0ea;
}

QLineEdit:disabled {
    background-color: #e8ecf2;
    color: #a0aec0;
}

QSpinBox {
    background-color: #e0e5ec;
    color: #4a5568;
    border: none;
    border-radius: 12px;
    padding: 8px 12px;
}

QSpinBox:focus {
    background-color: #d9e0ea;
}

QSpinBox::up-button,
QSpinBox::down-button {
    background-color: #d1d9e6;
    border: none;
    border-radius: 6px;
    width: 20px;
    margin: 2px;
}

QSpinBox::up-button:hover,
QSpinBox::down-button:hover {
    background-color: #c8d0e0;
}

QComboBox {
    background-color: #e0e5ec;
    color: #4a5568;
    border: none;
    border-radius: 12px;
    padding: 10px 14px;
    min-width: 80px;
}

QComboBox:hover {
    background-color: #d9e0ea;
}

QComboBox:focus {
    background-color: #d9e0ea;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
    border-top-right-radius: 12px;
    border-bottom-right-radius: 12px;
}

QComboBox QAbstractItemView {
    background-color: #e0e5ec;
    color: #4a5568;
    border: none;
    border-radius: 12px;
    selection-background-color: #d1d9e6;
    selection-color: #6c5ce7;
    padding: 6px;
}

/* === Buttons === */
QPushButton {
    background-color: #e0e5ec;
    color: #6c5ce7;
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    font-weight: 600;
    min-width: 70px;
}

QPushButton:hover {
    background-color: #d9e0ea;
    color: #5b4cdb;
}

QPushButton:pressed {
    background-color: #d1d9e6;
}

QPushButton:disabled {
    background-color: #e8ecf2;
    color: #a0aec0;
}

/* Secondary button style for Delete */
QPushButton#delete_btn {
    color: #e53e3e;
}

QPushButton#delete_btn:hover {
    background-color: #fee2e2;
    color: #c53030;
}

QPushButton#delete_btn:pressed {
    background-color: #fecaca;
}

/* === Text Edit / Code Editor === */
QPlainTextEdit, QTextEdit {
    background-color: #d9e0ea;
    color: #4a5568;
    border: none;
    border-radius: 12px;
    font-family: "Cascadia Code", "Consolas", "Monaco", monospace;
    font-size: 13px;
    selection-background-color: #6c5ce7;
    selection-color: #ffffff;
    padding: 8px;
}

QPlainTextEdit:focus, QTextEdit:focus {
    background-color: #d1d9e6;
}

/* === Status Bar === */
QStatusBar {
    background-color: #e0e5ec;
    color: #6c5ce7;
    border: none;
    padding: 8px;
    font-weight: 500;
}

QStatusBar::item {
    border: none;
}

/* === Graphics View === */
QGraphicsView {
    background-color: #d9e0ea;
    border: none;
    border-radius: 12px;
}

/* === Tooltips === */
QToolTip {
    background-color: #4a5568;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
}

/* === Message Box === */
QMessageBox {
    background-color: #e0e5ec;
}

QMessageBox QLabel {
    color: #4a5568;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* === File Dialog === */
QFileDialog {
    background-color: #e0e5ec;
}

QFileDialog QLabel {
    color: #4a5568;
}

QFileDialog QLineEdit {
    background-color: #e0e5ec;
}

QFileDialog QListView,
QFileDialog QTreeView {
    background-color: #d9e0ea;
    color: #4a5568;
    border: none;
    border-radius: 10px;
}

QFileDialog QListView::item:selected,
QFileDialog QTreeView::item:selected {
    background-color: #d1d9e6;
    color: #6c5ce7;
}

/* === Color Dialog === */
QColorDialog {
    background-color: #e0e5ec;
}

/* === Compact Form Elements (Property Panel) === */
QDockWidget QLineEdit, PropertyPanel QLineEdit {
    padding: 1px 4px;
}

QDockWidget QSpinBox, PropertyPanel QSpinBox {
    padding: 0px 2px;
}

QDockWidget QComboBox, PropertyPanel QComboBox {
    padding: 1px 4px;
}

QDockWidget QPushButton, PropertyPanel QPushButton {
    padding: 0px 6px;
    margin: 0px;
    min-width: 36px;
    min-height: 0px;
    max-height: 24px;
    border: none;
    border-radius: 6px;
    font-size: 10px;
    background-color: #e0e5ec;
    color: #6c5ce7;
}

QDockWidget QPushButton:hover, PropertyPanel QPushButton:hover {
    background-color: #d9e0ea;
    color: #5b4cdb;
}

QDockWidget QPushButton:pressed, PropertyPanel QPushButton:pressed {
    background-color: #d1d9e6;
}

QDockWidget QComboBox, PropertyPanel QComboBox {
    background-color: #e0e5ec;
    color: #4a5568;
    border: none;
}

QDockWidget QSpinBox, PropertyPanel QSpinBox {
    background-color: #e0e5ec;
    color: #4a5568;
    border: none;
}

/* === Splitter === */
QSplitter::handle {
    background-color: #9d90f0;
    border-radius: 1px;
}

QSplitter::handle:horizontal {
    width: 3px;
}

QSplitter::handle:vertical {
    height: 3px;
}

QSplitter::handle:hover {
    background-color: #8577ed;
}

/* === Dock Widget Separator === */
QMainWindow::separator {
    background-color: #9d90f0;
    width: 3px;
    height: 3px;
}

QMainWindow::separator:hover {
    background-color: #8577ed;
}
"""

MATERIALIZE_STYLE = """
/* === Materialize (Material Design) Theme === */
/* Primary: #3f51b5 (Indigo), Accent: #ff4081 (Pink) */
/* Roboto font, elevation shadows, bold colors */

QMainWindow {
    background-color: #fafafa;
}

QWidget {
    background-color: #fafafa;
    color: #212121;
    font-family: "Roboto", "Segoe UI", sans-serif;
    font-size: 13px;
}

/* === Menu Bar === */
QMenuBar {
    background-color: #3f51b5;
    color: #ffffff;
    border: none;
    padding: 0;
}

QMenuBar::item {
    background-color: transparent;
    padding: 10px 16px;
}

QMenuBar::item:selected {
    background-color: #5c6bc0;
}

QMenu {
    background-color: #ffffff;
    border: none;
    border-radius: 2px;
    padding: 8px 0;
}

QMenu::item {
    padding: 12px 24px;
}

QMenu::item:selected {
    background-color: #e8eaf6;
    color: #3f51b5;
}

QMenu::separator {
    height: 1px;
    background-color: #e0e0e0;
    margin: 4px 0;
}

/* === Toolbar === */
QToolBar {
    background-color: #3f51b5;
    border: none;
    padding: 2px 3px;
    spacing: 1px;
}

QToolBar::separator {
    width: 1px;
    background-color: #5c6bc0;
    margin: 3px 8px;
}

QToolBar QToolButton {
    background-color: transparent;
    color: #ffffff;
    border: none;
    border-radius: 2px;
    padding: 2px 4px;
    margin: 0px;
    min-width: 24px;
}

QToolBar QToolButton:hover {
    background-color: #5c6bc0;
}

QToolBar QToolButton:pressed {
    background-color: #7986cb;
}

QToolBar QToolButton:checked {
    background-color: #ff4081;
    color: #ffffff;
    font-weight: bold;
}

QToolBar QToolButton:disabled {
    background-color: #37474f;
    color: #78909c;
    border: 1px solid #455a64;
}

QToolBar QLabel {
    color: rgba(255, 255, 255, 0.7);
    padding: 0 8px;
    background-color: transparent;
}

/* === Dock Widgets === */
QDockWidget {
    color: #212121;
}

QDockWidget::title {
    background-color: #e8eaf6;
    padding: 12px;
    border: none;
    font-weight: 500;
    color: #3f51b5;
}

QDockWidget::close-button,
QDockWidget::float-button {
    background-color: transparent;
    border: none;
    padding: 4px;
}

QDockWidget::close-button:hover,
QDockWidget::float-button:hover {
    background-color: #c5cae9;
    border-radius: 12px;
}

/* === Tab Widget === */
QTabWidget::pane {
    background-color: #ffffff;
    border: none;
    border-top: 2px solid #3f51b5;
}

QTabBar::tab {
    background-color: transparent;
    color: #757575;
    border: none;
    padding: 14px 24px;
    margin-right: 0;
    font-weight: 500;
}

QTabBar::tab:selected {
    color: #3f51b5;
    border-bottom: 2px solid #ff4081;
}

QTabBar::tab:hover:!selected {
    color: #3f51b5;
    background-color: #e8eaf6;
}

/* === Scroll Area === */
QScrollArea {
    background-color: #fafafa;
    border: none;
}

/* === Scrollbars === */
QScrollBar:vertical {
    background-color: #fafafa;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #bdbdbd;
    border-radius: 4px;
    min-height: 40px;
}

QScrollBar::handle:vertical:hover {
    background-color: #9e9e9e;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #fafafa;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background-color: #bdbdbd;
    border-radius: 4px;
    min-width: 40px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #9e9e9e;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* === Form Elements === */
QLabel {
    color: #212121;
    background-color: transparent;
}

QLineEdit {
    background-color: transparent;
    color: #212121;
    border: none;
    border-bottom: 1px solid #9e9e9e;
    border-radius: 0;
    padding: 8px 0;
    selection-background-color: #c5cae9;
}

QLineEdit:focus {
    border-bottom: 2px solid #3f51b5;
}

QLineEdit:disabled {
    color: #9e9e9e;
    border-bottom: 1px dotted #bdbdbd;
}

QSpinBox {
    background-color: transparent;
    color: #212121;
    border: none;
    border-bottom: 1px solid #9e9e9e;
    border-radius: 0;
    padding: 6px 0;
}

QSpinBox:focus {
    border-bottom: 2px solid #3f51b5;
}

QSpinBox::up-button,
QSpinBox::down-button {
    background-color: transparent;
    border: none;
    width: 20px;
}

QSpinBox::up-button:hover,
QSpinBox::down-button:hover {
    background-color: #e0e0e0;
}

QComboBox {
    background-color: transparent;
    color: #212121;
    border: none;
    border-bottom: 1px solid #9e9e9e;
    border-radius: 0;
    padding: 8px 0;
    min-width: 80px;
}

QComboBox:focus {
    border-bottom: 2px solid #3f51b5;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #212121;
    border: none;
    selection-background-color: #e8eaf6;
    selection-color: #3f51b5;
}

/* === Buttons === */
QPushButton {
    background-color: #3f51b5;
    color: #ffffff;
    border: none;
    border-radius: 2px;
    padding: 10px 20px;
    font-weight: 500;
    min-width: 70px;
    text-transform: uppercase;
}

QPushButton:hover {
    background-color: #5c6bc0;
}

QPushButton:pressed {
    background-color: #3949ab;
}

QPushButton:disabled {
    background-color: #e0e0e0;
    color: #9e9e9e;
}

/* Secondary button style for Delete */
QPushButton#delete_btn {
    background-color: #f44336;
}

QPushButton#delete_btn:hover {
    background-color: #e57373;
}

QPushButton#delete_btn:pressed {
    background-color: #d32f2f;
}

/* === Text Edit / Code Editor === */
QPlainTextEdit, QTextEdit {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #e0e0e0;
    border-radius: 2px;
    font-family: "Roboto Mono", "Consolas", monospace;
    font-size: 13px;
    selection-background-color: #c5cae9;
    padding: 8px;
}

QPlainTextEdit:focus, QTextEdit:focus {
    border: 2px solid #3f51b5;
}

/* === Status Bar === */
QStatusBar {
    background-color: #3f51b5;
    color: #ffffff;
    border: none;
    padding: 8px;
}

QStatusBar::item {
    border: none;
}

/* === Graphics View === */
QGraphicsView {
    background-color: #eeeeee;
    border: 1px solid #e0e0e0;
}

/* === Tooltips === */
QToolTip {
    background-color: #616161;
    color: #ffffff;
    border: none;
    border-radius: 2px;
    padding: 8px 12px;
}

/* === Message Box === */
QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #212121;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* === File Dialog === */
QFileDialog {
    background-color: #fafafa;
}

QFileDialog QLabel {
    color: #212121;
}

QFileDialog QLineEdit {
    background-color: transparent;
}

QFileDialog QListView,
QFileDialog QTreeView {
    background-color: #ffffff;
    color: #212121;
    border: 1px solid #e0e0e0;
}

QFileDialog QListView::item:selected,
QFileDialog QTreeView::item:selected {
    background-color: #e8eaf6;
    color: #3f51b5;
}

/* === Color Dialog === */
QColorDialog {
    background-color: #fafafa;
}

/* === Compact Form Elements (Property Panel) === */
QDockWidget QLineEdit, PropertyPanel QLineEdit {
    padding: 1px 0;
}

QDockWidget QSpinBox, PropertyPanel QSpinBox {
    padding: 0px 0;
}

QDockWidget QComboBox, PropertyPanel QComboBox {
    padding: 1px 0;
}

QDockWidget QPushButton, PropertyPanel QPushButton {
    padding: 0px 6px;
    margin: 0px;
    min-width: 36px;
    min-height: 0px;
    max-height: 24px;
    border: none;
    border-radius: 2px;
    font-size: 10px;
    background-color: #3f51b5;
    color: #ffffff;
}

QDockWidget QPushButton:hover, PropertyPanel QPushButton:hover {
    background-color: #5c6bc0;
}

QDockWidget QPushButton:pressed, PropertyPanel QPushButton:pressed {
    background-color: #3949ab;
}

QDockWidget QComboBox, PropertyPanel QComboBox {
    background-color: transparent;
    color: #212121;
    border: none;
    border-bottom: 1px solid #9e9e9e;
}

QDockWidget QSpinBox, PropertyPanel QSpinBox {
    background-color: transparent;
    color: #212121;
    border: none;
    border-bottom: 1px solid #9e9e9e;
}

/* === Splitter === */
QSplitter::handle {
    background-color: #7986cb;
}

QSplitter::handle:horizontal {
    width: 3px;
}

QSplitter::handle:vertical {
    height: 3px;
}

QSplitter::handle:hover {
    background-color: #5c6bc0;
}

/* === Dock Widget Separator === */
QMainWindow::separator {
    background-color: #7986cb;
    width: 3px;
    height: 3px;
}

QMainWindow::separator:hover {
    background-color: #5c6bc0;
}
"""

TAILWIND_STYLE = """
/* === Tailwind CSS-inspired Theme === */
/* Primary: #6366f1 (Indigo-500), Slate grays, Inter font */
/* Clean, modern utility-driven aesthetic */

QMainWindow {
    background-color: #f8fafc;
}

QWidget {
    background-color: #f8fafc;
    color: #1e293b;
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 13px;
}

/* === Menu Bar === */
QMenuBar {
    background-color: #ffffff;
    color: #475569;
    border-bottom: 1px solid #e2e8f0;
    padding: 2px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 8px 14px;
    border-radius: 6px;
}

QMenuBar::item:selected {
    background-color: #f1f5f9;
    color: #6366f1;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 10px 20px;
    border-radius: 6px;
    margin: 2px;
}

QMenu::item:selected {
    background-color: #f1f5f9;
    color: #6366f1;
}

QMenu::separator {
    height: 1px;
    background-color: #e2e8f0;
    margin: 6px 10px;
}

/* === Toolbar === */
QToolBar {
    background-color: #ffffff;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    padding: 2px 3px;
    spacing: 1px;
}

QToolBar::separator {
    width: 1px;
    background-color: #e2e8f0;
    margin: 3px 7px;
}

QToolBar QToolButton {
    background-color: #f8fafc;
    color: #475569;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 2px 4px;
    margin: 0px;
    min-width: 24px;
}

QToolBar QToolButton:hover {
    background-color: #f1f5f9;
    border-color: #cbd5e1;
    color: #6366f1;
}

QToolBar QToolButton:pressed {
    background-color: #e2e8f0;
}

QToolBar QToolButton:checked {
    background-color: #6366f1;
    border-color: #6366f1;
    color: #ffffff;
    font-weight: 600;
}

QToolBar QToolButton:disabled {
    background-color: #f1f5f9;
    color: #94a3b8;
    border: 1px solid #e2e8f0;
}

QToolBar QLabel {
    color: #94a3b8;
    padding: 0 8px;
    background-color: transparent;
}

/* === Dock Widgets === */
QDockWidget {
    color: #1e293b;
}

QDockWidget::title {
    background-color: #f1f5f9;
    padding: 10px 12px;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 600;
    color: #475569;
}

QDockWidget::close-button,
QDockWidget::float-button {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 4px;
}

QDockWidget::close-button:hover,
QDockWidget::float-button:hover {
    background-color: #e2e8f0;
}

/* === Tab Widget === */
QTabWidget::pane {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: transparent;
    color: #64748b;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 12px 20px;
    margin-right: 4px;
    font-weight: 500;
}

QTabBar::tab:selected {
    color: #6366f1;
    border-bottom: 2px solid #6366f1;
}

QTabBar::tab:hover:!selected {
    color: #475569;
    background-color: #f8fafc;
}

/* === Scroll Area === */
QScrollArea {
    background-color: #ffffff;
    border: none;
}

/* === Scrollbars === */
QScrollBar:vertical {
    background-color: #f1f5f9;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    border-radius: 5px;
    min-height: 30px;
    margin: 1px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #f1f5f9;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #cbd5e1;
    border-radius: 5px;
    min-width: 30px;
    margin: 1px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* === Form Elements === */
QLabel {
    color: #1e293b;
    background-color: transparent;
}

QLineEdit {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 14px;
    selection-background-color: #c7d2fe;
}

QLineEdit:focus {
    border-color: #6366f1;
    border-width: 2px;
}

QLineEdit:disabled {
    background-color: #f1f5f9;
    color: #94a3b8;
}

QSpinBox {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 12px;
}

QSpinBox:focus {
    border-color: #6366f1;
    border-width: 2px;
}

QSpinBox::up-button,
QSpinBox::down-button {
    background-color: #f8fafc;
    border: none;
    border-radius: 4px;
    width: 20px;
    margin: 2px;
}

QSpinBox::up-button:hover,
QSpinBox::down-button:hover {
    background-color: #e2e8f0;
}

QComboBox {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 14px;
    min-width: 80px;
}

QComboBox:hover {
    border-color: #cbd5e1;
}

QComboBox:focus {
    border-color: #6366f1;
    border-width: 2px;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    selection-background-color: #f1f5f9;
    selection-color: #6366f1;
    padding: 4px;
}

/* === Buttons === */
QPushButton {
    background-color: #6366f1;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 600;
    min-width: 70px;
}

QPushButton:hover {
    background-color: #4f46e5;
}

QPushButton:pressed {
    background-color: #4338ca;
}

QPushButton:disabled {
    background-color: #e2e8f0;
    color: #94a3b8;
}

/* Secondary button style for Delete */
QPushButton#delete_btn {
    background-color: #ef4444;
}

QPushButton#delete_btn:hover {
    background-color: #dc2626;
}

QPushButton#delete_btn:pressed {
    background-color: #b91c1c;
}

/* === Text Edit / Code Editor === */
QPlainTextEdit, QTextEdit {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-family: "JetBrains Mono", "Cascadia Code", "Consolas", monospace;
    font-size: 13px;
    selection-background-color: #c7d2fe;
    padding: 8px;
}

QPlainTextEdit:focus, QTextEdit:focus {
    border-color: #6366f1;
    border-width: 2px;
}

/* === Status Bar === */
QStatusBar {
    background-color: #6366f1;
    color: #ffffff;
    border: none;
    padding: 8px;
    font-weight: 500;
}

QStatusBar::item {
    border: none;
}

/* === Graphics View === */
QGraphicsView {
    background-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}

/* === Tooltips === */
QToolTip {
    background-color: #1e293b;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
}

/* === Message Box === */
QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #1e293b;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* === File Dialog === */
QFileDialog {
    background-color: #f8fafc;
}

QFileDialog QLabel {
    color: #1e293b;
}

QFileDialog QLineEdit {
    background-color: #ffffff;
}

QFileDialog QListView,
QFileDialog QTreeView {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}

QFileDialog QListView::item:selected,
QFileDialog QTreeView::item:selected {
    background-color: #f1f5f9;
    color: #6366f1;
}

/* === Color Dialog === */
QColorDialog {
    background-color: #f8fafc;
}

/* === Compact Form Elements (Property Panel) === */
QDockWidget QLineEdit, PropertyPanel QLineEdit {
    padding: 1px 4px;
}

QDockWidget QSpinBox, PropertyPanel QSpinBox {
    padding: 0px 2px;
}

QDockWidget QComboBox, PropertyPanel QComboBox {
    padding: 1px 4px;
}

QDockWidget QPushButton, PropertyPanel QPushButton {
    padding: 0px 6px;
    margin: 0px;
    min-width: 36px;
    min-height: 0px;
    max-height: 24px;
    border: none;
    border-radius: 4px;
    font-size: 10px;
    background-color: #6366f1;
    color: #ffffff;
}

QDockWidget QPushButton:hover, PropertyPanel QPushButton:hover {
    background-color: #4f46e5;
}

QDockWidget QPushButton:pressed, PropertyPanel QPushButton:pressed {
    background-color: #4338ca;
}

QDockWidget QComboBox, PropertyPanel QComboBox {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
}

QDockWidget QSpinBox, PropertyPanel QSpinBox {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
}

/* === Splitter === */
QSplitter::handle {
    background-color: #a5b4fc;
    border-radius: 1px;
}

QSplitter::handle:horizontal {
    width: 3px;
}

QSplitter::handle:vertical {
    height: 3px;
}

QSplitter::handle:hover {
    background-color: #818cf8;
}

/* === Dock Widget Separator === */
QMainWindow::separator {
    background-color: #a5b4fc;
    width: 3px;
    height: 3px;
}

QMainWindow::separator:hover {
    background-color: #818cf8;
}
"""

BOOTSTRAP_STYLE = """
/* === Bootstrap-inspired Theme === */
/* Primary: #0d6efd, Secondary: #6c757d, Success: #198754 */
/* System font stack, familiar Bootstrap aesthetic */

QMainWindow {
    background-color: #ffffff;
}

QWidget {
    background-color: #ffffff;
    color: #212529;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

/* === Menu Bar === */
QMenuBar {
    background-color: #212529;
    color: rgba(255, 255, 255, 0.85);
    border: none;
    padding: 0;
}

QMenuBar::item {
    background-color: transparent;
    padding: 10px 16px;
}

QMenuBar::item:selected {
    background-color: rgba(255, 255, 255, 0.1);
    color: #ffffff;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.15);
    border-radius: 6px;
    padding: 8px 0;
}

QMenu::item {
    padding: 8px 24px;
}

QMenu::item:selected {
    background-color: #e9ecef;
    color: #1e2125;
}

QMenu::separator {
    height: 1px;
    background-color: #dee2e6;
    margin: 8px 0;
}

/* === Toolbar === */
QToolBar {
    background-color: #f8f9fa;
    border: none;
    border-bottom: 1px solid #dee2e6;
    padding: 2px 3px;
    spacing: 1px;
}

QToolBar::separator {
    width: 1px;
    background-color: #dee2e6;
    margin: 3px 7px;
}

QToolBar QToolButton {
    background-color: #ffffff;
    color: #212529;
    border: 1px solid #dee2e6;
    border-radius: 3px;
    padding: 2px 4px;
    margin: 0px;
    min-width: 24px;
}

QToolBar QToolButton:hover {
    background-color: #e9ecef;
    border-color: #dee2e6;
}

QToolBar QToolButton:pressed {
    background-color: #dee2e6;
}

QToolBar QToolButton:checked {
    background-color: #0d6efd;
    border-color: #0d6efd;
    color: #ffffff;
    font-weight: 600;
}

QToolBar QToolButton:disabled {
    background-color: #f8f9fa;
    color: #adb5bd;
    border: 1px solid #dee2e6;
}

QToolBar QLabel {
    color: #6c757d;
    padding: 0 8px;
    background-color: transparent;
}

/* === Dock Widgets === */
QDockWidget {
    color: #212529;
}

QDockWidget::title {
    background-color: #e9ecef;
    padding: 10px 12px;
    border-bottom: 1px solid #dee2e6;
    font-weight: 600;
}

QDockWidget::close-button,
QDockWidget::float-button {
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 4px;
}

QDockWidget::close-button:hover,
QDockWidget::float-button:hover {
    background-color: #dee2e6;
}

/* === Tab Widget === */
QTabWidget::pane {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: transparent;
    color: #0d6efd;
    border: 1px solid transparent;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 18px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #495057;
    border-color: #dee2e6;
    border-bottom: 1px solid #ffffff;
}

QTabBar::tab:hover:!selected {
    border-color: #e9ecef #e9ecef #dee2e6;
    background-color: #e9ecef;
}

/* === Scroll Area === */
QScrollArea {
    background-color: #ffffff;
    border: none;
}

/* === Scrollbars === */
QScrollBar:vertical {
    background-color: #f8f9fa;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #ced4da;
    border-radius: 6px;
    min-height: 30px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #adb5bd;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #f8f9fa;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #ced4da;
    border-radius: 6px;
    min-width: 30px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #adb5bd;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* === Form Elements === */
QLabel {
    color: #212529;
    background-color: transparent;
}

QLineEdit {
    background-color: #ffffff;
    color: #212529;
    border: 1px solid #ced4da;
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: #0d6efd;
    selection-color: #ffffff;
}

QLineEdit:focus {
    border-color: #86b7fe;
    outline: 0;
}

QLineEdit:disabled {
    background-color: #e9ecef;
    color: #6c757d;
}

QSpinBox {
    background-color: #ffffff;
    color: #212529;
    border: 1px solid #ced4da;
    border-radius: 6px;
    padding: 6px 10px;
}

QSpinBox:focus {
    border-color: #86b7fe;
}

QSpinBox::up-button,
QSpinBox::down-button {
    background-color: #e9ecef;
    border: none;
    width: 20px;
}

QSpinBox::up-button:hover,
QSpinBox::down-button:hover {
    background-color: #dee2e6;
}

QComboBox {
    background-color: #ffffff;
    color: #212529;
    border: 1px solid #ced4da;
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 80px;
}

QComboBox:hover {
    border-color: #86b7fe;
}

QComboBox:focus {
    border-color: #86b7fe;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #212529;
    border: 1px solid rgba(0, 0, 0, 0.15);
    border-radius: 6px;
    selection-background-color: #0d6efd;
    selection-color: #ffffff;
}

/* === Buttons === */
QPushButton {
    background-color: #0d6efd;
    color: #ffffff;
    border: 1px solid #0d6efd;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-width: 70px;
}

QPushButton:hover {
    background-color: #0b5ed7;
    border-color: #0a58ca;
}

QPushButton:pressed {
    background-color: #0a58ca;
    border-color: #0a53be;
}

QPushButton:disabled {
    background-color: #6c757d;
    border-color: #6c757d;
    color: #ffffff;
    opacity: 0.65;
}

/* Secondary button style for Delete */
QPushButton#delete_btn {
    background-color: #dc3545;
    border-color: #dc3545;
}

QPushButton#delete_btn:hover {
    background-color: #bb2d3b;
    border-color: #b02a37;
}

QPushButton#delete_btn:pressed {
    background-color: #b02a37;
    border-color: #a52834;
}

/* === Text Edit / Code Editor === */
QPlainTextEdit, QTextEdit {
    background-color: #ffffff;
    color: #212529;
    border: 1px solid #ced4da;
    border-radius: 6px;
    font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-size: 13px;
    selection-background-color: #0d6efd;
    selection-color: #ffffff;
    padding: 8px;
}

QPlainTextEdit:focus, QTextEdit:focus {
    border-color: #86b7fe;
}

/* === Status Bar === */
QStatusBar {
    background-color: #212529;
    color: rgba(255, 255, 255, 0.85);
    border: none;
    padding: 8px;
}

QStatusBar::item {
    border: none;
}

/* === Graphics View === */
QGraphicsView {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
}

/* === Tooltips === */
QToolTip {
    background-color: #212529;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
}

/* === Message Box === */
QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #212529;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* === File Dialog === */
QFileDialog {
    background-color: #ffffff;
}

QFileDialog QLabel {
    color: #212529;
}

QFileDialog QLineEdit {
    background-color: #ffffff;
}

QFileDialog QListView,
QFileDialog QTreeView {
    background-color: #ffffff;
    color: #212529;
    border: 1px solid #dee2e6;
    border-radius: 6px;
}

QFileDialog QListView::item:selected,
QFileDialog QTreeView::item:selected {
    background-color: #0d6efd;
    color: #ffffff;
}

/* === Color Dialog === */
QColorDialog {
    background-color: #ffffff;
}

/* === Compact Form Elements (Property Panel) === */
QDockWidget QLineEdit, PropertyPanel QLineEdit {
    padding: 1px 4px;
}

QDockWidget QSpinBox, PropertyPanel QSpinBox {
    padding: 0px 2px;
}

QDockWidget QComboBox, PropertyPanel QComboBox {
    padding: 1px 4px;
}

QDockWidget QPushButton, PropertyPanel QPushButton {
    padding: 0px 6px;
    margin: 0px;
    min-width: 36px;
    min-height: 0px;
    max-height: 24px;
    border: none;
    border-radius: 4px;
    font-size: 10px;
    background-color: #0d6efd;
    color: #ffffff;
}

QDockWidget QPushButton:hover, PropertyPanel QPushButton:hover {
    background-color: #0b5ed7;
}

QDockWidget QPushButton:pressed, PropertyPanel QPushButton:pressed {
    background-color: #0a58ca;
}

QDockWidget QComboBox, PropertyPanel QComboBox {
    background-color: #ffffff;
    color: #212529;
    border: 1px solid #ced4da;
}

QDockWidget QSpinBox, PropertyPanel QSpinBox {
    background-color: #ffffff;
    color: #212529;
    border: 1px solid #ced4da;
}

/* === Splitter === */
QSplitter::handle {
    background-color: #6ea8fe;
    border-radius: 1px;
}

QSplitter::handle:horizontal {
    width: 3px;
}

QSplitter::handle:vertical {
    height: 3px;
}

QSplitter::handle:hover {
    background-color: #3d8bfd;
}

/* === Dock Widget Separator === */
QMainWindow::separator {
    background-color: #6ea8fe;
    width: 3px;
    height: 3px;
}

QMainWindow::separator:hover {
    background-color: #3d8bfd;
}
"""

# Style registry for easy access
STYLES = {
    "Foundation (Dark)": FOUNDATION_STYLE,
    "Bulma (Light)": BULMA_STYLE,
    "Bauhaus": BAUHAUS_STYLE,
    "Neumorphism": NEUMORPHISM_STYLE,
    "Materialize": MATERIALIZE_STYLE,
    "Tailwind": TAILWIND_STYLE,
    "Bootstrap": BOOTSTRAP_STYLE,
}

DEFAULT_STYLE = "Tailwind"

# Default text color for canvas text items (contrasts with canvas background)
# Dark themes need light text, light themes need dark text
CANVAS_TEXT_COLORS = {
    "Foundation (Dark)": "#FFFFFF",  # White on dark background (#1e1e1e)
    "Bulma (Light)": "#1A1A1A",      # Dark on light background (#f5f5f5)
    "Bauhaus": "#000000",            # Black on light background (#f5f5f5)
    "Neumorphism": "#2D3748",        # Dark gray on light background (#d9e0ea)
    "Materialize": "#212121",        # Dark on light background (#eeeeee)
    "Tailwind": "#1E293B",           # Slate-800 on light background (#f1f5f9)
    "Bootstrap": "#212529",          # Dark on light background (#f8f9fa)
}

# Line number area colors for the code editor
# background: slightly different from main editor background
# text: high contrast for readability
# highlight: accent color for selection/highlight bar
LINE_NUMBER_COLORS = {
    "Foundation (Dark)": {
        "background": "#1a1a1a",      # Slightly darker than editor (#1e1e1e)
        "text": "#606060",            # Dimmed text
        "text_active": "#ffffff",     # Active line text
        "highlight_bg": "#2A3A4A",    # Highlighted line background
        "highlight_bar": "#0078D4",   # Selection bar color
        "current_line_bg": "#2d2d2d", # Current line background
    },
    "Bulma (Light)": {
        "background": "#f0f0f0",      # Slightly darker than editor (#ffffff)
        "text": "#a0a0a0",            # Dimmed text
        "text_active": "#363636",     # Active line text
        "highlight_bg": "#e0f0e8",    # Highlighted line background
        "highlight_bar": "#00d1b2",   # Selection bar color
        "current_line_bg": "#e8e8e8", # Current line background
    },
    "Bauhaus": {
        "background": "#f0f0f0",      # Slightly darker than editor (#ffffff)
        "text": "#888888",            # Dimmed text
        "text_active": "#000000",     # Active line text
        "highlight_bg": "#fff3cd",    # Highlighted line background (yellow tint)
        "highlight_bar": "#e53935",   # Selection bar color (red)
        "current_line_bg": "#e0e0e0", # Current line background
    },
    "Neumorphism": {
        "background": "#cdd4df",      # Slightly darker than editor (#d9e0ea)
        "text": "#8a9bb0",            # Dimmed text
        "text_active": "#4a5568",     # Active line text
        "highlight_bg": "#c5cce0",    # Highlighted line background
        "highlight_bar": "#6c5ce7",   # Selection bar color (purple)
        "current_line_bg": "#d1d8e4", # Current line background
    },
    "Materialize": {
        "background": "#f5f5f5",      # Slightly darker than editor (#ffffff)
        "text": "#9e9e9e",            # Dimmed text
        "text_active": "#212121",     # Active line text
        "highlight_bg": "#e8eaf6",    # Highlighted line background (indigo tint)
        "highlight_bar": "#3f51b5",   # Selection bar color (indigo)
        "current_line_bg": "#eeeeee", # Current line background
    },
    "Tailwind": {
        "background": "#f1f5f9",      # Slightly darker than editor (#ffffff)
        "text": "#94a3b8",            # Dimmed text (slate-400)
        "text_active": "#1e293b",     # Active line text (slate-800)
        "highlight_bg": "#e0e7ff",    # Highlighted line background (indigo-100)
        "highlight_bar": "#6366f1",   # Selection bar color (indigo-500)
        "current_line_bg": "#e2e8f0", # Current line background (slate-200)
    },
    "Bootstrap": {
        "background": "#f8f9fa",      # Slightly different from editor (#ffffff)
        "text": "#adb5bd",            # Dimmed text
        "text_active": "#212529",     # Active line text
        "highlight_bg": "#cfe2ff",    # Highlighted line background (blue tint)
        "highlight_bar": "#0d6efd",   # Selection bar color (primary blue)
        "current_line_bg": "#e9ecef", # Current line background
    },
}
