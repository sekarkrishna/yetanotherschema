# YetAnotherSchema - API Reference

**Version:** 0.1.0 MVP  
**Complete Function Signatures**

---

## 📦 Main API

### `YetAnotherSchema` (Primary Interface)

```python
class YetAnotherSchema:
    """
    Main database interface for YetAnotherSchema.
    
    Example:
        db = YetAnotherSchema(
            db_path='clinical_study.db',
            schema_path='schema.toml'
        )
    """
    
    def __init__(
        self,
        db_path: str,
        schema_path: str,
        read_only: bool = False
    ) -> None:
        """
        Initialize database.
        
        Args:
            db_path: Path to DuckDB file (created if doesn't exist)
            schema_path: Path to TOML schema definition
            read_only: If True, open in read-only mode
        
        Raises:
            SchemaValidationError: If schema is invalid
            DatabaseError: If database cannot be opened
        """
        pass
    
    def write(
        self,
        field: str,
        raw_value: Any,
        contexts: Dict[str, str],
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        reported_timestamp: Optional[str] = None
    ) -> int:
        """
        Write a single value to the database.
        
        Args:
            field: Field name (e.g., 'height', 'weight')
            raw_value: The actual value (will be converted to string)
            contexts: Context mappings (e.g., {'subject_id': 'S001', 'visit': 'V1'})
            user_id: User who created this value
            metadata: Optional metadata dict (merged with schema metadata)
            reported_timestamp: Optional user-reported timestamp (ISO format)
        
        Returns:
            value_id: Unique ID of the created value
        
        Raises:
            ValidationError: If required contexts are missing
            DatabaseError: If write fails
        
        Example:
            value_id = db.write(
                field='height',
                raw_value=170,
                contexts={'subject_id': 'S001', 'visit': 'V1'},
                user_id='nurse_001',
                reported_timestamp='2026-01-30T09:00:00'
            )
        """
        pass
    
    def write_batch(
        self,
        records: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Write multiple values in a single transaction (faster).
        
        Args:
            records: List of dicts, each with keys:
                - field: str
                - raw_value: Any
                - contexts: Dict[str, str]
                - user_id: str
                - metadata: Optional[Dict]
                - reported_timestamp: Optional[str]
        
        Returns:
            List of value_ids
        
        Example:
            value_ids = db.write_batch([
                {
                    'field': 'height',
                    'raw_value': 170,
                    'contexts': {'subject_id': 'S001', 'visit': 'V1'},
                    'user_id': 'nurse_001'
                },
                {
                    'field': 'weight',
                    'raw_value': 70,
                    'contexts': {'subject_id': 'S001', 'visit': 'V1'},
                    'user_id': 'nurse_001'
                }
            ])
        """
        pass
    
    def query(
        self,
        contexts: Dict[str, str],
        fields: Optional[List[str]] = None,
        as_of: Optional[str] = None,
        latest_only: bool = True,
        include_metadata: bool = True
    ) -> pl.DataFrame:
        """
        Query values matching context filter.
        
        Args:
            contexts: Context filter (e.g., {'subject_id': 'S001'})
            fields: Specific fields to retrieve (None = all)
            as_of: Timestamp for time-travel query (ISO format)
            latest_only: If True, return only latest value per field+context
            include_metadata: If True, include metadata column
        
        Returns:
            Polars DataFrame with columns:
                - field: str
                - raw_value: str
                - metadata: dict (if include_metadata=True)
                - reported_timestamp: datetime
                - created_timestamp: datetime
                - user_id: str
                - [context columns]: str
        
        Example:
            # Get all data for subject S001
            data = db.query(contexts={'subject_id': 'S001'})
            
            # Get specific fields for subject S001, visit V1
            data = db.query(
                contexts={'subject_id': 'S001', 'visit': 'V1'},
                fields=['height', 'weight']
            )
            
            # Time-travel query
            data = db.query(
                contexts={'subject_id': 'S001'},
                as_of='2026-01-15T00:00:00'
            )
        """
        pass
    
    def materialize_view(
        self,
        contexts: Dict[str, str],
        fields: List[str],
        expressions: Optional[Dict[str, pl.Expr]] = None,
        pivot: bool = True
    ) -> pl.DataFrame:
        """
        Materialize a traditional table view with optional expressions.
        
        Args:
            contexts: Context filter
            fields: Fields to include in view
            expressions: Dict of {name: polars_expression} for derived columns
            pivot: If True, pivot to wide format (one row per context)
        
        Returns:
            Polars DataFrame in traditional table format
        
        Example:
            # Simple view
            view = db.materialize_view(
                contexts={'subject_id': 'S001', 'visit': 'V1'},
                fields=['height', 'weight']
            )
            # Result: subject_id | visit | height | weight
            
            # View with BMI calculation
            view = db.materialize_view(
                contexts={'subject_id': 'S001', 'visit': 'V1'},
                fields=['height', 'weight'],
                expressions={
                    'bmi': pl.col('weight') / (pl.col('height')/100)**2
                }
            )
            # Result: subject_id | visit | height | weight | bmi
        """
        pass
    
    def get_history(
        self,
        field: str,
        contexts: Dict[str, str]
    ) -> pl.DataFrame:
        """
        Get full history of a value (all versions).
        
        Args:
            field: Field name
            contexts: Context filter
        
        Returns:
            Polars DataFrame with all versions, sorted by created_timestamp
        
        Example:
            # See all corrections for weight
            history = db.get_history(
                field='weight',
                contexts={'subject_id': 'S001', 'visit': 'V1'}
            )
        """
        pass
    
    def stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dict with:
                - total_values: int
                - unique_contexts: int
                - fields: List[str]
                - storage_size_mb: float
                - oldest_timestamp: str
                - newest_timestamp: str
        
        Example:
            stats = db.stats()
            print(f"Total values: {stats['total_values']}")
        """
        pass
    
    def validate_schema(self) -> Dict[str, Any]:
        """
        Validate current schema against database.
        
        Returns:
            Dict with validation results:
                - valid: bool
                - errors: List[str]
                - warnings: List[str]
        """
        pass
    
    def close(self) -> None:
        """
        Close database connection.
        
        Example:
            db.close()
            # Or use context manager:
            with YetAnotherSchema('data.db', 'schema.toml') as db:
                db.write(...)
        """
        pass
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
```

