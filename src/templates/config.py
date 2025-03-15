"""
Template configuration module for D&D Knowledge Navigator.

This module contains configuration settings for the template system,
allowing easy enabling/disabling of formatted templates.
"""

# Master switch to enable/disable all templates
TEMPLATES_ENABLED = True

# Individual template settings
# These are only used if TEMPLATES_ENABLED is True
TEMPLATE_SETTINGS = {
    "monster": {
        "enabled": True,
        "include_image_placeholder": False,  # For future enhancement
    },
    "spell": {
        "enabled": True,
        "show_components_detail": True,
    },
    "equipment": {
        "enabled": True,
        "show_cost_details": True,
    },
    "class": {
        "enabled": True,
    },
    # Add more template types as needed
}

# Formatting options
FORMATTING_OPTIONS = {
    "use_tables": True,       # Use markdown tables for structured data
    "use_emojis": False,      # Add emojis to headings (e.g. ⚔️ for attacks)
    "compact_mode": False,    # Use more compact formatting
}


def is_template_enabled(template_type):
    """
    Check if a specific template type is enabled.

    Args:
        template_type: The type of template to check

    Returns:
        Boolean indicating if the template is enabled
    """
    if not TEMPLATES_ENABLED:
        return False

    if template_type not in TEMPLATE_SETTINGS:
        return False

    return TEMPLATE_SETTINGS[template_type]["enabled"]


def get_template_setting(template_type, setting_name, default=None):
    """
    Get a specific setting for a template type.

    Args:
        template_type: The type of template
        setting_name: The name of the setting
        default: Default value if setting doesn't exist

    Returns:
        The setting value or default
    """
    if template_type not in TEMPLATE_SETTINGS:
        return default

    return TEMPLATE_SETTINGS[template_type].get(setting_name, default)


def get_formatting_option(option_name, default=None):
    """
    Get a formatting option.

    Args:
        option_name: The name of the formatting option
        default: Default value if option doesn't exist

    Returns:
        The option value or default
    """
    return FORMATTING_OPTIONS.get(option_name, default)
