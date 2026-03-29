# YetAnotherSchema - Final API Specification

**Version:** 0.1.0 MVP  
**Philosophy:** Metadata is informational only. No validation. Frontend handles validation.

---

## 🎯 Complete API (4 Functions)

```python
import yetanotherschema as ys
```

---

## 1. `ys.create()` - Create a Space

### Function Signature

```python
def create(
    space_name: str,
    schema_path: str,
    storage_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new space.
    
    Args:
        space_name: Name of the space (e.g., 'clinical_study_001')
        schema_path: Path to schema.toml
        storage_path: Optional custom storage path (default: ./{space_name}.db)
    
    Returns:
        Dict with creation info:
            - space_name: str
            - storage_path: str
            - created_at: str (ISO timestamp)
            - schema_version: str
    
    Raises:
        SpaceExistsError: If space already exists
        SchemaValidationError: If schema.toml is invalid
    """
```

### Example Usage

```python
# Create a space
result = ys.create(
    space_name='clinical_study_001',
    schema_path='schema.toml'
)

print(result)
# {
#     'space_name': 'clinical_study_001',
#     'storage_path': './clinical_study_001.db',
#     'created_at': '2026-01-30T10:00:00.123456',
#     'schema_version': '0.1.0'
# }
```

---

## 2. `ys.write()` - Write a Value

### Function Signature

```python
def write(
    space_name: str,
    field: str,
    value: Dict[str, Any],
    contexts: Dict[str, str]
) -> int:
    """
    Write a value to the space.
    
    Args:
        space_name: Name of the space
        field: Field name (e.g., 'height', 'weight')
        value: Value dict with:
            - raw_value: Any (required) - the actual measurement
            - metadata: Dict[str, Any] (optional) - informational only, no validation
            - reported_timestamp: str (optional) - ISO format, user-reported time
            - user_id: str (required) - who created this value
        contexts: Context mappings (at least 1 required per schema)
            e.g., {'subject_id': 'S001', 'visit': 'V1'}
    
    Returns:
        value_id: int - Unique ID of created value
    
    Raises:
        SpaceNotFoundError: If space doesn't exist
        ValidationError: If required contexts missing (per schema)
        ValidationError: If required value fields missing (raw_value, user_id)
    
    Notes:
        - Metadata is NOT validated against schema
        - User can enter any metadata fields
        - Schema metadata is merged with user metadata (user wins on conflicts)
        - This enables unit harmonization (e.g., cm → inches)
        - Frontend should handle validation if needed
    """

def write_batch(
    space_name: str,
    records: List[Dict[str, Any]]
) -> List[int]:
    """
    Write multiple values in batch (faster).
    
    Args:
        space_name: Name of the space
        records: List of dicts, each with:
            - field: str
            - value: Dict (same structure as write())
            - contexts: Dict
    
    Returns:
        List[int]: List of value_ids
    """
```

### Example Usage

