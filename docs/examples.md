# YetAnotherSchema - Detailed Examples

---

## 1. Value Structure - Nested Dict Examples

### Example 1: Clinical Research Data

```python
import yetanotherschema as ys

# Write height measurement
ys.write(
    space_name='clinical_study_001',
    field='height',
    value={
        'raw_value': 170,
        'metadata': {
            'unit': 'cm',
            'category': 'vital_sign',
            'device': 'stadiometer_model_x',
            'measurement_method': 'standing',
            'quality_flag': 'verified'
        },
        'reported_timestamp': '2026-01-30T09:00:00',
        'user_id': 'nurse_001'
    },
    contexts={
        'subject_id': 'S001',
        'visit': 'V1',
        'site': 'Site_Boston'
    }
)

# Write weight measurement
ys.write(
    space_name='clinical_study_001',
    field='weight',
    value={
        'raw_value': 70,
        'metadata': {
            'unit': 'kg',
            'category': 'vital_sign',
            'device': 'scale_model_y',
            'calibration_date': '2026-01-15',
            'quality_flag': 'verified'
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

# Write lab result
ys.write(
    space_name='clinical_study_001',
    field='hemoglobin',
    value={
        'raw_value': 14.5,
        'metadata': {
            'unit': 'g/dL',
            'category': 'lab_result',
            'lab_name': 'Central_Lab',
            'test_method': 'automated_analyzer',
            'reference_range': '12.0-16.0',
            'abnormal_flag': 'normal'
        },
        'reported_timestamp': '2026-01-30T14:30:00',
        'user_id': 'lab_tech_005'
    },
    contexts={
        'subject_id': 'S001',
        'visit': 'V1',
        'site': 'Site_Boston',
        'lab_category': 'hematology'
    }
)

# Write adverse event
ys.write(
    space_name='clinical_study_001',
    field='adverse_event',
    value={
        'raw_value': 'Mild headache',
        'metadata': {
            'unit': 'none',
            'category': 'safety',
            'severity': 'mild',
            'relationship': 'possibly_related',
            'action_taken': 'none',
            'outcome': 'resolved'
        },
        'reported_timestamp': '2026-01-31T10:00:00',
        'user_id': 'physician_003'
    },
    contexts={
        'subject_id': 'S001',
        'visit': 'V1',
        'site': 'Site_Boston',
        'ae_number': 'AE001'
    }
)
```

### Example 2: IoT Sensor Data

```python
# Temperature sensor reading
ys.write(
    space_name='factory_monitoring',
    field='temperature',
    value={
        'raw_value': 75.3,
        'metadata': {
            'unit': 'celsius',
            'category': 'environmental',
            'sensor_type': 'thermocouple',
            'accuracy': '±0.1',
            'calibration_status': 'valid'
        },
        'reported_timestamp': '2026-01-30T12:00:00',
        'user_id': 'sensor_gateway_01'
    },
    contexts={
        'device_id': 'TEMP_001',
        'location': 'Assembly_Line_A',
        'facility': 'Factory_Boston',
        'batch_id': 'BATCH_2026_001'
    }
)

# Vibration sensor reading
ys.write(
    space_name='factory_monitoring',
    field='vibration',
    value={
        'raw_value': 2.5,
        'metadata': {
            'unit': 'mm/s',
            'category': 'mechanical',
            'sensor_type': 'accelerometer',
            'frequency_range': '10-1000Hz',
            'alarm_threshold': '5.0'
        },
        'reported_timestamp': '2026-01-30T12:00:01',
        'user_id': 'sensor_gateway_01'
    },
    contexts={
        'device_id': 'VIB_001',
        'location': 'Assembly_Line_A',
        'facility': 'Factory_Boston',
        'machine_id': 'MACHINE_A1'
    }
)
```

### Example 3: Financial Trading Data

