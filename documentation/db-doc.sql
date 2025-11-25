-- Enable uuid-ossp extension if using uuid_generate_v4()
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- USERS, ROLES, TEAMS
CREATE TABLE roles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE teams (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  username TEXT NOT NULL UNIQUE,
  email TEXT UNIQUE,
  full_name TEXT,
  password_hash TEXT, -- if storing
  phone TEXT,
  role_id UUID REFERENCES roles(id) ON DELETE SET NULL,
  team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
  is_active BOOLEAN DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  deleted_at timestamptz
);

CREATE INDEX idx_users_team_id ON users(team_id);
CREATE INDEX idx_users_role_id ON users(role_id);

-- TAGS (for leads/contacts/projects)
CREATE TABLE tags (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL UNIQUE,
  created_at timestamptz DEFAULT now()
);

-- CONTACTS (generic persons)
CREATE TABLE contacts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  first_name TEXT,
  last_name TEXT,
  email TEXT,
  phone TEXT,
  country TEXT,
  city TEXT,
  source_id UUID, -- FK to lead_sources optionally
  extra_data JSONB, -- flexible profile fields
  owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
  assigned_team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  deleted_at timestamptz
);

CREATE INDEX idx_contacts_owner_id ON contacts(owner_id);
CREATE INDEX idx_contacts_phone ON contacts(phone);
CREATE INDEX idx_contacts_email ON contacts(email);

-- MANY-TO-MANY contact_tags
CREATE TABLE contact_tags (
  contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
  tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY(contact_id, tag_id)
);

-- LEAD SOURCES / CAMPAIGNS
CREATE TABLE lead_sources (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL UNIQUE,
  medium TEXT,
  sub_source TEXT,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE campaigns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  source_id UUID REFERENCES lead_sources(id) ON DELETE SET NULL,
  start_date date,
  end_date date,
  budget numeric,
  meta JSONB,
  created_at timestamptz DEFAULT now()
);

-- LEADS
CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_code TEXT UNIQUE, -- optional reference code
  contact_id UUID REFERENCES contacts(id) ON DELETE SET NULL,
  name TEXT, -- redundant convenience
  phone TEXT,
  email TEXT,
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL, -- sales agent
  assigned_team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
  channel_partner_id UUID, -- link to CP table below
  source_id UUID REFERENCES lead_sources(id) ON DELETE SET NULL,
  campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
  lead_stage TEXT, -- e.g. 'new','contacted','qualified','booked','lost'
  lead_category TEXT, -- e.g. deal / inquiry
  requirement JSONB, -- budget range, area range, property types, etc
  budget_min numeric,
  budget_max numeric,
  area_min numeric,
  area_max numeric,
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  tags JSONB,
  status TEXT, -- 'open','closed','archived'
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  deleted_at timestamptz
);

CREATE INDEX idx_leads_assigned_to ON leads(assigned_to);
CREATE INDEX idx_leads_stage ON leads(lead_stage);
CREATE INDEX idx_leads_source ON leads(source_id);
CREATE INDEX idx_leads_created_at ON leads(created_at);

-- Many-to-many lead_tags if you want relational tags
CREATE TABLE lead_tags (
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY(lead_id, tag_id)
);

-- LEAD STAGE HISTORY (track stage transitions)
CREATE TABLE lead_stage_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  from_stage TEXT,
  to_stage TEXT,
  changed_by UUID REFERENCES users(id) ON DELETE SET NULL,
  changed_at timestamptz DEFAULT now(),
  note TEXT
);

CREATE INDEX idx_lead_stage_history_lead_id ON lead_stage_history(lead_id);

-- ACTIVITIES (generic tasks/calls/meetings/site-visits)
CREATE TYPE activity_type AS ENUM ('call','email','meeting','site_visit','task','other');