```python
# Example 1: Basic write with schema metadata
ys.write(
    space_name='clinical_study_001',
    field='height',
    value={
        'raw_value': 170,
        'user_id': 'nurse_001'
    },
    contexts={'subject_id': 'S001', 'visit': 'V1'}
)
# Schema metadata (unit: cm) is automatically added

# Example 2: Write with custom metadata (overrides schema)
ys.write(
    space_name='clinical_study_001',
    field='height',
    value={
        'raw_value': 67,  # Different value
        'metadata': {
            'unit': 'inches',  # User overrides schema (cm)
            'device': 'tape_measure',
            'custom_field': 'baseline_measurement'
        },
        'reported_timestamp': '2026-01-30T09:00:00',
        'user_id': 'nurse_001'
    },
    contexts={'subject_id': 'S001', 'visit': 'V1'}
)
# Final metadata: {unit: 'inches', device: 'tape_measure', custom_field: 'baseline_measurement'}
# User metadata wins - enables unit harmonization later

# Example 3: Write with all fields
ys.write(
    space_name='clinical_study_001',
    field='weight',
    value={
        'raw_value': 154,
        'metadata': {
            'unit': 'lbs',  # User enters pounds
            'device': 'scale_model_y',
            'calibration_date': '2026-01-15',
            'quality_flag': 'verified',
            'notes': 'Patient wearing light clothing'
        },
        'reported_timestamp': '2026-01-30T09:05:00',
        'user_id': 'nurse_001'
    },
    contexts={
        'subject_id': 'S001',
        'visit': 'V1',
        'site': 'Site_Boston'
    }
)
# Returns: value_id (e.g., 42)

# Example 4: Batch write
value_ids = ys.write_batch(
    space_name='clinical_study_001',
    records=[
        {
            'field': 'height',
            'value': {
                'raw_value': 170,
                'metadata': {'unit': 'cm'},
                'user_id': 'nurse_001'
            },
            'contexts': {'subject_id': 'S001', 'visit': 'V1'}
        },
        {
            'field': 'weight',
            'value': {
                'raw_value': 70,
                'metadata': {'unit': 'kg'},
                'user_id': 'nurse_001'
            },
            'contexts': {'subject_id': 'S001', 'visit': 'V1'}
        },
        {
            'field': 'temperature',
            'value': {
                'raw_value': 98.6,
                'metadata': {'unit': 'fahrenheit'},
                'user_id': 'nurse_001'
            },
            'contexts': {'subject_id': 'S001', 'visit': 'V1'}
        }
    ]
)
# Returns: [42, 43, 44]

# Example 5: Data correction (append-only)
# Original entry (typo)
ys.write(
    space_name='clinical_study_001',
    field='weight',
    value={
        'raw_value': 500,  # Typo!
        'metadata': {'unit': 'kg'},
        'reported_timestamp': '2026-01-30T09:05:00',
        'user_id': 'nurse_001'
    },
    contexts={'subject_id': 'S001', 'visit': 'V1'}
)
# created_timestamp: 2026-01-30T09:05:23

# Correction (new entry)
ys.write(
    space_name='clinical_study_001',
    field='weight',
    value={
        'raw_value': 50,  # Corrected
        'metadata': {'unit': 'kg', 'correction': 'typo_fix'},
        'reported_timestamp': '2026-01-30T09:05:00',  # Same reported time
        'user_id': 'nurse_001'
    },
    contexts={'subject_id': 'S001', 'visit': 'V1'}
)
# created_timestamp: 2026-01-30T09:06:15 (later)
# Both values preserved, latest returned by default
```

---

## 3. `ys.read()` - Read Values

### Function Signature

```python
def read(
    space_name: str,
    fields: List[str],
    contexts: Optional[Dict[str, str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    as_of: Optional[str] = None,
    include_metadata: bool = False
) -> pl.DataFrame:
    """
    Read values from the space as a Polars DataFrame.
    
    Args:
        space_name: Name of the space
        fields: List of fields to include
            - Context fields (e.g., 'subject_id', 'visit')
            - Value fields (e.g., 'height', 'weight')
        contexts: Optional context filter
            e.g., {'subject_id': 'S001'} - returns all visits for S001
            e.g., {'subject_id': 'S001', 'visit': 'V1'} - specific visit
        filters: Optional value filters (dict-based syntax)
            e.g., {'height': {'gt': 160, 'lt': 200}}
            e.g., {'weight': {'gte': 50, 'lte': 100}}
            Supported operators: gt, gte, lt, lte, eq, ne, contains, in, not_in
        as_of: Optional timestamp for time-travel (ISO format)
            Uses created_timestamp for filtering
            e.g., '2026-01-15T23:59:59' - data as it existed on Jan 15
        include_metadata: If True, include metadata column in result
    
    Returns:
        Polars DataFrame with requested fields
        - Context columns (from fields list)
        - Value columns (from fields list)
        - metadata column (if include_metadata=True)
    
    Raises:
        SpaceNotFoundError: If space doesn't exist
        FieldNotFoundError: If field in fields list doesn't exist
    
    Notes:
        - Returns latest value by default (based on created_timestamp)
        - Pivoted to wide format (one row per unique context combination)
        - Metadata not validated - can contain any fields
    """
```

### Example Usage

