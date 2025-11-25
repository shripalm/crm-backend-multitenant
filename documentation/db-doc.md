
# CRM Database Design – Markdown Representation

## 1. Overview
This CRM database schema covers:

- Users, Teams, Roles  
- Contacts & Leads  
- Lead Stages & Activities  
- Projects & Properties  
- Channel Partners  
- Bookings, Accounts & Transactions  
- Campaigns & Lead Sources  
- Call Logs & Auto-dialer  
- Documents, Notes  
- System Logs & Audit  

UUID PKs, soft-delete via `deleted_at`, flexible fields via JSONB.

---

## 2. ER Overview (Text Diagram)

Users ───┐  
Teams ───┤──< Users  
Roles ───┘  

Contacts ─< Leads >── Projects >── Properties  
      │          │  
      │          └── Activities >── Site Visits  
      │  
      └── Activities (calls/meetings/tasks)

Leads ─< Lead Stage History  
Leads ─< Lead Tags >── Tags  

Leads ─< Bookings >── Properties  

Leads ─< Call Logs >── Users  
Contacts ─< Call Logs  

Campaigns ─< Leads  
Lead Sources ─< Leads  

Channel Partners ─< Leads  

Documents (polymorphic)  
Notes (polymorphic)  
Audit Logs (polymorphic)

---

## 3. Tables Summary

### 3.1 Users & Access Control
- users  
- roles  
- teams  

### 3.2 Contacts & Tags
- contacts  
- tags  
- contact_tags  

### 3.3 Leads & Lifecycle
- leads  
- lead_tags  
- lead_stage_history  

### 3.4 Activities
- activities  
- site_visits  

### 3.5 Projects & Properties
- projects  
- properties  

### 3.6 Channel Partners
- channel_partners  

### 3.7 Bookings & Accounts
- bookings  
- accounts  
- transactions  

### 3.8 Campaigns & Lead Sources
- campaigns  
- lead_sources  

### 3.9 Calls & Auto Dialer
- call_logs  
- auto_dialer_jobs  

### 3.10 Documents & Notes
- documents  
- notes  

### 3.11 Audits
- audit_logs  

---

## 4. Entity-to-Module Summary

| Module | Tables |
|--------|--------|
| User Management | users, roles, teams |
| Contacts | contacts, contact_tags |
| Leads | leads, lead_tags, lead_stage_history |
| Activities | activities, site_visits |
| Projects | projects, properties |
| Channel Partners | channel_partners |
| Booking & Sales | bookings, accounts, transactions |
| Campaigns | campaigns, lead_sources |
| Calls | call_logs, auto_dialer_jobs |
| File Management | documents |
| Notes | notes |
| Logs & Audits | audit_logs |

---