```python
# Stock price
ys.write(
    space_name='trading_data',
    field='price',
    value={
        'raw_value': 150.25,
        'metadata': {
            'unit': 'USD',
            'category': 'market_data',
            'exchange': 'NYSE',
            'trade_type': 'limit_order',
            'volume': 1000
        },
        'reported_timestamp': '2026-01-30T09:30:00.123',
        'user_id': 'trading_system_01'
    },
    contexts={
        'ticker': 'AAPL',
        'exchange': 'NYSE',
        'trader_id': 'TRADER_001',
        'order_id': 'ORD_123456'
    }
)
```

---

## 2. Filters Syntax - Real Examples

### Example 1: Column Filtering + as_of Date

```python
import yetanotherschema as ys
import polars as pl

# Scenario: Get height and weight for subjects where height > 160cm
# and weight between 50-100kg, as of January 15, 2026

df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'visit', 'height', 'weight'],
    contexts={'site': 'Site_Boston'},  # Optional: filter by site
    filters={
        'height': {'gt': 160, 'lt': 200},
        'weight': {'gte': 50, 'lte': 100}
    },
    as_of='2026-01-15T23:59:59'  # Time-travel to Jan 15
)

print(df)
# Result (Polars DataFrame):
# ┌────────────┬───────┬────────┬────────┐
# │ subject_id │ visit │ height │ weight │
# │ ---        │ ---   │ ---    │ ---    │
# │ str        │ str   │ f64    │ f64    │
# ╞════════════╪═══════╪════════╪════════╡
# │ S001       │ V1    │ 170.0  │ 70.0   │
# │ S002       │ V1    │ 165.0  │ 60.0   │
# │ S003       │ V1    │ 175.0  │ 80.0   │
# └────────────┴───────┴────────┴────────┘
```

### Example 2: Multiple Filter Conditions

```python
# Get lab results for hemoglobin where value is abnormal
# (outside reference range 12.0-16.0)

df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'visit', 'hemoglobin'],
    contexts={'lab_category': 'hematology'},
    filters={
        'hemoglobin': {
            'or': [
                {'lt': 12.0},  # Below normal
                {'gt': 16.0}   # Above normal
            ]
        }
    }
)

print(df)
# Result:
# ┌────────────┬───────┬────────────┐
# │ subject_id │ visit │ hemoglobin │
# │ ---        │ ---   │ ---        │
# │ str        │ str   │ f64        │
# ╞════════════╪═══════╪════════════╡
# │ S005       │ V1    │ 11.5       │
# │ S012       │ V2    │ 16.8       │
# └────────────┴───────┴────────────┘
```

### Example 3: Text Filtering

```python
# Get adverse events containing "headache"

df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'visit', 'adverse_event'],
    filters={
        'adverse_event': {'contains': 'headache'}
    }
)

print(df)
# Result:
# ┌────────────┬───────┬────────────────┐
# │ subject_id │ visit │ adverse_event  │
# │ ---        │ ---   │ ---            │
# │ str        │ str   │ str            │
# ╞════════════╪═══════╪════════════════╡
# │ S001       │ V1    │ Mild headache  │
# │ S003       │ V2    │ Severe headache│
# └────────────┴───────┴────────────────┘
```

### Example 4: Time-Travel with Context Filter

```python
# Get all measurements for Subject S001 as they existed on Jan 10
# (before any corrections were made)

df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'visit', 'height', 'weight'],
    contexts={'subject_id': 'S001'},
    as_of='2026-01-10T23:59:59'
)

print(df)
# Result shows data as it was on Jan 10
# (may include typos that were later corrected)
```

### Example 5: IoT Sensor Filtering

```python
# Get temperature readings above alarm threshold

df = ys.read(
    space_name='factory_monitoring',
    fields=['device_id', 'location', 'temperature', 'timestamp'],
    contexts={'facility': 'Factory_Boston'},
    filters={
        'temperature': {'gt': 80.0}  # Alarm threshold
    },
    as_of='2026-01-30T23:59:59'
)

print(df)
# Result:
# ┌───────────┬─────────────────┬─────────────┬─────────────────────┐
# │ device_id │ location        │ temperature │ timestamp           │
# │ ---       │ ---             │ ---         │ ---                 │
# │ str       │ str             │ f64         │ datetime            │
# ╞═══════════╪═════════════════╪═════════════╪═════════════════════╡
# │ TEMP_001  │ Assembly_Line_A │ 85.3        │ 2026-01-30 14:30:00 │
# │ TEMP_003  │ Assembly_Line_C │ 82.1        │ 2026-01-30 15:45:00 │
# └───────────┴─────────────────┴─────────────┴─────────────────────┘
```