---

## 🗄️ Core Components

### `DatabaseManager`

```python
class DatabaseManager:
    """Manages DuckDB connection and schema."""
    
    def __init__(
        self,
        db_path: str,
        schema: Dict[str, Any],
        read_only: bool = False
    ) -> None:
        """Initialize database connection."""
        pass
    
    def execute(
        self,
        query: str,
        params: Optional[Dict] = None
    ) -> Any:
        """Execute SQL query."""
        pass
    
    def execute_many(
        self,
        query: str,
        params_list: List[Dict]
    ) -> None:
        """Execute query with multiple parameter sets."""
        pass
    
    def fetch_df(
        self,
        query: str,
        params: Optional[Dict] = None
    ) -> pl.DataFrame:
        """Execute query and return Polars DataFrame."""
        pass
    
    def begin_transaction(self) -> None:
        """Begin transaction."""
        pass
    
    def commit(self) -> None:
        """Commit transaction."""
        pass
    
    def rollback(self) -> None:
        """Rollback transaction."""
        pass
    
    def close(self) -> None:
        """Close connection."""
        pass
```

### `ValueStore`

```python
class ValueStore:
    """Inner Sphere: Manages atomic values."""
    
    def __init__(self, db_manager: DatabaseManager) -> None:
        """Initialize value store."""
        pass
    
    def add_value(
        self,
        field: str,
        raw_value: Any,
        metadata: Dict[str, Any],
        user_id: str,
        reported_timestamp: Optional[str] = None
    ) -> int:
        """
        Add a value to the database.
        
        Returns:
            value_id
        """
        pass
    
    def add_values_batch(
        self,
        values: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Add multiple values in batch.
        
        Returns:
            List of value_ids
        """
        pass
    
    def get_values(
        self,
        value_ids: List[int]
    ) -> pl.DataFrame:
        """
        Get values by IDs.
        
        Returns:
            Polars DataFrame
        """
        pass
    
    def get_values_by_field(
        self,
        field: str,
        as_of: Optional[str] = None
    ) -> pl.DataFrame:
        """
        Get all values for a field.
        
        Returns:
            Polars DataFrame
        """
        pass
```

