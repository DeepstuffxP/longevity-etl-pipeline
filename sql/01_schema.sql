CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS warehouse;

CREATE TABLE raw.athletes_snapshot(
    snapshot_id SERIAL PRIMARY KEY,
    pulled_at   TIMESTAMPTZ NOT NULL,
    source_file TEXT NOT NULL UNIQUE,
    payload     JSONB NOT NULL
);

CREATE TABLE warehouse.dim_marker (
    marker_key SERIAL PRIMARY KEY,
    marker_code TEXT NOT NULL UNIQUE,
    marker_name TEXT NOT NULL,
    unit        TEXT NOT NULL
);

INSERT INTO warehouse.dim_marker (marker_code, marker_name, unit) VALUES 
('AlbGL',            'Albumin',                 'g/L'),
('CreatUmolL',       'Creatinine',              'umol/L'),
('GluMmolL',         'Glucose',                 'mmol/L'),
('CrpMgL',           'C-reactive protein',      'mg/L'),
('LymPc',            'Lymphocytes',             '%'),
('McvFL',            'Mean corpuscular volume', 'fL'),
('RdwPc',            'Red cell distribution width', '%'),
('AlpUL',            'Alkaline phosphatase',    'U/L'),
('Wbc1000cellsuL',   'White blood cells',       '10^3 cells/uL'),
('NeutrophilPc',     'Neutrophils',             '%'),
('MonocytePc',       'Monocytes',               '%'),
('Rbc10e12L',        'Red blood cells',         '10^12/L'),
('MchPg',            'Mean corpuscular hemoglobin', 'pg'),
('UreaMmolL',        'Urea',                    'mmol/L'),
('CystatinCMgL',     'Cystatin C',              'mg/L'),
('Hba1cMmolMol',     'HbA1c',                   'mmol/mol'),
('CholesterolMmolL', 'Total cholesterol',       'mmol/L'),
('ApoA1GL',          'Apolipoprotein A1',       'g/L'),
('AltUL',            'Alanine aminotransferase','U/L'),
('GgtUL',            'Gamma-glutamyl transferase','U/L'),
('ShbgNmolL',        'Sex hormone-binding globulin','nmol/L'),
('VitaminDNmolL',    'Vitamin D',               'nmol/L');