---

## 3. Parameter Naming - `fields` Examples

### Example 1: Basic Usage

```python
# Using 'fields' parameter
df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'visit', 'height', 'weight']
)

# Clear and intuitive - "give me these fields"
```

### Example 2: With Context Fields

```python
# Context fields are automatically included
df = ys.read(
    space_name='clinical_study_001',
    fields=['height', 'weight'],  # Value fields
    contexts={'subject_id': 'S001', 'visit': 'V1'}  # Context fields auto-included
)

# Result includes: subject_id, visit, height, weight
```

### Example 3: All Fields

```python
# Get all fields (no fields parameter = all)
df = ys.read(
    space_name='clinical_study_001',
    contexts={'subject_id': 'S001'}
)

# Returns all value fields for S001
```

### Example 4: Selective Fields

```python
# Get only specific fields
df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'hemoglobin', 'platelet_count'],
    contexts={'lab_category': 'hematology'}
)

# Only returns requested fields
```

---

## 4. Space Management - Future Vision

### Sub-Spaces for Data Residency

```python
# Main space (corporate HQ - USA)
ys.create(
    space_name='global_study',
    schema_path='schema.toml'
)

# Sub-space for EU data (values only, no relationships)
ys.create_subspace(
    parent_space='global_study',
    subspace_name='global_study_eu',
    storage_path='/eu_datacenter/global_study_eu.db',
    mode='values_only'  # Only value store, no relationships
)

# Sub-space for Asia data
ys.create_subspace(
    parent_space='global_study',
    subspace_name='global_study_asia',
    storage_path='/asia_datacenter/global_study_asia.db',
    mode='values_only'
)

# Write to EU sub-space
ys.write(
    space_name='global_study_eu',
    field='height',
    value={...},
    contexts={'subject_id': 'EU_S001', 'country': 'Germany'}
)

# Read from main space (combines all sub-spaces + relationships)
df = ys.read(
    space_name='global_study',  # Automatically queries all sub-spaces
    fields=['subject_id', 'country', 'height', 'weight']
)

# Result includes data from USA, EU, Asia sub-spaces
# Relationships and expressions applied at main space level
```

### Blinded/Unblinded Separation

```python
# Blinded space (values only)
ys.create_subspace(
    parent_space='clinical_trial',
    subspace_name='clinical_trial_blinded',
    mode='values_only'
)

# Unblinded space (values + relationships + expressions)
ys.create(
    space_name='clinical_trial_unblinded',
    schema_path='schema.toml'
)

# Blinded users can only access blinded space
df_blinded = ys.read(
    space_name='clinical_trial_blinded',
    fields=['subject_id', 'height', 'weight'],
    auth_key='blinded_user_token'
)
# No treatment assignment visible

# Unblinded users can access full space
df_unblinded = ys.read(
    space_name='clinical_trial_unblinded',
    fields=['subject_id', 'treatment', 'height', 'weight'],
    auth_key='unblinded_user_token'
)
# Treatment assignment visible
```

---

## 5. Context Requirement - Schema Example

```toml
# schema.toml

[metadata]
name = "clinical_study_001"
version = "0.1.0"

[contexts]
# At least one required context must be provided
required = ["subject_id"]

# Optional contexts can be provided
optional = ["visit", "timepoint", "site", "country"]

[hierarchies]
# Geographic hierarchy
geographic = ["region", "country", "site"]

# Lab hierarchy
lab = ["lab_category", "lab_subcategory", "lab_test"]

[values]
height = { unit = "cm", type = "numeric", category = "vital_sign" }
weight = { unit = "kg", type = "numeric", category = "vital_sign" }
hemoglobin = { unit = "g/dL", type = "numeric", category = "lab_result" }
```

