"""
YetAnotherSchema - Example Usage
Demonstrates real-world clinical research scenario
"""

import yetanotherschema as ys
import os
from pathlib import Path


def clinical_research_example():
    """
    Example: Clinical Research Study
    
    Scenario:
    - Multi-site clinical trial
    - Collecting vital signs and lab results
    - Data corrections needed
    - Time-travel queries for audit
    """
    
    # Clean up
    test_db = Path('./clinical_trial_001.db')
    if test_db.exists():
        os.remove(test_db)
    
    print("=" * 70)
    print("YetAnotherSchema - Clinical Research Example")
    print("=" * 70)
    
    # Step 1: Create the space
    print("\n📋 Step 1: Create clinical trial space")
    print("-" * 70)
    
    result = ys.create(
        space_name='clinical_trial_001',
        schema_path='schema_example.toml'
    )
    
    print(f"✓ Created space: {result['space_name']}")
    print(f"  Storage: {result['storage_path']}")
    print(f"  Schema version: {result['schema_version']}")
    
    # Step 2: Collect baseline data
    print("\n📝 Step 2: Collect baseline data (Visit 1)")
    print("-" * 70)
    
    # Subject S001 - Site Boston
    ys.write(
        space_name='clinical_trial_001',
        field='height',
        value={
            'raw_value': 170,
            'metadata': {
                'unit': 'cm',
                'device': 'stadiometer_model_x',
                'site': 'Boston'
            },
            'reported_timestamp': '2026-01-15T09:00:00',
            'user_id': 'nurse_boston_001'
        },
        contexts={
            'subject_id': 'S001',
            'visit': 'V1',
            'site': 'Boston'
        }
    )
    
    ys.write(
        space_name='clinical_trial_001',
        field='weight',
        value={
            'raw_value': 70,
            'metadata': {
                'unit': 'kg',
                'device': 'scale_model_y',
                'site': 'Boston'
            },
            'reported_timestamp': '2026-01-15T09:05:00',
            'user_id': 'nurse_boston_001'
        },
        contexts={
            'subject_id': 'S001',
            'visit': 'V1',
            'site': 'Boston'
        }
    )
    
    print("✓ S001 baseline data collected (Boston)")
    
    # Subject S002 - Site New York
    ys.write_batch(
        space_name='clinical_trial_001',
        records=[
            {
                'field': 'height',
                'value': {
                    'raw_value': 165,
                    'metadata': {'unit': 'cm', 'site': 'New York'},
                    'reported_timestamp': '2026-01-15T10:00:00',
                    'user_id': 'nurse_ny_001'
                },
                'contexts': {'subject_id': 'S002', 'visit': 'V1', 'site': 'New York'}
            },
            {
                'field': 'weight',
                'value': {
                    'raw_value': 60,
                    'metadata': {'unit': 'kg', 'site': 'New York'},
                    'reported_timestamp': '2026-01-15T10:05:00',
                    'user_id': 'nurse_ny_001'
                },
                'contexts': {'subject_id': 'S002', 'visit': 'V1', 'site': 'New York'}
            }
        ]
    )
    
    print("✓ S002 baseline data collected (New York)")
    
    # Step 3: Data correction scenario
    print("\n🔧 Step 3: Data correction (typo fix)")
    print("-" * 70)
    
    print("  Original entry: S001 weight = 700 kg (typo!)")
    ys.write(
        space_name='clinical_trial_001',
        field='weight',
        value={
            'raw_value': 700,  # Typo!
            'metadata': {'unit': 'kg', 'note': 'data_entry_error'},
            'reported_timestamp': '2026-01-20T09:00:00',
            'user_id': 'nurse_boston_001'
        },
        contexts={'subject_id': 'S001', 'visit': 'V2', 'site': 'Boston'}
    )
    
    import time
    time.sleep(0.1)  # Ensure different timestamp
    
    print("  Corrected entry: S001 weight = 72 kg")
    ys.write(
        space_name='clinical_trial_001',
        field='weight',
        value={
            'raw_value': 72,  # Corrected
            'metadata': {'unit': 'kg', 'note': 'corrected_typo'},
            'reported_timestamp': '2026-01-20T09:00:00',  # Same reported time
            'user_id': 'nurse_boston_001'
        },
        contexts={'subject_id': 'S001', 'visit': 'V2', 'site': 'Boston'}
    )
    
    print("✓ Data correction completed (both values preserved)")
    
    # Step 4: Query current data
    print("\n📊 Step 4: Query current data (latest values)")
    print("-" * 70)
    
    df = ys.read(
        space_name='clinical_trial_001',
        fields=['subject_id', 'visit', 'site', 'height', 'weight']
    )
    
    print(f"✓ Retrieved {len(df)} records")
    print("\nCurrent data:")
    print(df)
    
    # Step 5: Site-specific query
    print("\n🏥 Step 5: Site-specific query (Boston only)")
    print("-" * 70)
    
    df_boston = ys.read(
        space_name='clinical_trial_001',
        fields=['subject_id', 'visit', 'height', 'weight'],
        contexts={'site': 'Boston'}
    )
    
    print(f"✓ Retrieved {len(df_boston)} records from Boston")
    print("\nBoston data:")
    print(df_boston)
    
    # Step 6: Filter by value
    print("\n🔍 Step 6: Filter by value (weight > 65 kg)")
    print("-" * 70)
    
    df_filtered = ys.read(
        space_name='clinical_trial_001',
        fields=['subject_id', 'visit', 'weight'],
        filters={'weight': {'gt': 65}}
    )
    
    print(f"✓ Found {len(df_filtered)} subjects with weight > 65 kg")
    print("\nFiltered data:")
    print(df_filtered)
    
    # Step 7: Add lab results
    print("\n🧪 Step 7: Add lab results")
    print("-" * 70)
    
    ys.write(
        space_name='clinical_trial_001',
        field='hemoglobin',
        value={
            'raw_value': 14.5,
            'metadata': {
                'unit': 'g/dL',
                'lab': 'Central_Lab',
                'reference_range': '12.0-16.0'
            },
            'reported_timestamp': '2026-01-15T14:00:00',
            'user_id': 'lab_tech_001'
        },
        contexts={
            'subject_id': 'S001',
            'visit': 'V1',
            'site': 'Boston'
        }
    )
    
    print("✓ Lab result added for S001")
    
    # Step 8: Comprehensive query
    print("\n📈 Step 8: Comprehensive query (all data for S001)")
    print("-" * 70)
    
    df_s001 = ys.read(
        space_name='clinical_trial_001',
        fields=['subject_id', 'visit', 'height', 'weight', 'hemoglobin'],
        contexts={'subject_id': 'S001'}
    )
    
    print(f"✓ Retrieved {len(df_s001)} visits for S001")
    print("\nS001 complete data:")
    print(df_s001)
    
    # Step 9: View schema and statistics
    print("\n📋 Step 9: View schema and statistics")
    print("-" * 70)
    
    stats = ys.schema('clinical_trial_001', detail='stats')
    print(f"✓ Total values: {stats['total_values']}")
    print(f"✓ Unique contexts: {stats['unique_contexts']}")
    print(f"✓ Value fields: {stats['value_fields']}")
    
    schema_info = ys.schema('clinical_trial_001', detail='summary')
    print(f"\n✓ Required contexts: {schema_info['contexts']['required']}")
    print(f"✓ Optional contexts: {schema_info['contexts']['optional']}")
    print(f"✓ Available fields: {schema_info['value_fields']}")
    
    # Step 10: List all spaces
    print("\n📂 Step 10: List all spaces")
    print("-" * 70)
    
    spaces = ys.list_spaces()
    print(f"✓ Found {len(spaces)} space(s):")
    for space in spaces:
        print(f"  - {space['space_name']}: {space['total_values']} values")
    
    print("\n" + "=" * 70)
    print("✅ Example completed successfully!")
    print("=" * 70)
    
    print("\n💡 Key Features Demonstrated:")
    print("  1. Space creation with schema")
    print("  2. Single and batch writes")
    print("  3. Data corrections (append-only)")
    print("  4. Context filtering (site, subject, visit)")
    print("  5. Value filtering (weight > 65)")
    print("  6. Multi-field queries")
    print("  7. Schema inspection")
    print("  8. Statistics")
    
    print("\n🎯 Philosophy: 'Values are free ions, not tables.'")
    print("   - No data duplication")
    print("   - Full audit trail")
    print("   - On-demand views")
    print("   - Append-only corrections")
    
    # Clean up
    if test_db.exists():
        os.remove(test_db)
        print("\n✓ Test database cleaned up")


if __name__ == '__main__':
    clinical_research_example()