### `RelationshipStore`

```python
class RelationshipStore:
    """Middle Sphere: Manages context relationships."""
    
    def __init__(self, db_manager: DatabaseManager) -> None:
        """Initialize relationship store."""
        pass
    
    def add_relationship(
        self,
        context_key: str,
        field: str,
        value_id: int
    ) -> int:
        """
        Add a context → value relationship.
        
        Returns:
            relationship_id
        """
        pass
    
    def add_relationships_batch(
        self,
        relationships: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Add multiple relationships in batch.
        
        Returns:
            List of relationship_ids
        """
        pass
    
    def get_value_ids(
        self,
        context_filter: Dict[str, str],
        fields: Optional[List[str]] = None
    ) -> pl.DataFrame:
        """
        Get value IDs matching context filter.
        
        Returns:
            Polars DataFrame with columns:
                - context_key: str
                - field: str
                - value_id: int
        """
        pass
    
    def get_contexts(
        self,
        value_id: int
    ) -> List[Dict[str, str]]:
        """
        Get all contexts for a value.
        
        Returns:
            List of context dicts
        """
        pass
```

### `QueryEngine`

```python
class QueryEngine:
    """High-level query interface."""
    
    def __init__(
        self,
        value_store: ValueStore,
        relationship_store: RelationshipStore,
        expression_engine: ExpressionEngine
    ) -> None:
        """Initialize query engine."""
        pass
    
    def query(
        self,
        contexts: Dict[str, str],
        fields: Optional[List[str]] = None,
        as_of: Optional[str] = None,
        latest_only: bool = True,
        include_metadata: bool = True
    ) -> pl.DataFrame:
        """
        Query values with context filter.
        
        Returns:
            Polars DataFrame
        """
        pass
    
    def materialize_view(
        self,
        contexts: Dict[str, str],
        fields: List[str],
        expressions: Optional[Dict[str, pl.Expr]] = None,
        pivot: bool = True
    ) -> pl.DataFrame:
        """
        Materialize traditional table view.
        
        Returns:
            Polars DataFrame
        """
        pass
    
    def get_history(
        self,
        field: str,
        contexts: Dict[str, str]
    ) -> pl.DataFrame:
        """
        Get full history of a value.
        
        Returns:
            Polars DataFrame sorted by created_timestamp
        """
        pass
```

### `ExpressionEngine`

```python
class ExpressionEngine:
    """Outer Sphere: Evaluates expressions using Polars."""
    
    def __init__(self) -> None:
        """Initialize expression engine."""
        pass
    
    def register_expression(
        self,
        name: str,
        expr: pl.Expr
    ) -> None:
        """
        Register a named Polars expression.
        
        Example:
            engine.register_expression(
                'bmi',
                pl.col('weight') / (pl.col('height')/100)**2
            )
        """
        pass
    
    def evaluate(
        self,
        expr_name: str,
        data: pl.DataFrame
    ) -> pl.Series:
        """
        Evaluate registered expression on data.
        
        Returns:
            Polars Series with results
        """
        pass
    
    def evaluate_multiple(
        self,
        expr_names: List[str],
        data: pl.DataFrame
    ) -> pl.DataFrame:
        """
        Evaluate multiple expressions.
        
        Returns:
            Polars DataFrame with new columns
        """
        pass
```

---

## 🛠️ Utility Functions

### `schema_validator.py`

```python
def load_schema(schema_path: str) -> Dict[str, Any]:
    """
    Load and validate TOML schema.
    
    Args:
        schema_path: Path to schema.toml
    
    Returns:
        Validated schema dict
    
    Raises:
        SchemaValidationError: If schema is invalid
    """
    pass

def validate_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate schema structure.
    
    Returns:
        Dict with validation results
    """
    pass

def validate_contexts(
    contexts: Dict[str, str],
    schema: Dict[str, Any]
) -> None:
    """
    Validate contexts against schema.
    
    Raises:
        ValidationError: If required contexts are missing
    """
    pass
```

