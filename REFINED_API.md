# YetAnotherSchema - Refined API Design

**Philosophy:** Not a database, not a table - it's a **SPACE** where values exist as free ions.

---

## 🎯 Core Concepts

### Terminology
- **Space** - Where all values are stored (not "database" or "table")
- **Value** - Atomic unit with metadata: `[raw_value, {unit: kg, cat: xyz}, reported_ts, created_ts, user_id]`
- **Context Store** - Maps contexts to values (at least 1 context required)
- **Relationship Store** - Defines hierarchies (e.g., Site → Country → Region)
- **Expression Store** - Derived calculations (e.g., BMI)

### Value Structure
```python
value = {
    'raw_value': 170,
    'metadata': {'unit': 'cm', 'category': 'vital_sign'},
    'reported_timestamp': '2026-01-30T09:00:00',  # User-reported
    'created_timestamp': '2026-01-30T09:01:23',   # System-generated
    'user_id': 'nurse_001'
}
```

### No Edits, Only Appends
- Rename = new value with different created_timestamp
- Correction = new value with different raw_value
- History preserved forever
- `as_of` queries work on created_timestamp

---

## 📦 User-Facing API (4 Functions)

```python
import yetanotherschema as ys
```

### 1. `ys.create()`

```python
def create(
    space_name: str,
    schema_path: str,
    storage_path: Optional[str] = None
) -> None:
    """
    Create a new space.
    
    Args:
        space_name: Name of the space (e.g., 'clinical_study_001')
        schema_path: Path to schema.toml defining contexts, hierarchies, etc.
        storage_path: Where to store DuckDB file (default: ./{space_name}.db)
    
    Raises:
        SpaceExistsError: If space already exists
        SchemaValidationError: If schema is invalid
    
    Example:
        ys.create(
            space_name='clinical_study_001',
            schema_path='schema.toml'
        )
    
    Future (not now):
        # Modify structure by adding variables
        ys.create(
            space_name='clinical_study_001',
            schema_path='updated_schema.toml',
            mode='modify'  # Add new variables
        )
    """
    pass
```

### 2. `ys.write()`

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
            - raw_value: Any (required)
            - metadata: Dict (optional, merged with schema)
            - reported_timestamp: str (optional, ISO format)
            - user_id: str (required)
        contexts: Context mappings (at least 1 required)
            e.g., {'subject_id': 'S001', 'visit': 'V1'}
    
    Returns:
        value_id: Unique ID of created value
    
    Raises:
        SpaceNotFoundError: If space doesn't exist
        ValidationError: If required contexts missing
        AuthenticationError: If user_id invalid (future)
    
    Example:
        value_id = ys.write(
            space_name='clinical_study_001',
            field='height',
            value={
                'raw_value': 170,
                'metadata': {'unit': 'cm', 'category': 'vital_sign'},
                'reported_timestamp': '2026-01-30T09:00:00',
                'user_id': 'nurse_001'
            },
            contexts={'subject_id': 'S001', 'visit': 'V1'}
        )
    
    Future (not now):
        # Authentication token embedded in value
        value_id = ys.write(
            space_name='clinical_study_001',
            field='height',
            value={
                'raw_value': 170,
                'user_id': 'nurse_001',
                'auth_token': 'eyJhbGc...'  # JWT or similar
            },
            contexts={'subject_id': 'S001'}
        )
    """
    pass

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
            - value: Dict (same as write())
            - contexts: Dict
    
    Returns:
        List of value_ids
    
    Example:
        value_ids = ys.write_batch(
            space_name='clinical_study_001',
            records=[
                {
                    'field': 'height',
                    'value': {
                        'raw_value': 170,
                        'user_id': 'nurse_001'
                    },
                    'contexts': {'subject_id': 'S001', 'visit': 'V1'}
                },
                {
                    'field': 'weight',
                    'value': {
                        'raw_value': 70,
                        'user_id': 'nurse_001'
                    },
                    'contexts': {'subject_id': 'S001', 'visit': 'V1'}
                }
            ]
        )
    """
    pass
