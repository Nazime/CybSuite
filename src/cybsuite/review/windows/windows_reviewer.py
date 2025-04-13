import json
import os
from typing import Any, Iterable

from cybsuite.review.files_reviewers import BaseReviewer, BaseTypeReviewer
from koalak.plugin_manager import Metadata


class WindowsTypeReviewer(BaseTypeReviewer):
    name = "windows"

    def __init__(self):
        self.windows_registries: WindowsRegistries = None

    def prepare_for_host(self):
        # Garbage collector will remove it
        self.windows_registries = None

    def cleanup_for_host(self):
        # Garbage collector will remove it
        self.windows_registries = None


class WindowsRegistries:
    """Class for handling Windows registry operations."""

    def __init__(self):
        """Initialize the Registry handler."""
        self._registries: dict[str, Any] = {}

    def unload(self):
        """Unload the registry data."""
        self._registries = {}

    def load_from_oneline_json(self, file_path: str) -> None:
        """
        Load registry data from a JSONL file.

        Args:
            file_path: Path to the JSONL file
        """
        with open(file_path, encoding="utf-8-sig") as f:
            self.load_from_list(json.loads(l) for l in f)

    def load_from_list(self, entries: Iterable[dict[str, Any]]) -> None:
        """
        Load registry data from a list of entries.

        Args:
            entries: Iterable of registry entries, each with 'path' and 'properties' keys
        """
        for entry in entries:
            properties = entry["properties"]
            for key, value in properties.items():
                if isinstance(value, list):
                    try:
                        properties[key] = bytes(value)
                    except Exception as e:
                        pass
            self._registries[entry["path"].lower()] = properties

    def get_key(self, key: str) -> dict[str, Any]:
        """
        Get registry key data by path (case insensitive).

        Args:
            key: The registry key path to retrieve

        Returns:
            Dictionary containing the registry key data or None if not found
        """
        # Normalize key

        key_lower = key.lower().replace("/", "\\")
        map_replace = {
            "hklm\\": "hkey_local_machine\\",
            "hkcu\\": "hkey_current_user\\",
            "hkcr\\": "hkey_classes_root\\",
            "hkcc\\": "hkey_current_config\\",
            "hku\\": "hkey_users\\",
        }
        for prefix, replacement in map_replace.items():
            if key_lower.startswith(prefix):
                key_lower = key_lower.replace(prefix, replacement, 1)
                break

        return self._registries[key_lower]


class WindowsReviewer(BaseReviewer):
    abstract = True
    metadata = Metadata(category="windows")
    type_reviewer: WindowsTypeReviewer

    # WINDOWS REGISTRY API #
    # -------------------- #
    def get_windows_registry(self, key: str) -> dict[str, Any]:
        """
        Get registry key data by path (case insensitive).

        Args:
            key: The registry key path to retrieve

        Returns:
            Dictionary containing the registry key data or None if not found
        """
        self._ensure_windows_registries_loaded()

        return self.type_reviewer.windows_registries.get_key(key)

    def get_windows_registries(self) -> dict[str, Any]:
        """
        Get all registry key data.

        Returns:
            Dictionary containing all registry keys
        """
        self._ensure_windows_registries_loaded()
        return self.type_reviewer.windows_registries._registries

    def _ensure_windows_registries_loaded(self) -> None:
        """
        Load all registry hives from files.
        """
        if self.type_reviewer.windows_registries is None:
            self.type_reviewer.windows_registries = WindowsRegistries()
            self.info(f"loading registry hives for '{self.context.hostname}'")
            for hive in ["hkcc", "hkcr", "hkcu", "hklm", "hku"]:
                file_path = os.path.join(
                    self.context.host_extracts_path,
                    "commands",
                    f"reg_{hive.upper()}.json",
                )
                self.type_reviewer.windows_registries.load_from_oneline_json(file_path)
