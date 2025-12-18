-- Admin Dummy Data Insert
-- This script seeds the admin database with sample data

-- Insert Admin users
-- Password for all admins: 'admin123' (hashed using bcrypt)
INSERT INTO admin (username, email, password_hash, created_at, updated_at) VALUES
('admin', 'admin@crmbackend.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/UZj.C', NOW(), NOW()),
('superadmin', 'superadmin@crmbackend.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/UZj.C', NOW(), NOW()),
('devadmin', 'devadmin@crmbackend.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/UZj.C', NOW(), NOW())
ON CONFLICT (email) DO NOTHING;