```python
# Valid write (has required context)
ys.write(
    space_name='clinical_study_001',
    field='height',
    value={...},
    contexts={'subject_id': 'S001'}  # ✅ Required context provided
)

# Valid write (has required + optional contexts)
ys.write(
    space_name='clinical_study_001',
    field='height',
    value={...},
    contexts={
        'subject_id': 'S001',  # Required
        'visit': 'V1',         # Optional
        'site': 'Site_Boston'  # Optional
    }
)

# Invalid write (missing required context)
ys.write(
    space_name='clinical_study_001',
    field='height',
    value={...},
    contexts={'visit': 'V1'}  # ❌ Missing required 'subject_id'
)
# Raises: ValidationError: Required context 'subject_id' missing
```

---

## 6. Metadata Merging - Example

### Schema Definition

```toml
# schema.toml
[values]
height = { 
    unit = "cm", 
    type = "numeric", 
    category = "vital_sign",
    reference_range = "150-200"
}
```

### User Write

```python
# User writes height with additional metadata
ys.write(
    space_name='clinical_study_001',
    field='height',
    value={
        'raw_value': 170,
        'metadata': {
            'device': 'stadiometer_model_x',  # User adds this
            'measurement_method': 'standing',  # User adds this
            'quality_flag': 'verified'         # User adds this
        },
        'user_id': 'nurse_001'
    },
    contexts={'subject_id': 'S001'}
)
```

### Final Stored Metadata

```python
# What gets stored in the database:
{
    'raw_value': 170,
    'metadata': {
        # From schema (automatically added)
        'unit': 'cm',
        'type': 'numeric',
        'category': 'vital_sign',
        'reference_range': '150-200',
        
        # From user (merged in)
        'device': 'stadiometer_model_x',
        'measurement_method': 'standing',
        'quality_flag': 'verified'
    },
    'reported_timestamp': None,  # User didn't provide
    'created_timestamp': '2026-01-30T09:01:23.456',  # Auto-generated
    'user_id': 'nurse_001'
}
```

### Conflict Resolution

```python
# If user provides metadata that conflicts with schema
ys.write(
    space_name='clinical_study_001',
    field='height',
    value={
        'raw_value': 170,
        'metadata': {
            'unit': 'inches',  # ❌ Conflicts with schema (cm)
            'custom_field': 'value'
        },
        'user_id': 'nurse_001'
    },
    contexts={'subject_id': 'S001'}
)

# Option A: Schema wins (recommended)
# Final metadata: {'unit': 'cm', 'custom_field': 'value'}

# Option B: User wins (flexible but risky)
# Final metadata: {'unit': 'inches', 'custom_field': 'value'}

# Option C: Raise error (strict)
# Raises: ValidationError: Metadata 'unit' conflicts with schema
```

**Which option do you prefer?** I suggest Option A (schema wins) for data integrity.

---

## 7. Authentication - Future Vision

### Write with Auth Key

```python
# Every write includes auth_key
ys.write(
    space_name='clinical_study_001',
    field='height',
    value={
        'raw_value': 170,
        'user_id': 'nurse_001',
        'auth_key': 'ys_v1_user_nurse001_ts_20260130_counter_00042_sig_a3f9d2'
    },
    contexts={'subject_id': 'S001'}
)

# Auth key structure (example):
# ys_v1_user_{user_id}_ts_{timestamp}_counter_{counter}_sig_{signature}
#
# - version: v1
# - user_id: nurse001
# - timestamp: 20260130 (date)
# - counter: 00042 (increments with each write)
# - signature: cryptographic signature

# Internal counter tracking
# Every write with this user_id increments counter
# Enables audit: "nurse_001 made 42 writes today"
```

### Read Audit (Future)

```python
# Read operations can also be audited
df = ys.read(
    space_name='clinical_study_001',
    fields=['subject_id', 'height', 'weight'],
    auth_key='ys_v1_user_analyst001_ts_20260130_counter_00015_sig_b7e4c1'
)

# System logs: "analyst001 read height/weight data at 2026-01-30 10:30:00"
```

---

**Does this clarify everything?** Let me know if you want me to adjust any examples!