CREATE TABLE activities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  activity_type activity_type NOT NULL,
  title TEXT,
  description TEXT,
  lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
  contact_id UUID REFERENCES contacts(id) ON DELETE SET NULL,
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  assigned_by UUID REFERENCES users(id) ON DELETE SET NULL,
  scheduled_at timestamptz,
  due_at timestamptz,
  completed_at timestamptz,
  status TEXT, -- pending, completed, cancelled
  result TEXT, -- outcome note
  meta JSONB,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  deleted_at timestamptz
);

CREATE INDEX idx_activities_assigned_to ON activities(assigned_to);
CREATE INDEX idx_activities_lead_id ON activities(lead_id);
CREATE INDEX idx_activities_scheduled_at ON activities(scheduled_at);

-- SITE VISITS (detailed)
CREATE TABLE site_visits (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  activity_id UUID REFERENCES activities(id) ON DELETE CASCADE,
  site_address TEXT,
  visit_status TEXT, -- scheduled, completed, cancelled
  visitor_count int,
  photos JSONB, -- urls
  report TEXT,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- PROJECTS and PROPERTIES
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  developer TEXT,
  location TEXT,
  start_date date,
  end_date date,
  meta JSONB,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE properties (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  unit_number TEXT,
  size numeric,
  price numeric,
  status TEXT, -- available, reserved, sold
  attributes JSONB,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
CREATE INDEX idx_properties_project_id ON properties(project_id);

-- CHANNEL PARTNERS
CREATE TABLE channel_partners (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  contact_person TEXT,
  phone TEXT,
  email TEXT,
  address TEXT,
  meta JSONB,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- BOOKINGS
CREATE TABLE bookings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
  property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
  booking_amount numeric,
  booking_date timestamptz,
  status TEXT, -- pending, confirmed, cancelled
  documents JSONB,
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE INDEX idx_bookings_lead_id ON bookings(lead_id);

-- ACCOUNTS / FINANCIALS
CREATE TABLE accounts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
  account_name TEXT,
  balance numeric,
  currency TEXT DEFAULT 'INR',
  meta JSONB,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  type TEXT, -- invoice, payment, refund
  amount numeric,
  currency TEXT DEFAULT 'INR',
  transaction_date timestamptz DEFAULT now(),
  meta JSONB
);
CREATE INDEX idx_transactions_account_id ON transactions(account_id);

-- CALL LOGS / AUTO DIALER
CREATE TABLE call_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
  contact_id UUID REFERENCES contacts(id) ON DELETE SET NULL,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL, -- agent
  call_start timestamptz,
  call_end timestamptz,
  duration_seconds int,
  status TEXT, -- answered, missed, busy, no_answer
  recording_url TEXT,
  sip_meta JSONB,
  created_at timestamptz DEFAULT now()
);
CREATE INDEX idx_call_logs_lead_id ON call_logs(lead_id);

CREATE TABLE auto_dialer_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT,
  status TEXT, -- scheduled, running, completed
  payload JSONB, -- list of numbers / parameters
  scheduled_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz DEFAULT now()
);

-- DOCUMENTS & ATTACHMENTS
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  owner_type TEXT, -- 'lead','contact','booking','project','property','activity'
  owner_id UUID,
  file_name TEXT,
  file_path TEXT,
  file_meta JSONB,
  uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
  uploaded_at timestamptz DEFAULT now()
);

-- NOTES
CREATE TABLE notes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  owner_type TEXT,
  owner_id UUID,
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  content TEXT,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- LOGS / AUDIT (immutable)
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  entity_type TEXT, -- e.g. 'lead','user'
  entity_id UUID,
  action TEXT, -- 'create','update','delete','assign'
  performed_by UUID REFERENCES users(id) ON DELETE SET NULL,
  performed_at timestamptz DEFAULT now(),
  diff JSONB, -- before/after snapshot or delta
  meta JSONB
);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);

-- SIMPLE REPORTING TABLE: materialized or aggregated tables can be created later
