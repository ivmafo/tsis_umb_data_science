CREATE TABLE file_processing_control (
    id SERIAL PRIMARY KEY,
    file_name TEXT NOT NULL,
    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);