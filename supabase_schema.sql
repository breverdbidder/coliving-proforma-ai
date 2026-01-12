-- BidDeed.AI Co-Living Proforma - Supabase Schema
-- Generated: 2026-01-11

-- Table: coliving_properties

CREATE TABLE IF NOT EXISTS coliving_properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Property Information
    property_name TEXT,
    property_location TEXT DEFAULT 'Brevard County, FL',
    total_units INTEGER,
    total_bedrooms INTEGER,
    
    -- Unit Mix
    studio_units INTEGER DEFAULT 0,
    one_br_units INTEGER DEFAULT 0,
    two_br_units INTEGER DEFAULT 0,
    
    -- Financial Assumptions (JSONB for flexibility)
    assumptions JSONB,
    
    -- User/Session Info
    user_id TEXT,
    session_id TEXT,
    
    -- Metadata
    status TEXT DEFAULT 'draft',
    tags TEXT[]
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_coliving_properties_user ON coliving_properties(user_id);
CREATE INDEX IF NOT EXISTS idx_coliving_properties_session ON coliving_properties(session_id);
CREATE INDEX IF NOT EXISTS idx_coliving_properties_created ON coliving_properties(created_at DESC);


-- Table: coliving_analyses

CREATE TABLE IF NOT EXISTS coliving_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    property_id UUID REFERENCES coliving_properties(id) ON DELETE CASCADE,
    
    -- Analysis Metadata
    analysis_type TEXT DEFAULT 'full_analysis',
    pipeline_version TEXT DEFAULT 'v1.0.0',
    
    -- Financial Results
    revenue_projections JSONB,
    expense_analysis JSONB,
    cash_flow JSONB,
    returns_metrics JSONB,
    sensitivity_analysis JSONB,
    risk_assessment JSONB,
    
    -- Key Metrics (for easy querying)
    noi DECIMAL(12,2),
    cap_rate DECIMAL(5,2),
    cash_on_cash_return DECIMAL(5,2),
    dscr DECIMAL(5,2),
    
    -- AI Recommendations
    recommendations TEXT[],
    investment_decision TEXT,  -- 'BUY', 'PASS', 'FURTHER_ANALYSIS'
    
    -- Processing Info
    processing_time_seconds DECIMAL(6,2),
    stage_completed TEXT DEFAULT 'complete',
    errors JSONB
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_coliving_analyses_property ON coliving_analyses(property_id);
CREATE INDEX IF NOT EXISTS idx_coliving_analyses_created ON coliving_analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_coliving_analyses_decision ON coliving_analyses(investment_decision);


-- Table: coliving_reports

CREATE TABLE IF NOT EXISTS coliving_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analysis_id UUID REFERENCES coliving_analyses(id) ON DELETE CASCADE,
    
    -- Report Formats
    excel_url TEXT,
    pdf_url TEXT,
    dashboard_data JSONB,
    
    -- Metadata
    report_type TEXT,  -- 'executive_summary', 'full_proforma', 'dashboard'
    file_size_bytes INTEGER,
    download_count INTEGER DEFAULT 0,
    
    -- Storage
    storage_bucket TEXT DEFAULT 'coliving-reports',
    storage_path TEXT
);

-- Index
CREATE INDEX IF NOT EXISTS idx_coliving_reports_analysis ON coliving_reports(analysis_id);


-- Table: coliving_conversations

CREATE TABLE IF NOT EXISTS coliving_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Conversation Data
    user_id TEXT,
    session_id TEXT,
    property_id UUID REFERENCES coliving_properties(id) ON DELETE SET NULL,
    
    -- Messages
    user_message TEXT,
    assistant_response TEXT,
    
    -- Intent Analysis
    intent_classified TEXT,
    entities_extracted JSONB,
    
    -- Metadata
    response_time_ms INTEGER,
    model_used TEXT DEFAULT 'claude-sonnet-4-20250514'
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_coliving_conversations_session ON coliving_conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_coliving_conversations_created ON coliving_conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_coliving_conversations_property ON coliving_conversations(property_id);


-- Table: coliving_scenarios

CREATE TABLE IF NOT EXISTS coliving_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    property_id UUID REFERENCES coliving_properties(id) ON DELETE CASCADE,
    
    -- Scenario Info
    scenario_name TEXT,
    scenario_description TEXT,
    
    -- Modified Assumptions
    modified_assumptions JSONB,
    
    -- Results
    scenario_noi DECIMAL(12,2),
    scenario_cap_rate DECIMAL(5,2),
    scenario_cash_flow DECIMAL(12,2),
    scenario_dscr DECIMAL(5,2),
    
    -- Comparison
    base_scenario BOOLEAN DEFAULT FALSE,
    variance_from_base JSONB
);

-- Index
CREATE INDEX IF NOT EXISTS idx_coliving_scenarios_property ON coliving_scenarios(property_id);


-- Row Level Security (RLS) Policies

ALTER TABLE coliving_properties ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations for service role" ON coliving_properties
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Allow read for authenticated users" ON coliving_properties
FOR SELECT
TO authenticated
USING (true);

ALTER TABLE coliving_analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations for service role" ON coliving_analyses
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Allow read for authenticated users" ON coliving_analyses
FOR SELECT
TO authenticated
USING (true);

ALTER TABLE coliving_reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations for service role" ON coliving_reports
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Allow read for authenticated users" ON coliving_reports
FOR SELECT
TO authenticated
USING (true);

ALTER TABLE coliving_conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations for service role" ON coliving_conversations
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Allow read for authenticated users" ON coliving_conversations
FOR SELECT
TO authenticated
USING (true);

ALTER TABLE coliving_scenarios ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations for service role" ON coliving_scenarios
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Allow read for authenticated users" ON coliving_scenarios
FOR SELECT
TO authenticated
USING (true);

