"""Shared component parsing and system prompt for LLM clients."""

import logging

from polly_pipeline_server.domain.rag.entities import (
    Chart,
    ChartDataPoint,
    ChartSeries,
    ChartType,
    Comparison,
    ComparisonAttribute,
    ComparisonItem,
    Component,
    DataTable,
    MemberProfile,
    MemberProfiles,
    Notice,
    NoticeLevel,
    PartyVote,
    TableColumn,
    TextBlock,
    TextFormat,
    Timeline,
    TimelineEvent,
    VotingBreakdown,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Polly, an assistant that helps people understand political information.

RULES:
1. Only use information from the provided context
2. Be factually accurate and non-partisan
3. Present asymmetric facts accurately without false balance

RESPONSE FORMAT:
You must respond with a JSON object with this exact structure:
{
  "title": "Response Title",
  "sections": [
    {
      "title": "Optional Section Title",
      "components": [
        { component object }
      ]
    }
  ]
}

AVAILABLE COMPONENT TYPES (use exact type values):

1. "text_block" - For explanations and narrative content
{
  "type": "text_block",
  "title": "Optional Title",
  "content": "Markdown content here. Can include **bold**, *italic*, lists, etc."
}

2. "notice" - For important callouts and warnings
{
  "type": "notice",
  "level": "info",
  "title": "Optional Title",
  "message": "The important message to highlight"
}
level must be: "info", "warning", or "important"

3. "chart" - For data visualization
{
  "type": "chart",
  "chart_type": "bar",
  "title": "Chart Title",
  "series": [
    {
      "name": "Series Name",
      "data": [
        {"label": "Category A", "value": 150},
        {"label": "Category B", "value": 230}
      ]
    }
  ],
  "x_axis_label": "Categories",
  "y_axis_label": "Count"
}
chart_type must be: "bar", "line", "pie", "doughnut", "horizontal_bar", or "stacked_bar"
IMPORTANT: value must be a number, not a string

4. "timeline" - For chronological events
{
  "type": "timeline",
  "title": "Timeline Title",
  "events": [
    {"date": "2024-01-15", "label": "First Reading", "description": "Bill introduced"},
    {"date": "2024-02-20", "label": "Second Reading", "description": "Debate held"}
  ]
}

5. "data_table" - For structured tabular data
{
  "type": "data_table",
  "title": "Table Title",
  "columns": [
    {"header": "Name", "key": "name"},
    {"header": "Party", "key": "party"},
    {"header": "Vote", "key": "vote"}
  ],
  "rows": [
    {"name": "John Smith", "party": "Labour", "vote": "Aye"},
    {"name": "Jane Doe", "party": "Conservative", "vote": "No"}
  ]
}

6. "comparison" - For comparing policies or positions
{
  "type": "comparison",
  "title": "Policy Comparison",
  "items": [
    {"name": "Labour"},
    {"name": "Conservative"}
  ],
  "attributes": [
    {"name": "Tax Policy", "values": ["Increase for high earners", "Reduce overall"]},
    {"name": "NHS Funding", "values": ["Increase by 5%", "Maintain current"]}
  ]
}

7. "member_profiles" - For politician information
{
  "type": "member_profiles",
  "title": "MPs Mentioned",
  "members": [
    {"member_id": "1", "name": "John Smith", "party": "Labour", "constituency": "Leeds Central", "roles": ["Shadow Minister"]}
  ]
}

8. "voting_breakdown" - For parliamentary vote results
{
  "type": "voting_breakdown",
  "title": "Vote on Climate Bill",
  "date": "2024-03-15",
  "result": "passed",
  "total_for": 350,
  "total_against": 220,
  "total_abstentions": 30,
  "party_breakdown": [
    {"party": "Labour", "votes_for": 195, "votes_against": 5, "abstentions": 2},
    {"party": "Conservative", "votes_for": 45, "votes_against": 200, "abstentions": 20}
  ]
}
result must be: "passed", "rejected", or "tied"
IMPORTANT: all vote counts must be numbers, not strings

EXAMPLE COMPLETE RESPONSE:

For a question about a parliamentary vote:
{
  "title": "Climate Action Bill Vote Results",
  "sections": [
    {
      "title": "Summary",
      "components": [
        {
          "type": "text_block",
          "content": "The Climate Action Bill passed its third reading on March 15, 2024, with cross-party support despite Conservative opposition."
        }
      ]
    },
    {
      "title": "Vote Breakdown",
      "components": [
        {
          "type": "voting_breakdown",
          "title": "Third Reading Vote",
          "date": "2024-03-15",
          "result": "passed",
          "total_for": 350,
          "total_against": 220,
          "party_breakdown": [
            {"party": "Labour", "votes_for": 195, "votes_against": 5, "abstentions": 2},
            {"party": "Conservative", "votes_for": 45, "votes_against": 200, "abstentions": 20},
            {"party": "Liberal Democrats", "votes_for": 70, "votes_against": 0, "abstentions": 2}
          ]
        }
      ]
    }
  ]
}

For a question about bill history:
{
  "title": "Housing Reform Bill Progress",
  "sections": [
    {
      "components": [
        {
          "type": "text_block",
          "content": "The Housing Reform Bill has progressed through multiple readings since its introduction."
        },
        {
          "type": "timeline",
          "title": "Legislative Journey",
          "events": [
            {"date": "2024-01-10", "label": "First Reading", "description": "Bill formally introduced"},
            {"date": "2024-02-15", "label": "Second Reading", "description": "Passed 320-180"},
            {"date": "2024-03-20", "label": "Committee Stage", "description": "Amendments proposed"}
          ]
        }
      ]
    }
  ]
}

GUIDELINES:
- Always include at least one text_block to provide context
- Use voting_breakdown for any parliamentary vote data
- Use chart when comparing numerical data visually
- Use timeline for chronological sequences
- Combine multiple component types for rich responses
- All numerical values must be actual numbers, not strings"""


# JSON Schema for Ollama format parameter
RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["title", "sections"],
    "properties": {
        "title": {"type": "string"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["components"],
                "properties": {
                    "title": {"type": ["string", "null"]},
                    "components": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["type"],
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": [
                                        "text_block",
                                        "notice",
                                        "chart",
                                        "timeline",
                                        "data_table",
                                        "comparison",
                                        "member_profiles",
                                        "voting_breakdown",
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


# Type aliases for more lenient parsing
TYPE_ALIASES = {
    "text": "text_block",
    "textblock": "text_block",
    "text-block": "text_block",
    "paragraph": "text_block",
    "voting": "voting_breakdown",
    "vote": "voting_breakdown",
    "vote_breakdown": "voting_breakdown",
    "votes": "voting_breakdown",
    "table": "data_table",
    "datatable": "data_table",
    "data-table": "data_table",
    "compare": "comparison",
    "members": "member_profiles",
    "member": "member_profiles",
    "profiles": "member_profiles",
    "memberprofiles": "member_profiles",
    "member-profiles": "member_profiles",
    "graph": "chart",
    "bar_chart": "chart",
    "pie_chart": "chart",
    "line_chart": "chart",
    "events": "timeline",
    "history": "timeline",
    "alert": "notice",
    "warning": "notice",
    "info": "notice",
}


def parse_component(data: dict) -> Component | None:
    """Parse a component dictionary into a domain Component object."""
    raw_type = data.get("type", "")
    
    # Normalize type: lowercase, replace hyphens with underscores
    normalized_type = raw_type.lower().replace("-", "_").strip()
    
    # Apply aliases
    comp_type = TYPE_ALIASES.get(normalized_type, normalized_type)

    if comp_type == "text_block":
        return Component.create(
            TextBlock(
                content=data.get("content", ""),
                title=data.get("title"),
                format=TextFormat.MARKDOWN,
            )
        )

    elif comp_type == "notice":
        level_str = data.get("level", "info")
        level = NoticeLevel.INFO
        if level_str == "warning":
            level = NoticeLevel.WARNING
        elif level_str == "important":
            level = NoticeLevel.IMPORTANT

        return Component.create(
            Notice(
                message=data.get("message", ""),
                level=level,
                title=data.get("title"),
            )
        )

    elif comp_type == "chart":
        chart_type_str = data.get("chart_type", "bar")
        try:
            chart_type = ChartType(chart_type_str)
        except ValueError:
            chart_type = ChartType.BAR

        series_data = data.get("series", [])
        series = []
        for s in series_data:
            data_points = [
                ChartDataPoint(
                    label=str(d.get("label", "")),
                    value=float(d.get("value", 0)),
                    category=d.get("category"),
                )
                for d in s.get("data", [])
            ]
            series.append(
                ChartSeries(
                    name=s.get("name", ""),
                    data=data_points,
                )
            )

        return Component.create(
            Chart(
                chart_type=chart_type,
                series=series,
                title=data.get("title"),
                x_axis_label=data.get("x_axis_label"),
                y_axis_label=data.get("y_axis_label"),
                caption=data.get("caption"),
            )
        )

    elif comp_type == "timeline":
        events_data = data.get("events", [])
        events = [
            TimelineEvent(
                date=str(e.get("date", "")),
                label=str(e.get("label", "")),
                description=e.get("description"),
                reference_url=e.get("reference_url"),
                significance=int(e.get("significance", 3)),
            )
            for e in events_data
        ]

        return Component.create(
            Timeline(
                events=events,
                title=data.get("title"),
                caption=data.get("caption"),
            )
        )

    elif comp_type == "data_table":
        columns_data = data.get("columns", [])
        columns = [
            TableColumn(
                header=str(c.get("header", "")),
                key=str(c.get("key", "")),
                sortable=bool(c.get("sortable", False)),
                align=str(c.get("align", "left")),
            )
            for c in columns_data
        ]

        rows = data.get("rows", [])
        # Ensure rows are dicts with string values
        parsed_rows = []
        for row in rows:
            if isinstance(row, dict):
                parsed_rows.append({str(k): str(v) for k, v in row.items()})

        return Component.create(
            DataTable(
                columns=columns,
                rows=parsed_rows,
                title=data.get("title"),
                caption=data.get("caption"),
            )
        )

    elif comp_type == "comparison":
        items_data = data.get("items", [])
        items = [
            ComparisonItem(
                name=str(i.get("name", "")),
                description=i.get("description"),
            )
            for i in items_data
        ]

        attributes_data = data.get("attributes", [])
        attributes = [
            ComparisonAttribute(
                name=str(a.get("name", "")),
                values=[str(v) for v in a.get("values", [])],
            )
            for a in attributes_data
        ]

        return Component.create(
            Comparison(
                items=items,
                attributes=attributes,
                title=data.get("title"),
                caption=data.get("caption"),
            )
        )

    elif comp_type == "member_profiles":
        members_data = data.get("members", [])
        members = [
            MemberProfile(
                member_id=str(m.get("member_id", "")),
                name=str(m.get("name", "")),
                party=str(m.get("party", "")),
                constituency=m.get("constituency"),
                roles=list(m.get("roles", [])),
                photo_url=m.get("photo_url"),
                biography=m.get("biography"),
                profile_url=m.get("profile_url"),
            )
            for m in members_data
        ]

        return Component.create(
            MemberProfiles(
                members=members,
                title=data.get("title"),
                caption=data.get("caption"),
            )
        )

    elif comp_type == "voting_breakdown":
        party_data = data.get("party_breakdown", [])
        party_breakdown = [
            PartyVote(
                party=str(p.get("party", "")),
                votes_for=int(p.get("votes_for", 0)),
                votes_against=int(p.get("votes_against", 0)),
                abstentions=int(p.get("abstentions", 0)),
                not_voting=int(p.get("not_voting", 0)),
            )
            for p in party_data
        ]

        return Component.create(
            VotingBreakdown(
                total_for=int(data.get("total_for", 0)),
                total_against=int(data.get("total_against", 0)),
                party_breakdown=party_breakdown,
                title=data.get("title"),
                date=data.get("date"),
                total_abstentions=int(data.get("total_abstentions", 0)),
                result=data.get("result"),
                caption=data.get("caption"),
            )
        )

    # Log unrecognized types for debugging
    if raw_type:
        logger.warning(f"Unrecognized component type: '{raw_type}' (normalized: '{comp_type}')")
    
    return None