```python
# Example 1: Basic read
df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'visit', 'height', 'weight']
)
print(df)
# ┌────────────┬───────┬────────┬────────┐
# │ subject_id │ visit │ height │ weight │
# │ ---        │ ---   │ ---    │ ---    │
# │ str        │ str   │ f64    │ f64    │
# ╞════════════╪═══════╪════════╪════════╡
# │ S001       │ V1    │ 170.0  │ 70.0   │
# │ S001       │ V2    │ 171.0  │ 72.0   │
# │ S002       │ V1    │ 165.0  │ 60.0   │
# └────────────┴───────┴────────┴────────┘

# Example 2: With context filter
df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'visit', 'height', 'weight'],
    contexts={'subject_id': 'S001'}  # Only S001
)
print(df)
# ┌────────────┬───────┬────────┬────────┐
# │ subject_id │ visit │ height │ weight │
# ╞════════════╪═══════╪════════╪════════╡
# │ S001       │ V1    │ 170.0  │ 70.0   │
# │ S001       │ V2    │ 171.0  │ 72.0   │
# └────────────┴───────┴────────┴────────┘

# Example 3: With value filters
df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'visit', 'height', 'weight'],
    filters={
        'height': {'gt': 160, 'lt': 180},
        'weight': {'gte': 50, 'lte': 100}
    }
)
print(df)
# Only rows where height between 160-180 and weight between 50-100

# Example 4: Time-travel query
df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'visit', 'weight'],
    contexts={'subject_id': 'S001', 'visit': 'V1'},
    as_of='2026-01-30T09:05:30'  # Before correction
)
print(df)
# ┌────────────┬───────┬────────┐
# │ subject_id │ visit │ weight │
# ╞════════════╪═══════╪════════╡
# │ S001       │ V1    │ 500.0  │  # Shows typo (before correction)
# └────────────┴───────┴────────┘

df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'visit', 'weight'],
    contexts={'subject_id': 'S001', 'visit': 'V1'},
    as_of='2026-01-30T09:06:30'  # After correction
)
print(df)
# ┌────────────┬───────┬────────┐
# │ subject_id │ visit │ weight │
# ╞════════════╪═══════╪════════╡
# │ S001       │ V1    │ 50.0   │  # Shows corrected value
# └────────────┴───────┴────────┘

# Example 5: With metadata
df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'height', 'weight'],
    contexts={'subject_id': 'S001'},
    include_metadata=True
)
print(df)
# ┌────────────┬────────┬────────┬──────────────────────────────┐
# │ subject_id │ height │ weight │ metadata                     │
# │ ---        │ ---    │ ---    │ ---                          │
# │ str        │ f64    │ f64    │ struct                       │
# ╞════════════╪════════╪════════╪══════════════════════════════╡
# │ S001       │ 170.0  │ 70.0   │ {height: {unit: cm, ...},    │
# │            │        │        │  weight: {unit: kg, ...}}    │
# └────────────┴────────┴────────┴──────────────────────────────┘

# Example 6: Complex filters
df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'visit', 'hemoglobin'],
    filters={
        'hemoglobin': {
            'or': [
                {'lt': 12.0},  # Below normal
                {'gt': 16.0}   # Above normal
            ]
        }
    }
)
# Returns only abnormal hemoglobin values

# Example 7: Text filtering
df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'adverse_event'],
    filters={
        'adverse_event': {'contains': 'headache'}
    }
)
# Returns only adverse events containing "headache"

# Example 8: Multiple context levels
df = ys.read(
    space_name='clinical_study_001',
    fields=['country', 'site', 'subject_id', 'height', 'weight'],
    contexts={'country': 'USA'}  # All sites in USA
)
# Returns data for all USA sites
```

### Filter Operators Reference

```python
filters = {
    'field_name': {
        # Numeric comparisons
        'gt': 100,          # Greater than
        'gte': 100,         # Greater than or equal
        'lt': 200,          # Less than
        'lte': 200,         # Less than or equal
        'eq': 150,          # Equal to
        'ne': 150,          # Not equal to
        
        # List operations
        'in': [100, 150, 200],      # Value in list
        'not_in': [100, 150, 200],  # Value not in list
        
        # String operations
        'contains': 'text',         # Contains substring
        'starts_with': 'prefix',    # Starts with
        'ends_with': 'suffix',      # Ends with
        
        # Logical operations
        'or': [                     # Any condition matches
            {'gt': 100},
            {'lt': 50}
        ],
        'and': [                    # All conditions match
            {'gt': 50},
            {'lt': 100}
        ]
    }
}
```

---

## 4. `ys.schema()` - View Schema

### Function Signature

```python
def schema(
    space_name: str,
    detail: str = 'summary'
) -> Dict[str, Any]:
    """
    Display the schema of a space.
    
    Args:
        space_name: Name of the space
        detail: Level of detail
            - 'summary': High-level overview (default)
            - 'full': Complete schema with all metadata
            - 'contexts': Only context definitions
            - 'hierarchies': Only hierarchy definitions
            - 'values': Only value field definitions
            - 'stats': Statistics about the space
    
    Returns:
        Dict with schema information (structure depends on detail level)
    
    Raises:
        SpaceNotFoundError: If space doesn't exist
    """
```

### Example Usage