```

### 3. `ys.read()`

```python
def read(
    space_name: str,
    as_: List[str],
    contexts: Optional[Dict[str, str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    as_of: Optional[str] = None
) -> pl.DataFrame:
    """
    Read values from the space as a Polars table.
    
    Args:
        space_name: Name of the space
        as_: List of fields to include (e.g., ['subject_id', 'height', 'weight'])
             Context fields are automatically included
        contexts: Optional context filter (e.g., {'subject_id': 'S001'})
        filters: Optional value filters (e.g., {'height': {'gt': 20}})
        as_of: Optional timestamp for time-travel (ISO format)
               Uses created_timestamp for filtering
    
    Returns:
        Polars DataFrame with requested fields
    
    Raises:
        SpaceNotFoundError: If space doesn't exist
        FieldNotFoundError: If field in as_ doesn't exist
    
    Examples:
        # Basic read
        df = ys.read(
            space_name='clinical_study_001',
            as_=['subject_id', 'height', 'weight']
        )
        
        # With context filter
        df = ys.read(
            space_name='clinical_study_001',
            as_=['subject_id', 'visit', 'height', 'weight'],
            contexts={'subject_id': 'S001'}
        )
        
        # With value filters
        df = ys.read(
            space_name='clinical_study_001',
            as_=['subject_id', 'height', 'weight'],
            filters={
                'height': {'gt': 20, 'lt': 200},
                'weight': {'gt': 30}
            }
        )
        
        # Time-travel query (as of created_timestamp)
        df = ys.read(
            space_name='clinical_study_001',
            as_=['subject_id', 'height', 'weight'],
            as_of='2026-01-15T00:00:00'
        )
    
    Future (not now):
        # Event-based time-travel (as_of event_date)
        df = ys.read(
            space_name='clinical_study_001',
            as_=['subject_id', 'height', 'weight'],
            as_of_event='2026-01-15',  # Based on reported_timestamp
            handle_missing='forward_fill'  # How to handle missing values
        )
    """
    pass
```

### 4. `ys.schema()`

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
            - 'summary': High-level overview
            - 'full': Complete schema with all metadata
            - 'contexts': Only context definitions
            - 'hierarchies': Only hierarchy definitions
            - 'values': Only value field definitions
    
    Returns:
        Dict with schema information
    
    Example:
        # Summary
        schema_info = ys.schema('clinical_study_001')
        print(schema_info)
        # {
        #     'space_name': 'clinical_study_001',
        #     'contexts': {
        #         'required': ['subject_id'],
        #         'optional': ['visit', 'timepoint']
        #     },
        #     'hierarchies': {
        #         'geographic': ['region', 'country', 'site'],
        #         'lab': ['lab_category', 'lab_subcategory', 'lab_test']
        #     },
        #     'values': ['height', 'weight', 'temperature'],
        #     'total_values': 1500,
        #     'created_at': '2026-01-30T08:00:00'
        # }
        
        # Full detail
        full_schema = ys.schema('clinical_study_001', detail='full')
        
        # Only contexts
        contexts = ys.schema('clinical_study_001', detail='contexts')
    """
    pass
```

---

## 🏗️ Internal Architecture (Not User-Facing)

### Storage Layers

```
┌─────────────────────────────────────────────────────────┐
│                    SPACE                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Expression Store (Outer Sphere)                       │
│  - Derived calculations (BMI, etc.)                    │
│  - Never materialized                                  │
│                                                         │
│  Relationship Store (Middle Sphere)                    │
│  - Hierarchies (Site → Country → Region)               │
│  - AST-based relationships                             │
│                                                         │
│  Context Store (Middle Sphere)                         │
│  - Maps contexts → value indices                       │
│  - At least 1 context per value                        │
│                                                         │
│  Value Store (Inner Sphere)                            │
│  - Atomic values with full metadata                    │
│  - [raw_value, metadata, reported_ts, created_ts, uid] │
│  - Append-only, never deleted                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Internal Functions (Many)
- DatabaseManager
- ValueStore operations
- ContextStore operations
- RelationshipStore operations
- ExpressionEngine
- QueryEngine
- Schema validation
- Type conversion
- Context parsing
- etc.

---

## ❓ Questions & Clarifications Needed

### 1. Value Structure - Confirm Format

**Option A: Dict with nested metadata**
```python
value = {
    'raw_value': 170,
    'metadata': {'unit': 'cm', 'category': 'vital_sign'},
    'reported_timestamp': '2026-01-30T09:00:00',
    'user_id': 'nurse_001'
}
```

**Option B: Flat dict**
```python
value = {
    'raw_value': 170,
    'unit': 'cm',
    'category': 'vital_sign',
    'reported_timestamp': '2026-01-30T09:00:00',
    'user_id': 'nurse_001'
}
```

**Which do you prefer?** I suggest Option A (nested) for flexibility.

---

### 2. Filters Syntax - Confirm Format

**Option A: Dict-based**
```python
filters = {
    'height': {'gt': 20, 'lt': 200},
    'weight': {'gte': 30, 'lte': 150}
}
```

**Option B: Polars expressions**
```python
filters = [
    pl.col('height') > 20,
    pl.col('height') < 200,
    pl.col('weight') >= 30
]
```

**Which do you prefer?** Option A is simpler for users, Option B is more powerful.

---

### 3. `as_` Parameter - Naming

The parameter `as_` (with underscore) is to avoid Python keyword `as`.

**Alternatives:**
- `fields`
- `select`
- `columns`
- `include`

**Which do you prefer?** I suggest `fields` for clarity.

---

### 4. Space Management

**Should we have additional functions?**

```python
# List all spaces
spaces = ys.list_spaces()

# Delete a space
ys.delete_space('clinical_study_001')

# Copy a space
ys.copy_space('study_001', 'study_001_backup')

# Get space info
info = ys.info('clinical_study_001')
```

**Do you want these now or later?**

---

### 5. Context Requirement

You said "at least 1 context is mandatory". 

**Clarification:**
- Is this enforced at schema level (required contexts)?
- Or can any context be provided as long as there's at least one?

**Example:**
```toml
[contexts]
required = ["subject_id"]  # Must always provide
optional = ["visit", "timepoint"]  # Can provide
```

Is this correct?

---

### 6. Metadata Merging

You mentioned "metadata merged with schema".

**Example:**
```toml
# schema.toml
[values]
height = { unit = "cm", type = "numeric", category = "vital_sign" }
```

```python
# User writes
ys.write(
    field='height',
    value={
        'raw_value': 170,
        'metadata': {'custom_field': 'baseline'},  # User adds this
        'user_id': 'nurse_001'
    }
)

# Final metadata stored:
# {'unit': 'cm', 'type': 'numeric', 'category': 'vital_sign', 'custom_field': 'baseline'}
```

**Is this correct?**

---

### 7. Authentication (Future)

You mentioned "significant departure from traditional db authentication".

**Can you give a hint?** I'm curious about your vision here. Is it:
- Token-based (JWT)?
- Cryptographic (public/private keys)?
- Blockchain-inspired?
- Something else?

(Not implementing now, just curious for future design)

---

### 8. Return Format for `read()`

**Should `read()` always return a pivoted table?**

```python
# Pivoted (wide format)
df = ys.read(as_=['subject_id', 'visit', 'height', 'weight'])
# Result:
# subject_id | visit | height | weight
# S001       | V1    | 170    | 70
# S001       | V2    | 171    | 72

# Or should we support long format too?
df = ys.read(as_=['subject_id', 'visit', 'height', 'weight'], format='long')
# Result:
# subject_id | visit | field  | value
# S001       | V1    | height | 170
# S001       | V1    | weight | 70
# S001       | V2    | height | 171
# S001       | V2    | weight | 72
```

**Which format(s) should we support?**

---

## 📝 Proposed Refined API Summary

```python
import yetanotherschema as ys

# 1. Create a space
ys.create(
    space_name='clinical_study_001',
    schema_path='schema.toml'
)

# 2. Write values
ys.write(
    space_name='clinical_study_001',
    field='height',
    value={
        'raw_value': 170,
        'metadata': {'unit': 'cm'},
        'reported_timestamp': '2026-01-30T09:00:00',
        'user_id': 'nurse_001'
    },
    contexts={'subject_id': 'S001', 'visit': 'V1'}
)

# 2b. Batch write
ys.write_batch(space_name='...', records=[...])

# 3. Read values
df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'visit', 'height', 'weight'],
    contexts={'subject_id': 'S001'},
    filters={'height': {'gt': 20}},
    as_of='2026-01-15T00:00:00'
)

# 4. View schema
schema_info = ys.schema('clinical_study_001')
```

**Total user-facing functions: 4 (+ write_batch)**

---

## 🎯 Next Steps

Once you answer the questions above, I'll:
1. Create the refined API specification
2. Design the internal architecture
3. Start implementation

**What do you think?**
