DROP TABLE IF EXISTS plan;

CREATE TABLE IF NOT EXISTS plan (
  id SERIAL PRIMARY KEY,
  terraform_version varchar(10),
  git_remote text,
  git_commit varchar(50),
  ci_url text,
  source text,
  resource_updated integer,
  resource_nooped integer,
  plan jsonb,
  generation_date timestamp with time zone
);

COMMENT ON COLUMN plan.source IS 'Free field to indicate event that generate report: ''pipeline with wrapper'', ''cli from laptop'', ''bulk import''';
