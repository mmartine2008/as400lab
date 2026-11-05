
CREATE TABLE IF NOT EXISTS ibmi_libraries (
    id BIGSERIAL PRIMARY KEY,
    library_name VARCHAR(10) NOT NULL UNIQUE,
    description VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ibmi_objects (
    id BIGSERIAL PRIMARY KEY,
    library_id BIGINT NOT NULL REFERENCES ibmi_libraries(id),
    object_name VARCHAR(10) NOT NULL,
    object_type VARCHAR(10) NOT NULL,
    description VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(library_id, object_name, object_type)
);

CREATE TABLE IF NOT EXISTS ibmi_jobs (
    id BIGSERIAL PRIMARY KEY,
    job_name VARCHAR(10) NOT NULL,
    user_name VARCHAR(10) NOT NULL DEFAULT 'MARIANO',
    job_type VARCHAR(10) NOT NULL DEFAULT 'INTERACTIVE',
    status VARCHAR(15) NOT NULL DEFAULT 'ACTIVE',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initial system libraries

INSERT INTO ibmi_libraries (library_name, description)
VALUES
    ('QSYS', 'System library'),
    ('QGPL', 'General purpose library'),
    ('QTEMP', 'Temporary library')
ON CONFLICT (library_name) DO NOTHING;

