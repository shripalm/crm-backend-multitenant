-- Client Database Dummy Data Insert
-- This script seeds client databases with sample data
-- Password for all users: 'password123' (hashed using bcrypt)

-- Insert Permissions
INSERT INTO permissions (id, name, label, description, created_at) VALUES
('11111111-1111-1111-1111-111111111111', 'create_user', 'Create User', 'Permission to create new users', NOW()),
('22222222-2222-2222-2222-222222222222', 'edit_user', 'Edit User', 'Permission to edit user details', NOW()),
('33333333-3333-3333-3333-333333333333', 'delete_user', 'Delete User', 'Permission to delete users', NOW()),
('44444444-4444-4444-4444-444444444444', 'view_users', 'View Users', 'Permission to view user list', NOW()),
('55555555-5555-5555-5555-555555555555', 'create_project', 'Create Project', 'Permission to create new projects', NOW()),
('66666666-6666-6666-6666-666666666666', 'edit_project', 'Edit Project', 'Permission to edit project details', NOW()),
('77777777-7777-7777-7777-777777777777', 'delete_project', 'Delete Project', 'Permission to delete projects', NOW()),
('88888888-8888-8888-8888-888888888888', 'view_projects', 'View Projects', 'Permission to view project list', NOW()),
('99999999-9999-9999-9999-999999999999', 'manage_contacts', 'Manage Contacts', 'Permission to manage contacts', NOW()),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'manage_tasks', 'Manage Tasks', 'Permission to manage tasks', NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert Roles
INSERT INTO roles (id, name, description, created_at) VALUES
('10000000-0000-0000-0000-000000000001', 'presales', 'Presales team member with basic access', NOW()),
('10000000-0000-0000-0000-000000000002', 'sales', 'Sales team member with basic access', NOW()),
('10000000-0000-0000-0000-000000000003', 'sitevisit', 'Site visit team member with basic access', NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert Role-Permission Mappings
-- NOTE: We must generate IDs explicitly because the table definition lacks a server_default for ID
INSERT INTO role_permissions (id, role_id, permission_id) VALUES
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000001', '22222222-2222-2222-2222-222222222222'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000001', '33333333-3333-3333-3333-333333333333'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000001', '44444444-4444-4444-4444-444444444444'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000001', '55555555-5555-5555-5555-555555555555'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000001', '66666666-6666-6666-6666-666666666666'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000001', '77777777-7777-7777-7777-777777777777'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000001', '88888888-8888-8888-8888-888888888888'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000001', '99999999-9999-9999-9999-999999999999'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000001', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000002', '44444444-4444-4444-4444-444444444444'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000002', '55555555-5555-5555-5555-555555555555'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000002', '66666666-6666-6666-6666-666666666666'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000002', '88888888-8888-8888-8888-888888888888'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000002', '99999999-9999-9999-9999-999999999999'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000002', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000003', '88888888-8888-8888-8888-888888888888'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000003', '99999999-9999-9999-9999-999999999999'),
(uuid_generate_v4(), '10000000-0000-0000-0000-000000000003', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Insert Users
INSERT INTO users (id, email, full_name, password_hash, team_name, active, created_at, updated_at) VALUES
('20000000-0000-0000-0000-000000000001', 'john.presales@example.com', 'John Presales', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/UZj.C', 'presales', true, NOW(), NOW()),
('20000000-0000-0000-0000-000000000002', 'sarah.sales@example.com', 'Sarah Sales', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/UZj.C', 'sales ', true, NOW(), NOW()),
('20000000-0000-0000-0000-000000000003', 'mike.sales@example.com', 'Mike Sales', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/UZj.C', 'presales', true, NOW(), NOW()),
('20000000-0000-0000-0000-000000000004', 'lisa.sales@example.com', 'Lisa Sales', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/UZj.C', 'sales', true, NOW(), NOW()),
('20000000-0000-0000-0000-000000000005', 'david.sitevisit@example.com', 'David sitevisit', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/UZj.C', 'sitevisit', true, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert User-Role Mappings
INSERT INTO user_roles (id, user_id, role_id) VALUES
(uuid_generate_v4(), '20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001'),
(uuid_generate_v4(), '20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002'),
(uuid_generate_v4(), '20000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003'),
(uuid_generate_v4(), '20000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000003')
ON CONFLICT (user_id, role_id) DO NOTHING;

-- Insert Projects
INSERT INTO projects (id, name, developer, location, start_date, end_date, meta, is_deleted, created_at, updated_at) VALUES
('30000000-0000-0000-0000-000000000001', 'Green Valley Residency', 'ABC Developers', 'Bangalore, Karnataka', '2024-01-01', '2025-12-31', '{"total_units": 200, "amenities": ["Swimming Pool", "Gym", "Garden"]}', false, NOW(), NOW()),
('30000000-0000-0000-0000-000000000002', 'Silver Heights Tower', 'XYZ Constructions', 'Mumbai, Maharashtra', '2024-06-01', '2026-06-30', '{"total_units": 150, "amenities": ["Clubhouse", "Parking", "Security"]}', false, NOW(), NOW()),
('30000000-0000-0000-0000-000000000003', 'Ocean View Apartments', 'Coastal Realty', 'Goa', '2024-03-15', '2025-09-30', '{"total_units": 80, "amenities": ["Sea View", "Garden", "Kids Play Area"]}', false, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert Properties
INSERT INTO properties (id, project_id, unit_number, size, price, status, attributes, is_deleted, created_at, updated_at) VALUES
('40000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', 'A-101', 1250.00, 8500000, 'available', '{"bedrooms": 2, "bathrooms": 2, "floor": 1, "facing": "East"}', false, NOW(), NOW()),
('40000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', 'A-102', 1450.00, 9800000, 'booked', '{"bedrooms": 3, "bathrooms": 2, "floor": 1, "facing": "West"}', false, NOW(), NOW()),
('40000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000001', 'B-201', 1850.00, 12500000, 'available', '{"bedrooms": 3, "bathrooms": 3, "floor": 2, "facing": "North"}', false, NOW(), NOW()),
('40000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000002', 'T1-501', 980.00, 15000000, 'available', '{"bedrooms": 2, "bathrooms": 2, "floor": 5, "facing": "South"}', false, NOW(), NOW()),
('40000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000002', 'T1-502', 1200.00, 18000000, 'sold', '{"bedrooms": 2, "bathrooms": 2, "floor": 5, "facing": "East"}', false, NOW(), NOW()),
('40000000-0000-0000-0000-000000000006', '30000000-0000-0000-0000-000000000003', 'OV-101', 1600.00, 22000000, 'available', '{"bedrooms": 3, "bathrooms": 3, "floor": 1, "facing": "Sea"}', false, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert Contacts
INSERT INTO contacts (id, name, email, contact_no, city, state, source, project_name, property_type, budget_range, created_at, updated_at) VALUES
('50000000-0000-0000-0000-000000000001', 'Rajesh Kumar', 'rajesh.kumar@example.com', '9876543210', 'Bangalore', 'Karnataka', 'Website', 'Green Valley Residency', 'Apartment', '80L-1Cr', NOW(), NOW()),
('50000000-0000-0000-0000-000000000002', 'Priya Sharma', 'priya.sharma@example.com', '9876543211', 'Mumbai', 'Maharashtra', 'Referral', 'Silver Heights Tower', 'Apartment', '1.5Cr-2Cr', NOW(), NOW()),
('50000000-0000-0000-0000-000000000003', 'Amit Patel', 'amit.patel@example.com', '9876543212', 'Goa', 'Goa', 'Advertisement', 'Ocean View Apartments', 'Villa', '2Cr-3Cr', NOW(), NOW()),
('50000000-0000-0000-0000-000000000004', 'Sneha Reddy', 'sneha.reddy@example.com', '9876543213', 'Hyderabad', 'Telangana', 'Website', 'Green Valley Residency', 'Plot', '50L-80L', NOW(), NOW()),
('50000000-0000-0000-0000-000000000005', 'Vikram Singh', 'vikram.singh@example.com', '9876543214', 'Delhi', 'Delhi', 'Walk-in', 'Silver Heights Tower', 'Apartment', '1Cr-1.5Cr', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert Call Reports
-- CallReport columns: id, contact_id, tags, sales_agent, assigned_date, last_activity_date, remark, status, source, employee_id, call_duration, next_follow_up
INSERT INTO call_reports (id, contact_id, tags, sales_agent, assigned_date, last_activity_date, remark, status, source, employee_id, call_duration, next_follow_up, created_at, updated_at) VALUES
('60000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000001', 'Hot Lead', 'Mike Sales', NOW() - INTERVAL '5 days', NOW() - INTERVAL '2 days', 'Discussed project details and pricing. Customer very interested.', 'interested', 'Website', '20000000-0000-0000-0000-000000000003', 900, NOW() + INTERVAL '3 days', NOW(), NOW()),
('60000000-0000-0000-0000-000000000002', '50000000-0000-0000-0000-000000000002', 'Follow-up Required', 'Lisa Sales', NOW() - INTERVAL '3 days', NOW() - INTERVAL '1 day', 'Customer inquiry about amenities and pricing. Very positive response.', 'interested', 'Referral', '20000000-0000-0000-0000-000000000004', 1200, NOW() + INTERVAL '2 days', NOW(), NOW()),
('60000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000003', 'Callback Scheduled', 'Mike Sales', NOW() - INTERVAL '2 days', NOW(), 'Follow-up call, customer was busy. Requested callback tomorrow.', 'not interested', 'Advertisement', '20000000-0000-0000-0000-000000000003', 600, NOW() + INTERVAL '1 day', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;


-- Insert Site Visits
-- SiteVisit columns: id, employee_id, contact_id, visit_frequency, schedule_date, remark, lead_id, last_visited_date
INSERT INTO site_visits (id, employee_id, contact_id, visit_frequency, schedule_date, remark, lead_id, last_visited_date, created_at) VALUES
('80000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000001', 'first_visit', NOW() + INTERVAL '5 days', 'First site visit scheduled for Green Valley Residency', '50000000-0000-0000-0000-000000000001', NULL, NOW()),
('80000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000004', '50000000-0000-0000-0000-000000000002', 'follow_up', NOW() - INTERVAL '2 days', 'Customer impressed with amenities. Discussing unit options.', '50000000-0000-0000-0000-000000000002', NOW() - INTERVAL '2 days', NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert Leads
-- Lead columns: id, created_at, assigned_at, contact_id, sales_task_id, remark, site_visit, last_visited_date, call_duration, employee_id
INSERT INTO leads (id, created_at, assigned_at, contact_id, sales_task_id, remark, site_visit, last_visited_date, call_duration, employee_id) VALUES
('90000000-0000-0000-0000-000000000001', NOW(), NOW(), '50000000-0000-0000-0000-000000000001', '70000000-0000-0000-0000-000000000001', '10 December 9 pm', true, NOW(), 300, '20000000-0000-0000-0000-000000000003'),
('90000000-0000-0000-0000-000000000002', NOW(), NOW(), '50000000-0000-0000-0000-000000000002', '70000000-0000-0000-0000-000000000002', '20 December 2 pm', false, NULL, 150, '20000000-0000-0000-0000-000000000004'),
('90000000-0000-0000-0000-000000000003', NOW(), NOW(), '50000000-0000-0000-0000-000000000003', '70000000-0000-0000-0000-000000000003', '25 December 4 pm', true, NOW() - INTERVAL '5 days', 600, '20000000-0000-0000-0000-000000000003')
ON CONFLICT (id) DO NOTHING;