```python
# Example 1: Summary view
schema_info = ys.schema('clinical_study_001')
print(schema_info)
# {
#     'space_name': 'clinical_study_001',
#     'schema_version': '0.1.0',
#     'created_at': '2026-01-30T08:00:00',
#     'contexts': {
#         'required': ['subject_id'],
#         'optional': ['visit', 'timepoint', 'site']
#     },
#     'hierarchies': {
#         'geographic': ['region', 'country', 'site'],
#         'lab': ['lab_category', 'lab_subcategory', 'lab_test']
#     },
#     'value_fields': ['height', 'weight', 'temperature', 'hemoglobin'],
#     'total_values': 1500,
#     'unique_contexts': 250
# }

# Example 2: Full schema
full_schema = ys.schema('clinical_study_001', detail='full')
print(full_schema)
# {
#     'space_name': 'clinical_study_001',
#     'schema_version': '0.1.0',
#     'created_at': '2026-01-30T08:00:00',
#     'contexts': {...},
#     'hierarchies': {...},
#     'values': {
#         'height': {
#             'unit': 'cm',
#             'type': 'numeric',
#             'category': 'vital_sign',
#             'reference_range': '150-200'
#         },
#         'weight': {
#             'unit': 'kg',
#             'type': 'numeric',
#             'category': 'vital_sign'
#         },
#         ...
#     },
#     'null_values': {
#         'not_done': '@notdone',
#         'missing': '@null',
#         'refused': '@refused'
#     }
# }

# Example 3: Only contexts
contexts = ys.schema('clinical_study_001', detail='contexts')
print(contexts)
# {
#     'required': ['subject_id'],
#     'optional': ['visit', 'timepoint', 'site', 'country']
# }

# Example 4: Statistics
stats = ys.schema('clinical_study_001', detail='stats')
print(stats)
# {
#     'space_name': 'clinical_study_001',
#     'total_values': 1500,
#     'unique_contexts': 250,
#     'value_fields': 12,
#     'storage_size_mb': 45.3,
#     'oldest_timestamp': '2026-01-01T00:00:00',
#     'newest_timestamp': '2026-01-30T15:30:00',
#     'values_by_field': {
#         'height': 250,
#         'weight': 250,
#         'temperature': 200,
#         'hemoglobin': 150,
#         ...
#     }
# }
```

---

## 5. `ys.list_spaces()` - List All Spaces

### Function Signature

```python
def list_spaces(
    storage_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List all available spaces.
    
    Args:
        storage_path: Optional path to search for spaces (default: current directory)
    
    Returns:
        List of dicts, each with:
            - space_name: str
            - storage_path: str
            - created_at: str
            - schema_version: str
            - total_values: int
            - storage_size_mb: float
    """
```

### Example Usage

```python
# List all spaces
spaces = ys.list_spaces()
print(spaces)
# [
#     {
#         'space_name': 'clinical_study_001',
#         'storage_path': './clinical_study_001.db',
#         'created_at': '2026-01-30T08:00:00',
#         'schema_version': '0.1.0',
#         'total_values': 1500,
#         'storage_size_mb': 45.3
#     },
#     {
#         'space_name': 'factory_monitoring',
#         'storage_path': './factory_monitoring.db',
#         'created_at': '2026-01-25T10:00:00',
#         'schema_version': '0.1.0',
#         'total_values': 50000,
#         'storage_size_mb': 230.5
#     }
# ]
```

---

## 📊 Complete API Summary

```python
import yetanotherschema as ys

# 1. Create a space
ys.create(space_name='...', schema_path='...')

# 2. Write values
ys.write(space_name='...', field='...', value={...}, contexts={...})
ys.write_batch(space_name='...', records=[...])

# 3. Read values
df = ys.read(
    space_name='...',
    fields=[...],
    contexts={...},
    filters={...},
    as_of='...'
)

# 4. View schema
schema = ys.schema(space_name='...', detail='...')

# 5. List spaces
spaces = ys.list_spaces()
```

**Total Functions:** 5 (create, write, write_batch, read, schema, list_spaces)

---

## 🎯 Key Design Principles

1. **Metadata is informational only** - No validation, user can enter anything
2. **User metadata wins** - Enables unit harmonization (cm → inches)
3. **Frontend validates** - If validation needed, do it in UI
4. **Append-only** - Corrections are new entries, not updates
5. **Latest by default** - Based on created_timestamp
6. **Time-travel** - `as_of` parameter for historical queries
7. **Flexible filters** - Dict-based syntax, easy to use
8. **Polars output** - Fast, modern DataFrames

---

**Ready to implement?** This is the final API specification!
