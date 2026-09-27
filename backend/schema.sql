-- data_source_registry
CREATE TABLE data_source_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name VARCHAR(255) NOT NULL,
    dataset_name VARCHAR(255),
    parameter VARCHAR(255),
    coverage_type VARCHAR(255),
    geographic_coverage JSONB,
    temporal_coverage VARCHAR(255),
    update_frequency VARCHAR(255),
    ingestion_method VARCHAR(255),
    endpoint_or_dataset_reference TEXT,
    priority INTEGER,
    authority_level VARCHAR(255),
    last_successful_update TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50),
    is_available BOOLEAN DEFAULT TRUE
);

-- sar_incidents
CREATE TABLE sar_incidents (
    incident_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_type VARCHAR(100),
    object_type VARCHAR(100),
    people_count INTEGER,
    vessel_id VARCHAR(100),
    last_known_lat DOUBLE PRECISION,
    last_known_lon DOUBLE PRECISION,
    last_known_time TIMESTAMP WITH TIME ZONE,
    delivery_channel VARCHAR(100),
    severity VARCHAR(50),
    status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- marine_observations
CREATE TABLE marine_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(255),
    parameter VARCHAR(255),
    value DOUBLE PRECISION,
    unit VARCHAR(50),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    valid_time TIMESTAMP WITH TIME ZONE,
    retrieved_at TIMESTAMP WITH TIME ZONE,
    confidence DOUBLE PRECISION,
    is_stale BOOLEAN,
    conflict_flag BOOLEAN
);