### `context_parser.py`

```python
def build_context_key(contexts: Dict[str, str]) -> str:
    """
    Build a unique key from contexts.
    
    Args:
        contexts: {'subject_id': 'S001', 'visit': 'V1'}
    
    Returns:
        'subject_id=S001,visit=V1' (sorted)
    """
    pass

def parse_context_key(context_key: str) -> Dict[str, str]:
    """
    Parse context key back to dict.
    
    Args:
        context_key: 'subject_id=S001,visit=V1'
    
    Returns:
        {'subject_id': 'S001', 'visit': 'V1'}
    """
    pass

def match_context_filter(
    context_key: str,
    context_filter: Dict[str, str]
) -> bool:
    """
    Check if context key matches filter.
    
    Returns:
        True if all filter items match
    """
    pass
```

### `type_converter.py`

```python
def value_to_string(value: Any) -> str:
    """
    Convert value to string for storage.
    
    Handles: int, float, str, bool, None, datetime
    """
    pass

def string_to_value(
    value_str: str,
    value_type: str
) -> Any:
    """
    Convert string back to typed value.
    
    Args:
        value_str: Stored string
        value_type: 'numeric', 'text', 'boolean', 'datetime'
    
    Returns:
        Typed value
    """
    pass

def parse_metadata(metadata_json: str) -> Dict[str, Any]:
    """Parse JSON metadata string."""
    pass

def serialize_metadata(metadata: Dict[str, Any]) -> str:
    """Serialize metadata to JSON string."""
    pass
```

---

## 🎯 Usage Examples

### Example 1: Basic Write and Query

```python
from yetanotherschema import YetAnotherSchema

# Initialize
db = YetAnotherSchema(
    db_path='clinical_study.db',
    schema_path='schema.toml'
)

# Write data
db.write(
    field='height',
    raw_value=170,
    contexts={'subject_id': 'S001', 'visit': 'V1'},
    user_id='nurse_001'
)

# Query
data = db.query(contexts={'subject_id': 'S001'})
print(data)

db.close()
```

### Example 2: Batch Write

```python
# Batch write for performance
records = [
    {
        'field': 'height',
        'raw_value': 170,
        'contexts': {'subject_id': 'S001', 'visit': 'V1'},
        'user_id': 'nurse_001'
    },
    {
        'field': 'weight',
        'raw_value': 70,
        'contexts': {'subject_id': 'S001', 'visit': 'V1'},
        'user_id': 'nurse_001'
    }
]

value_ids = db.write_batch(records)
```

### Example 3: Materialize View with Expressions

```python
import polars as pl

# Materialize view with BMI calculation
view = db.materialize_view(
    contexts={'subject_id': 'S001', 'visit': 'V1'},
    fields=['height', 'weight'],
    expressions={
        'bmi': pl.col('weight') / (pl.col('height')/100)**2,
        'bmi_category': pl.when(pl.col('bmi') < 18.5).then('Underweight')
                         .when(pl.col('bmi') < 25).then('Normal')
                         .when(pl.col('bmi') < 30).then('Overweight')
                         .otherwise('Obese')
    }
)

print(view)
```

### Example 4: Time-Travel Query

```python
# Query data as it was on a specific date
historical_data = db.query(
    contexts={'subject_id': 'S001'},
    as_of='2026-01-15T00:00:00'
)
```

### Example 5: Context Manager

```python
# Use context manager for automatic cleanup
with YetAnotherSchema('data.db', 'schema.toml') as db:
    db.write(...)
    data = db.query(...)
# Automatically closed
```

---

## 📊 Return Types Summary

| Method | Returns |
|--------|---------|
| `write()` | `int` (value_id) |
| `write_batch()` | `List[int]` (value_ids) |
| `query()` | `pl.DataFrame` |
| `materialize_view()` | `pl.DataFrame` |
| `get_history()` | `pl.DataFrame` |
| `stats()` | `Dict[str, Any]` |
| `validate_schema()` | `Dict[str, Any]` |

---

**Total Functions:** ~30  
**Main API Functions:** 10  
**Core Component Functions:** 15  
**Utility Functions:** 5

Does this API look good to you? Any changes you'd like before we start implementation?
