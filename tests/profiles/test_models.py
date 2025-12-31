# ClamUI Profile Models Tests
"""Unit tests for the ScanProfile dataclass."""

import pytest

from src.profiles.models import ScanProfile


class TestScanProfileCreation:
    """Tests for ScanProfile creation."""

    def test_create_with_required_fields(self):
        """Test creating ScanProfile with all required fields."""
        profile = ScanProfile(
            id="test-uuid-123",
            name="Test Profile",
            targets=["/home/user/documents"],
            exclusions={"paths": ["/tmp"], "patterns": ["*.log"]},
            created_at="2024-01-15T10:30:00",
            updated_at="2024-01-15T10:30:00",
        )

        assert profile.id == "test-uuid-123"
        assert profile.name == "Test Profile"
        assert profile.targets == ["/home/user/documents"]
        assert profile.exclusions == {"paths": ["/tmp"], "patterns": ["*.log"]}
        assert profile.created_at == "2024-01-15T10:30:00"
        assert profile.updated_at == "2024-01-15T10:30:00"
        # Optional fields should have defaults
        assert profile.is_default is False
        assert profile.description == ""
        assert profile.options == {}

    def test_create_with_all_fields(self):
        """Test creating ScanProfile with all fields including optional."""
        profile = ScanProfile(
            id="test-uuid-456",
            name="Full Profile",
            targets=["/home", "/var/www"],
            exclusions={"paths": ["/home/user/.cache"]},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-16T14:30:00",
            is_default=True,
            description="A comprehensive scan profile",
            options={"recursive": True, "max_depth": 10},
        )

        assert profile.id == "test-uuid-456"
        assert profile.name == "Full Profile"
        assert profile.targets == ["/home", "/var/www"]
        assert profile.exclusions == {"paths": ["/home/user/.cache"]}
        assert profile.created_at == "2024-01-15T10:00:00"
        assert profile.updated_at == "2024-01-16T14:30:00"
        assert profile.is_default is True
        assert profile.description == "A comprehensive scan profile"
        assert profile.options == {"recursive": True, "max_depth": 10}

    def test_create_with_empty_targets(self):
        """Test creating ScanProfile with empty targets list."""
        profile = ScanProfile(
            id="test-uuid",
            name="Empty Targets",
            targets=[],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        assert profile.targets == []

    def test_create_with_empty_exclusions(self):
        """Test creating ScanProfile with empty exclusions dict."""
        profile = ScanProfile(
            id="test-uuid",
            name="No Exclusions",
            targets=["/home"],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        assert profile.exclusions == {}

    def test_create_with_complex_options(self):
        """Test creating ScanProfile with complex options dictionary."""
        complex_options = {
            "recursive": True,
            "max_depth": 5,
            "file_types": ["exe", "dll", "doc"],
            "scan_archives": True,
            "scan_ole2": True,
            "nested": {"level1": {"level2": "value"}},
        }

        profile = ScanProfile(
            id="test-uuid",
            name="Complex Options",
            targets=["/home"],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
            options=complex_options,
        )

        assert profile.options == complex_options
        assert profile.options["nested"]["level1"]["level2"] == "value"

    def test_create_with_special_characters_in_name(self):
        """Test creating ScanProfile with special characters in name."""
        profile = ScanProfile(
            id="test-uuid",
            name="Profile (Test) - v2.0 [Final]",
            targets=["/home"],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        assert profile.name == "Profile (Test) - v2.0 [Final]"

    def test_create_with_unicode_in_fields(self):
        """Test creating ScanProfile with unicode characters."""
        profile = ScanProfile(
            id="test-uuid",
            name="Perfil de análisis",
            targets=["/home/usuario/documentos"],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
            description="Профиль сканирования для файлов",
        )

        assert profile.name == "Perfil de análisis"
        assert profile.description == "Профиль сканирования для файлов"


class TestScanProfileToDict:
    """Tests for ScanProfile.to_dict serialization."""

    def test_to_dict_all_fields(self):
        """Test to_dict includes all fields."""
        profile = ScanProfile(
            id="test-uuid-123",
            name="Test Profile",
            targets=["/home/user"],
            exclusions={"paths": ["/tmp"]},
            created_at="2024-01-15T10:30:00",
            updated_at="2024-01-16T14:00:00",
            is_default=True,
            description="Test description",
            options={"recursive": True},
        )
        data = profile.to_dict()

        assert data["id"] == "test-uuid-123"
        assert data["name"] == "Test Profile"
        assert data["targets"] == ["/home/user"]
        assert data["exclusions"] == {"paths": ["/tmp"]}
        assert data["created_at"] == "2024-01-15T10:30:00"
        assert data["updated_at"] == "2024-01-16T14:00:00"
        assert data["is_default"] is True
        assert data["description"] == "Test description"
        assert data["options"] == {"recursive": True}

    def test_to_dict_with_defaults(self):
        """Test to_dict with default optional fields."""
        profile = ScanProfile(
            id="test-uuid",
            name="Default Fields",
            targets=[],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )
        data = profile.to_dict()

        assert data["is_default"] is False
        assert data["description"] == ""
        assert data["options"] == {}

    def test_to_dict_returns_dict_type(self):
        """Test that to_dict returns a dictionary."""
        profile = ScanProfile(
            id="test-uuid",
            name="Test",
            targets=[],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )
        data = profile.to_dict()

        assert isinstance(data, dict)

    def test_to_dict_contains_all_expected_keys(self):
        """Test that to_dict contains all expected keys."""
        profile = ScanProfile(
            id="test-uuid",
            name="Test",
            targets=[],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )
        data = profile.to_dict()

        expected_keys = {
            "id",
            "name",
            "targets",
            "exclusions",
            "created_at",
            "updated_at",
            "is_default",
            "description",
            "options",
        }
        assert set(data.keys()) == expected_keys

    def test_to_dict_returns_copy_of_mutable_fields(self):
        """Test that to_dict returns data that can be modified independently."""
        profile = ScanProfile(
            id="test-uuid",
            name="Test",
            targets=["/home"],
            exclusions={"paths": ["/tmp"]},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
            options={"recursive": True},
        )
        data = profile.to_dict()

        # Modify the returned data
        data["targets"].append("/var")
        data["exclusions"]["paths"].append("/cache")
        data["options"]["new_key"] = "value"

        # Original profile should be unchanged
        assert profile.targets == ["/home"]
        assert profile.exclusions == {"paths": ["/tmp"]}
        assert profile.options == {"recursive": True}


class TestScanProfileFromDict:
    """Tests for ScanProfile.from_dict deserialization."""

    def test_from_dict_all_fields(self):
        """Test from_dict with all fields present."""
        data = {
            "id": "test-uuid-123",
            "name": "Test Profile",
            "targets": ["/home/user"],
            "exclusions": {"paths": ["/tmp"]},
            "created_at": "2024-01-15T10:30:00",
            "updated_at": "2024-01-16T14:00:00",
            "is_default": True,
            "description": "Test description",
            "options": {"recursive": True},
        }
        profile = ScanProfile.from_dict(data)

        assert profile.id == "test-uuid-123"
        assert profile.name == "Test Profile"
        assert profile.targets == ["/home/user"]
        assert profile.exclusions == {"paths": ["/tmp"]}
        assert profile.created_at == "2024-01-15T10:30:00"
        assert profile.updated_at == "2024-01-16T14:00:00"
        assert profile.is_default is True
        assert profile.description == "Test description"
        assert profile.options == {"recursive": True}

    def test_from_dict_with_optional_fields_missing(self):
        """Test from_dict uses defaults for missing optional fields."""
        data = {
            "id": "test-uuid",
            "name": "Minimal",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00",
        }
        profile = ScanProfile.from_dict(data)

        assert profile.id == "test-uuid"
        assert profile.name == "Minimal"
        assert profile.targets == []
        assert profile.exclusions == {}
        assert profile.is_default is False
        assert profile.description == ""
        assert profile.options == {}

    def test_from_dict_missing_id_raises_error(self):
        """Test from_dict raises KeyError when id is missing."""
        data = {
            "name": "No ID",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00",
        }
        with pytest.raises(KeyError):
            ScanProfile.from_dict(data)

    def test_from_dict_missing_name_raises_error(self):
        """Test from_dict raises KeyError when name is missing."""
        data = {
            "id": "test-uuid",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00",
        }
        with pytest.raises(KeyError):
            ScanProfile.from_dict(data)

    def test_from_dict_missing_created_at_raises_error(self):
        """Test from_dict raises KeyError when created_at is missing."""
        data = {
            "id": "test-uuid",
            "name": "Test",
            "updated_at": "2024-01-15T10:00:00",
        }
        with pytest.raises(KeyError):
            ScanProfile.from_dict(data)

    def test_from_dict_missing_updated_at_raises_error(self):
        """Test from_dict raises KeyError when updated_at is missing."""
        data = {
            "id": "test-uuid",
            "name": "Test",
            "created_at": "2024-01-15T10:00:00",
        }
        with pytest.raises(KeyError):
            ScanProfile.from_dict(data)

    def test_from_dict_returns_scanprofile_type(self):
        """Test that from_dict returns a ScanProfile instance."""
        data = {
            "id": "test-uuid",
            "name": "Test",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00",
        }
        profile = ScanProfile.from_dict(data)

        assert isinstance(profile, ScanProfile)


class TestScanProfileRoundtrip:
    """Tests for roundtrip serialization (to_dict -> from_dict)."""

    def test_roundtrip_with_all_fields(self):
        """Test that to_dict and from_dict are reversible with all fields."""
        original = ScanProfile(
            id="test-uuid-789",
            name="Roundtrip Test",
            targets=["/home/user", "/var/www", "/opt"],
            exclusions={
                "paths": ["/tmp", "/var/log"],
                "patterns": ["*.pyc", "__pycache__"],
            },
            created_at="2024-01-15T10:30:00",
            updated_at="2024-01-16T14:00:00",
            is_default=True,
            description="Full roundtrip test profile",
            options={
                "recursive": True,
                "max_depth": 10,
                "scan_archives": True,
            },
        )
        data = original.to_dict()
        restored = ScanProfile.from_dict(data)

        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.targets == original.targets
        assert restored.exclusions == original.exclusions
        assert restored.created_at == original.created_at
        assert restored.updated_at == original.updated_at
        assert restored.is_default == original.is_default
        assert restored.description == original.description
        assert restored.options == original.options

    def test_roundtrip_with_defaults(self):
        """Test roundtrip with only required fields."""
        original = ScanProfile(
            id="test-uuid",
            name="Minimal",
            targets=[],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )
        data = original.to_dict()
        restored = ScanProfile.from_dict(data)

        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.targets == original.targets
        assert restored.exclusions == original.exclusions
        assert restored.created_at == original.created_at
        assert restored.updated_at == original.updated_at
        assert restored.is_default == original.is_default
        assert restored.description == original.description
        assert restored.options == original.options

    def test_roundtrip_preserves_empty_collections(self):
        """Test that roundtrip preserves empty collections correctly."""
        original = ScanProfile(
            id="test-uuid",
            name="Empty Collections",
            targets=[],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
            options={},
        )
        data = original.to_dict()
        restored = ScanProfile.from_dict(data)

        assert restored.targets == []
        assert restored.exclusions == {}
        assert restored.options == {}

    def test_roundtrip_preserves_nested_data(self):
        """Test that roundtrip preserves deeply nested structures."""
        original = ScanProfile(
            id="test-uuid",
            name="Nested Data",
            targets=["/home"],
            exclusions={
                "paths": ["/home/.cache"],
                "patterns": ["*.tmp"],
                "advanced": {
                    "deep": {
                        "nested": {
                            "value": [1, 2, 3],
                        }
                    }
                },
            },
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
            options={"nested": {"data": {"here": True}}},
        )
        data = original.to_dict()
        restored = ScanProfile.from_dict(data)

        assert restored.exclusions == original.exclusions
        assert restored.options == original.options


class TestScanProfileEquality:
    """Tests for ScanProfile equality and comparison."""

    def test_profiles_with_same_data_are_equal(self):
        """Test that two profiles with identical data are equal."""
        profile1 = ScanProfile(
            id="test-uuid",
            name="Test",
            targets=["/home"],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )
        profile2 = ScanProfile(
            id="test-uuid",
            name="Test",
            targets=["/home"],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        assert profile1 == profile2

    def test_profiles_with_different_ids_not_equal(self):
        """Test that profiles with different IDs are not equal."""
        profile1 = ScanProfile(
            id="uuid-1",
            name="Test",
            targets=["/home"],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )
        profile2 = ScanProfile(
            id="uuid-2",
            name="Test",
            targets=["/home"],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        assert profile1 != profile2

    def test_profiles_with_different_names_not_equal(self):
        """Test that profiles with different names are not equal."""
        profile1 = ScanProfile(
            id="test-uuid",
            name="Profile A",
            targets=[],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )
        profile2 = ScanProfile(
            id="test-uuid",
            name="Profile B",
            targets=[],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        assert profile1 != profile2


class TestScanProfileEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_very_long_name(self):
        """Test ScanProfile with a very long name."""
        long_name = "A" * 1000
        profile = ScanProfile(
            id="test-uuid",
            name=long_name,
            targets=[],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        assert len(profile.name) == 1000
        assert profile.name == long_name

    def test_very_long_description(self):
        """Test ScanProfile with a very long description."""
        long_description = "Description " * 1000
        profile = ScanProfile(
            id="test-uuid",
            name="Long Desc",
            targets=[],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
            description=long_description,
        )

        assert profile.description == long_description

    def test_many_targets(self):
        """Test ScanProfile with many targets."""
        targets = [f"/path/to/dir{i}" for i in range(100)]
        profile = ScanProfile(
            id="test-uuid",
            name="Many Targets",
            targets=targets,
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        assert len(profile.targets) == 100

    def test_complex_exclusions(self):
        """Test ScanProfile with complex exclusions structure."""
        exclusions = {
            "paths": [f"/exclude/{i}" for i in range(50)],
            "patterns": ["*.pyc", "*.pyo", "__pycache__", "*.egg-info"],
            "size_limits": {"min": 0, "max": 100 * 1024 * 1024},
            "metadata": {"created_by": "test", "version": 1},
        }
        profile = ScanProfile(
            id="test-uuid",
            name="Complex Exclusions",
            targets=["/home"],
            exclusions=exclusions,
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        assert len(profile.exclusions["paths"]) == 50
        assert profile.exclusions["size_limits"]["max"] == 100 * 1024 * 1024

    def test_paths_with_spaces(self):
        """Test ScanProfile with paths containing spaces."""
        profile = ScanProfile(
            id="test-uuid",
            name="Spaces in Paths",
            targets=["/home/user/My Documents", "/var/data/Some Folder"],
            exclusions={"paths": ["/tmp/temp files/cache"]},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        assert "/home/user/My Documents" in profile.targets
        assert "/tmp/temp files/cache" in profile.exclusions["paths"]

    def test_empty_string_name_allowed(self):
        """Test ScanProfile allows empty string name (validation is elsewhere)."""
        profile = ScanProfile(
            id="test-uuid",
            name="",
            targets=[],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        assert profile.name == ""

    def test_whitespace_only_id(self):
        """Test ScanProfile with whitespace-only ID (model allows it)."""
        profile = ScanProfile(
            id="   ",
            name="Test",
            targets=[],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        assert profile.id == "   "

    def test_none_values_in_optional_string_field(self):
        """Test ScanProfile with None description if explicitly passed."""
        # Note: This tests what happens if None is passed to description
        # The dataclass allows this but typing suggests str
        # This should still work at runtime
        profile = ScanProfile(
            id="test-uuid",
            name="Test",
            targets=[],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
            description=None,  # type: ignore
        )

        assert profile.description is None

    def test_timestamp_format_not_validated(self):
        """Test that timestamp format is not validated by the model."""
        # The model doesn't validate timestamp format
        profile = ScanProfile(
            id="test-uuid",
            name="Test",
            targets=[],
            exclusions={},
            created_at="not-a-timestamp",
            updated_at="also-not-valid",
        )

        assert profile.created_at == "not-a-timestamp"
        assert profile.updated_at == "also-not-valid"


class TestScanProfileImmutability:
    """Tests for ScanProfile mutability characteristics."""

    def test_mutable_fields_can_be_modified(self):
        """Test that mutable fields (lists, dicts) can be modified after creation."""
        profile = ScanProfile(
            id="test-uuid",
            name="Test",
            targets=["/home"],
            exclusions={"paths": ["/tmp"]},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
            options={"recursive": True},
        )

        # Modify mutable fields
        profile.targets.append("/var")
        profile.exclusions["patterns"] = ["*.log"]
        profile.options["max_depth"] = 5

        assert "/var" in profile.targets
        assert "patterns" in profile.exclusions
        assert profile.options["max_depth"] == 5

    def test_dataclass_field_assignment(self):
        """Test that dataclass fields can be directly assigned."""
        profile = ScanProfile(
            id="test-uuid",
            name="Original",
            targets=[],
            exclusions={},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
        )

        profile.name = "Modified"
        profile.is_default = True
        profile.description = "New description"

        assert profile.name == "Modified"
        assert profile.is_default is True
        assert profile.description == "New description"


class TestScanProfileJsonSerializable:
    """Tests to ensure ScanProfile data is JSON-serializable."""

    def test_to_dict_is_json_serializable(self):
        """Test that to_dict output can be serialized to JSON."""
        import json

        profile = ScanProfile(
            id="test-uuid",
            name="JSON Test",
            targets=["/home", "/var"],
            exclusions={"paths": ["/tmp"], "patterns": ["*.log"]},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
            is_default=False,
            description="Test profile",
            options={"recursive": True, "depth": 10},
        )
        data = profile.to_dict()

        # This should not raise
        json_str = json.dumps(data)
        assert isinstance(json_str, str)

    def test_json_roundtrip(self):
        """Test complete JSON serialization and deserialization."""
        import json

        original = ScanProfile(
            id="test-uuid-json",
            name="JSON Roundtrip",
            targets=["/home"],
            exclusions={"patterns": ["*.tmp"]},
            created_at="2024-01-15T10:00:00",
            updated_at="2024-01-15T10:00:00",
            options={"scan_archives": True},
        )

        # Serialize to JSON
        json_str = json.dumps(original.to_dict())

        # Deserialize from JSON
        data = json.loads(json_str)
        restored = ScanProfile.from_dict(data)

        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.targets == original.targets
        assert restored.exclusions == original.exclusions
        assert restored.options == original.options
