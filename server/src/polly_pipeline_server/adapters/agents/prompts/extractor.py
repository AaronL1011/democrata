"""Extraction prompts for grounded data extraction from context."""

GROUNDING_RULES = """GROUNDING RULES (CRITICAL):
- Only extract values EXPLICITLY stated in the context
- Use null for any field not directly found in the text
- Do not calculate, infer, or estimate missing values
- Do not use prior knowledge about Australian politics
- Include the exact source quote for every extracted fact
- If conflicting values exist, extract both with sources"""

# Note: We use string concatenation instead of f-strings to avoid issues
# with curly braces in JSON examples conflicting with .format() placeholders

VOTING_EXTRACTION_PROMPT = """Extract voting data from the context below.

""" + GROUNDING_RULES + """

Context:
{context}

Query focus: {query_focus}

Extract JSON:
```json
{{
  "bill_name": "exact name from text or null",
  "vote_date": "YYYY-MM-DD from text or null",
  "result": "passed|rejected|tied from text or null",
  "votes_for": "number from text or null",
  "votes_against": "number from text or null",
  "total_abstentions": "number from text or null",
  "party_breakdown": [
    {{
      "party": "exact party name",
      "votes_for": "number or null",
      "votes_against": "number or null",
      "abstentions": "number or null"
    }}
  ],
  "source_quotes": ["exact sentence containing this data"],
  "completeness": "0.0-1.0",
  "warnings": ["any missing critical fields"]
}}
```

Respond with JSON only:"""

CHART_EXTRACTION_PROMPT = """Extract numerical data suitable for charting from the context.

""" + GROUNDING_RULES + """

Context:
{context}

Query focus: {query_focus}

Extract JSON:
```json
{{
  "chart_type": "bar|line|pie|horizontal_bar|stacked_bar",
  "title": "descriptive title based on data",
  "series": [
    {{
      "name": "series name",
      "data": [
        {{"label": "category", "value": "number from text"}}
      ]
    }}
  ],
  "x_axis_label": "label or null",
  "y_axis_label": "label or null",
  "source_quotes": ["exact sentences containing numerical data"],
  "completeness": "0.0-1.0",
  "warnings": ["any data quality issues"]
}}
```

Respond with JSON only:"""

TIMELINE_EXTRACTION_PROMPT = """Extract chronological events from the context.

""" + GROUNDING_RULES + """

ADDITIONAL RULES:
- Only include events with explicit dates in the text
- Use exact wording from source for descriptions
- Do not infer dates from phrases like "last month"
- Order events chronologically

Context:
{context}

Query focus: {query_focus}

Extract JSON:
```json
{{
  "title": "timeline title",
  "events": [
    {{
      "date": "YYYY-MM-DD from text",
      "label": "short event name",
      "description": "event description from text",
      "source_quote": "exact sentence"
    }}
  ],
  "source_quotes": ["sentences containing dates"],
  "completeness": "0.0-1.0",
  "warnings": ["events with unclear dates"]
}}
```

Respond with JSON only:"""

COMPARISON_EXTRACTION_PROMPT = """Extract comparison data for multiple entities from the context.

""" + GROUNDING_RULES + """

Context:
{context}

Query focus: {query_focus}
Entities to compare: {entities}

Extract JSON:
```json
{{
  "title": "comparison title",
  "items": [
    {{"name": "entity name", "description": "brief description or null"}}
  ],
  "attributes": [
    {{
      "name": "attribute being compared",
      "values": ["value for entity 1", "value for entity 2"],
      "source_quotes": ["source for each value"]
    }}
  ],
  "source_quotes": ["key quotes supporting comparison"],
  "completeness": "0.0-1.0",
  "warnings": ["entities with missing data"]
}}
```

Respond with JSON only:"""

DATA_TABLE_EXTRACTION_PROMPT = """Extract structured tabular data from the context.

""" + GROUNDING_RULES + """

Context:
{context}

Query focus: {query_focus}

Extract JSON:
```json
{{
  "title": "table title",
  "columns": [
    {{"header": "column name", "key": "column_key"}}
  ],
  "rows": [
    {{"column_key": "value from text"}}
  ],
  "source_quotes": ["sentences containing tabular data"],
  "completeness": "0.0-1.0",
  "warnings": ["incomplete rows or columns"]
}}
```

Respond with JSON only:"""

MEMBER_PROFILES_EXTRACTION_PROMPT = """Extract politician/member information from the context.

""" + GROUNDING_RULES + """

Context:
{context}

Query focus: {query_focus}

Extract JSON:
```json
{{
  "title": "section title",
  "members": [
    {{
      "name": "full name from text",
      "party": "party affiliation from text or null",
      "constituency": "electorate from text or null",
      "roles": ["role or position from text"],
      "source_quote": "sentence mentioning this member"
    }}
  ],
  "source_quotes": ["key quotes about members"],
  "completeness": "0.0-1.0",
  "warnings": ["members with incomplete information"]
}}
```

Respond with JSON only:"""

TEXT_BLOCK_EXTRACTION_PROMPT = """Extract key information for a text summary from the context.

""" + GROUNDING_RULES + """

Context:
{context}

Query focus: {query_focus}

Extract JSON:
```json
{{
  "title": "section title or null",
  "key_points": [
    {{
      "point": "key fact or insight",
      "source_quote": "supporting quote from text"
    }}
  ],
  "summary_focus": "main topic of the text",
  "source_quotes": ["most relevant quotes"],
  "completeness": "0.0-1.0",
  "warnings": ["areas with insufficient information"]
}}
```

Respond with JSON only:"""

NOTICE_EXTRACTION_PROMPT = """Identify important notices, warnings, or callouts from the context.

""" + GROUNDING_RULES + """

Context:
{context}

Query focus: {query_focus}

Extract JSON:
```json
{{
  "notices": [
    {{
      "level": "info|warning|important",
      "title": "notice title or null",
      "message": "the important information from text",
      "source_quote": "exact source sentence"
    }}
  ],
  "completeness": 1.0,
  "warnings": []
}}
```

Respond with JSON only:"""

GENERIC_EXTRACTION_PROMPT = """Extract relevant information from the context for the specified component type.

""" + GROUNDING_RULES + """

Component type: {component_type}
Context:
{context}

Query focus: {query_focus}

Extract JSON with:
- Relevant structured data for the component type
- source_quotes: list of supporting quotes
- completeness: 0.0-1.0 score
- warnings: list of any data issues

Respond with JSON only:"""

EXTRACTION_PROMPTS = {
    "voting_breakdown": VOTING_EXTRACTION_PROMPT,
    "chart": CHART_EXTRACTION_PROMPT,
    "timeline": TIMELINE_EXTRACTION_PROMPT,
    "comparison": COMPARISON_EXTRACTION_PROMPT,
    "data_table": DATA_TABLE_EXTRACTION_PROMPT,
    "member_profiles": MEMBER_PROFILES_EXTRACTION_PROMPT,
    "text_block": TEXT_BLOCK_EXTRACTION_PROMPT,
    "notice": NOTICE_EXTRACTION_PROMPT,
}
