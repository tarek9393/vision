"""Stilguide för Label Vision System"""

# Färgschema
COLORS = {
    'primary': '#1976D2',      # Material Blue 700
    'secondary': '#2196F3',    # Material Blue 500
    'accent': '#42A5F5',       # Material Blue 400
    'success': '#4CAF50',      # Material Green
    'warning': '#FFC107',      # Material Amber
    'error': '#F44336',        # Material Red
    'background': '#F5F5F5',   # Material Grey 100
    'surface': '#FFFFFF',      # White
    'text': '#212121',         # Material Grey 900
    'text_light': '#757575',   # Material Grey 600
    'border': '#E0E0E0'        # Material Grey 300
}

# Typografi
FONTS = {
    'title': 'font-family: Segoe UI, Arial; font-size: 24px; font-weight: 600;',
    'subtitle': 'font-family: Segoe UI, Arial; font-size: 18px; font-weight: 500;',
    'body': 'font-family: Segoe UI, Arial; font-size: 14px;',
    'button': 'font-family: Segoe UI, Arial; font-size: 14px; font-weight: 500;',
    'small': 'font-family: Segoe UI, Arial; font-size: 12px;'
}

# Komponentstilar
STYLES = {
    'main_window': f"""
        QMainWindow {{
            background-color: {COLORS['background']};
        }}
        QFrame {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
        }}
    """,
    
    'group_box': f"""
        QGroupBox {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            margin-top: 1em;
            padding: 15px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: {COLORS['primary']};
            {FONTS['subtitle']}
            background-color: {COLORS['surface']};
        }}
    """,
    
    'button': f"""
        QPushButton {{
            background-color: {COLORS['surface']};
            color: {COLORS['primary']};
            border: 1px solid {COLORS['primary']};
            border-radius: 4px;
            padding: 8px 16px;
            {FONTS['button']}
        }}
        QPushButton:hover {{
            background-color: {COLORS['background']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['border']};
        }}
        QPushButton:disabled {{
            color: {COLORS['text_light']};
            border-color: {COLORS['border']};
        }}
    """,
    
    'action_button': f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: {COLORS['surface']};
            border: none;
            border-radius: 4px;
            padding: 10px 20px;
            {FONTS['button']}
        }}
        QPushButton:hover {{
            background-color: {COLORS['secondary']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['accent']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['text_light']};
        }}
    """,
    
    'list_widget': f"""
        QListWidget {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 4px;
            padding: 5px;
            {FONTS['body']}
        }}
        QListWidget::item {{
            padding: 8px;
            border-radius: 4px;
            margin: 2px;
        }}
        QListWidget::item:selected {{
            background-color: {COLORS['primary']};
            color: {COLORS['surface']};
        }}
        QListWidget::item:hover:!selected {{
            background-color: {COLORS['background']};
        }}
    """,
    
    'combo_box': f"""
        QComboBox {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 4px;
            padding: 8px;
            padding-right: 24px;
            {FONTS['body']}
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox::down-arrow {{
            image: url(resources/down_arrow.png);
            width: 12px;
            height: 12px;
        }}
        QComboBox:hover {{
            border-color: {COLORS['primary']};
        }}
        QComboBox:focus {{
            border-color: {COLORS['primary']};
        }}
        QComboBox QAbstractItemView {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 4px;
            selection-background-color: {COLORS['primary']};
            selection-color: {COLORS['surface']};
        }}
    """,
    
    'line_edit': f"""
        QLineEdit {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 4px;
            padding: 8px;
            {FONTS['body']}
        }}
        QLineEdit:focus {{
            border-color: {COLORS['primary']};
        }}
        QLineEdit:hover {{
            border-color: {COLORS['primary']};
        }}
    """,
    
    'label': f"""
        QLabel {{
            color: {COLORS['text']};
            {FONTS['body']}
        }}
    """,
    
    'title_label': f"""
        QLabel {{
            color: {COLORS['primary']};
            {FONTS['title']}
        }}
    """,
    
    'camera_view': f"""
        QLabel {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 2px;
        }}
    """,
    
    'status_ok': f"""
        QLabel {{
            color: {COLORS['success']};
            background-color: rgba(76, 175, 80, 0.1);
            border: 1px solid {COLORS['success']};
            border-radius: 4px;
            padding: 8px;
            {FONTS['body']}
        }}
    """,
    
    'status_warning': f"""
        QLabel {{
            color: {COLORS['warning']};
            background-color: rgba(255, 193, 7, 0.1);
            border: 1px solid {COLORS['warning']};
            border-radius: 4px;
            padding: 8px;
            {FONTS['body']}
        }}
    """,
    
    'status_error': f"""
        QLabel {{
            color: {COLORS['error']};
            background-color: rgba(244, 67, 54, 0.1);
            border: 1px solid {COLORS['error']};
            border-radius: 4px;
            padding: 8px;
            {FONTS['body']}
        }}
    """
}

def apply_style(widget, style_name):
    """Applicera en stil på en widget"""
    if style_name in STYLES:
        widget.setStyleSheet(STYLES[style_name])
