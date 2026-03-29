# YetAnotherSchema - DuckDB + Polars MVP Design

**Version:** 0.1.0  
**Status:** Design Phase  
**Target:** Production-ready semantic database

---

## 🎯 MVP Goals

1. **Persistent Storage** - DuckDB for ACID compliance
2. **Vectorized Operations** - Polars for performance
3. **Scale Testing** - 10,000+ values, 10+ categories
4. **Production API** - Clean, documented interface
5. **Performance Benchmarks** - Measure vs traditional approaches

---

## 🏗️ Architecture

### Three-Sphere Model (Persistent)

```
┌─────────────────────────────────────────────────────────────┐
│                    YetAnotherSchema                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Outer Sphere: Expressions (Computed)                │  │
│  │  - BMI, derived metrics                              │  │
│  │  - Polars expressions                                │  │
│  │  - Never materialized                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ▲                                  │
│                          │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Middle Sphere: Relationships (DuckDB)               │  │
│  │  - context_relationships table                       │  │
│  │  - Indexed for fast lookups                          │  │
│  │  - Maps contexts → value indices                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ▲                                  │
│                          │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Inner Sphere: Values (DuckDB)                       │  │
│  │  - values table (append-only)                        │  │
│  │  - Columnar storage                                  │  │
│  │  - Full audit trail                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 DuckDB Schema

### Table 1: `values` (Inner Sphere)

```sql
CREATE TABLE values (
    value_id INTEGER PRIMARY KEY,
    field_name VARCHAR NOT NULL,
    raw_value VARCHAR NOT NULL,  -- Store as string, parse on read
    metadata JSON,                -- {unit: "kg", custom: "value"}
    reported_timestamp TIMESTAMP,
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_values_field ON values(field_name);
CREATE INDEX idx_values_created ON values(created_timestamp);
```

### Table 2: `context_relationships` (Middle Sphere)

```sql
CREATE TABLE context_relationships (
    relationship_id INTEGER PRIMARY KEY,
    context_key VARCHAR NOT NULL,     -- "subject_id=S001,visit=V1"
    field_name VARCHAR NOT NULL,
    value_id INTEGER NOT NULL,
    created_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (value_id) REFERENCES values(value_id)
);

-- Indexes for fast lookups
CREATE INDEX idx_rel_context ON context_relationships(context_key);
CREATE INDEX idx_rel_field ON context_relationships(field_name);
CREATE INDEX idx_rel_value ON context_relationships(value_id);
CREATE INDEX idx_rel_composite ON context_relationships(context_key, field_name);
```

### Table 3: `schema_metadata` (Configuration)

```sql
CREATE TABLE schema_metadata (
    key VARCHAR PRIMARY KEY,
    value JSON NOT NULL,
    updated_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Store schema definition
INSERT INTO schema_metadata VALUES 
    ('contexts', '{"required": ["subject_id"], "optional": ["visit_name"]}'),
    ('hierarchies', '{"geographic": ["region", "country", "site"]}'),
    ('values', '{"height": {"unit": "cm", "type": "numeric"}}'),
    ('null_values', '{"not_done": "@notdone", "missing": "@null"}');
```

---

## 🔧 Core Components

### 1. Database Manager (`db_manager.py`)

```python
class DatabaseManager:
    """Manages DuckDB connection and schema"""
    
    def __init__(self, db_path: str, schema_path: str):
        self.conn = duckdb.connect(db_path)
        self.schema = self._load_schema(schema_path)
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Create tables if they don't exist"""
        pass
    
    def close(self):
        """Close database connection"""
        self.conn.close()
```

### 2. Value Store (`value_store.py`)

```python
class ValueStore:
    """Inner Sphere: Manages atomic values"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def add_value(
        self,
        field: str,
        raw_value: Any,
        metadata: Dict,
        user_id: str,
        reported_timestamp: Optional[str] = None
    ) -> int:
        """
        Add value to DuckDB.
        Returns value_id.
        """
        pass
    
    def get_values(
        self,
        field: str,
        value_ids: Optional[List[int]] = None
    ) -> pl.DataFrame:
        """
        Get values as Polars DataFrame.
        Vectorized operation.
        """
        pass
```

### 3. Relationship Store (`relationship_store.py`)

```python
class RelationshipStore:
    """Middle Sphere: Manages context relationships"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def add_relationship(
        self,
        context_key: str,
        field: str,
        value_id: int
    ):
        """Add context → value mapping"""
        pass
    
    def get_value_ids(
        self,
        context_filter: Dict[str, str],
        fields: Optional[List[str]] = None
    ) -> pl.DataFrame:
        """
        Get value IDs matching context filter.
        Returns Polars DataFrame with context_key, field, value_id.
        """
        pass
```

### 4. Expression Engine (`expression_engine.py`)

```python
class ExpressionEngine:
    """Outer Sphere: Evaluates expressions using Polars"""
    
    def __init__(self):
        self.expressions = {}
    
    def register_expression(self, name: str, expr: pl.Expr):
        """Register a Polars expression"""
        self.expressions[name] = expr
    
    def evaluate(
        self,
        expr_name: str,
        data: pl.DataFrame
    ) -> pl.Series:
        """Evaluate expression on data"""
        pass
```

### 5. Query Engine (`query_engine.py`)

```python
class QueryEngine:
    """High-level query interface"""
    
    def __init__(
        self,
        value_store: ValueStore,
        relationship_store: RelationshipStore,
        expression_engine: ExpressionEngine
    ):
        self.values = value_store
        self.relationships = relationship_store
        self.expressions = expression_engine
    
    def query(
        self,
        contexts: Dict[str, str],
        fields: Optional[List[str]] = None,
        as_of: Optional[str] = None,
        latest_only: bool = True
    ) -> pl.DataFrame:
        """
        Query values with context filter.
        Returns Polars DataFrame.
        """
        pass
    
    def materialize_view(
        self,
        contexts: Dict[str, str],
        fields: List[str],
        expressions: Optional[Dict[str, pl.Expr]] = None
    ) -> pl.DataFrame:
        """
        Materialize traditional table view.
        Returns Polars DataFrame.
        """
        pass
```

### 6. Main API (`yetanotherschema.py`)

```python
class YetAnotherSchema:
    """Main database interface"""
    
    def __init__(self, db_path: str, schema_path: str):
        self.db_manager = DatabaseManager(db_path, schema_path)
        self.value_store = ValueStore(self.db_manager)
        self.relationship_store = RelationshipStore(self.db_manager)
        self.expression_engine = ExpressionEngine()
        self.query_engine = QueryEngine(
            self.value_store,
            self.relationship_store,
            self.expression_engine
        )
    
    def write(self, field: str, raw_value: Any, contexts: Dict, user_id: str, **kwargs):
        """Write a value"""
        pass
    
    def query(self, contexts: Dict, **kwargs) -> pl.DataFrame:
        """Query values"""
        return self.query_engine.query(contexts, **kwargs)
    
    def materialize_view(self, contexts: Dict, fields: List, expressions: Dict = None) -> pl.DataFrame:
        """Materialize view"""
        return self.query_engine.materialize_view(contexts, fields, expressions)
    
    def close(self):
        """Close database"""
        self.db_manager.close()
```

---

## 🚀 Performance Optimizations

### 1. Batch Writes
```python
def write_batch(self, records: List[Dict]):
    """
    Batch insert for performance.
    Use DuckDB's bulk insert capabilities.
    """
    pass
```

### 2. Indexed Queries
- Composite index on `(context_key, field_name)`
- Separate indexes on frequently queried columns
- DuckDB's columnar storage for fast scans

### 3. Polars Vectorization
- Use Polars expressions for all computations
- Lazy evaluation where possible
- Zero-copy operations with DuckDB

### 4. Query Caching (Optional)
```python
class QueryCache:
    """LRU cache for frequent queries"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
    
    def get(self, query_key: str) -> Optional[pl.DataFrame]:
        pass
    
    def set(self, query_key: str, result: pl.DataFrame):
        pass
```

---

## 📦 Package Structure

```
yetanotherschema/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── db_manager.py
│   ├── value_store.py
│   ├── relationship_store.py
│   ├── expression_engine.py
│   └── query_engine.py
├── api/
│   ├── __init__.py
│   └── yetanotherschema.py
├── utils/
│   ├── __init__.py
│   ├── schema_validator.py
│   ├── context_parser.py
│   └── type_converter.py
├── tests/
│   ├── __init__.py
│   ├── test_value_store.py
│   ├── test_relationship_store.py
│   ├── test_query_engine.py
│   └── test_performance.py
└── examples/
    ├── clinical_research.py
    ├── iot_sensors.py
    └── finance_trading.py
```

---

## 🧪 Testing Strategy

### Unit Tests
- Each component tested independently
- Mock DuckDB for fast tests
- Polars DataFrame validation

### Integration Tests
- Full write → query → materialize flow
- Multiple contexts and fields
- Data correction scenarios

### Performance Tests
```python
def test_write_performance():
    """Benchmark: 10,000 writes"""
    pass

def test_query_performance():
    """Benchmark: Complex multi-context queries"""
    pass

def test_view_materialization():
    """Benchmark: Large view with expressions"""
    pass
```

### Comparison Tests
```python
def test_vs_traditional_db():
    """
    Compare:
    - Storage size
    - Query time
    - Transformation time
    """
    pass
```

---

## 📊 Benchmarks to Collect

1. **Write Performance**
   - Single write: < 1ms
   - Batch write (1000): < 100ms
   - Batch write (10,000): < 1s

2. **Query Performance**
   - Simple query (1 context): < 10ms
   - Complex query (3 contexts): < 50ms
   - Full scan (10,000 values): < 500ms

3. **View Materialization**
   - Small view (100 values): < 20ms
   - Medium view (1,000 values): < 100ms
   - Large view (10,000 values): < 1s

4. **Storage Efficiency**
   - Compare to traditional DB with duplicated data
   - Measure compression ratio
   - Track index overhead

---

## 🔄 Migration from PoC

### Step 1: Port Core Logic
- [x] Value store (Pandas → DuckDB)
- [x] Relationship store (Pandas → DuckDB)
- [x] Query engine (Pandas → Polars)

### Step 2: Add Persistence
- [x] DuckDB schema creation
- [x] Transaction handling
- [x] Connection management

### Step 3: Optimize
- [x] Batch operations
- [x] Indexed queries
- [x] Polars vectorization

### Step 4: Test & Benchmark
- [x] Unit tests
- [x] Integration tests
- [x] Performance benchmarks

---

## 🎯 Success Criteria

1. ✅ **Functionality**: All PoC features work with DuckDB + Polars
2. ✅ **Performance**: Handles 10,000+ values efficiently
3. ✅ **Persistence**: Data survives restarts
4. ✅ **API**: Clean, documented interface
5. ✅ **Tests**: >90% coverage
6. ✅ **Benchmarks**: Documented performance characteristics

---

## 📝 Next Steps

1. **Implement Core** (Day 1)
   - DatabaseManager
   - ValueStore with DuckDB
   - RelationshipStore with DuckDB

2. **Implement Query** (Day 2)
   - QueryEngine with Polars
   - ExpressionEngine with Polars
   - Main API

3. **Test & Benchmark** (Day 3)
   - Unit tests
   - Integration tests
   - Performance benchmarks
   - Comparison with PoC

4. **Documentation** (Day 3)
   - API documentation
   - Usage examples
   - Performance guide

---

**Status:** 📋 Design Complete  
**Next:** Implementation  
**Estimated Effort:** 3 days
