
Summary
This document outlines a high-level plan for a standalone AI-driven DatabaseAgent using PydanticAI and a self-hosted Supabase instance for data persistence. It details the chosen tech stack, core workflows (insert/upsert, fetch/list), freeform category classification via an LLM (with current categories provided), conditional schema evolution based on user requests, user-friendly messaging, and key design considerations for reliability and extensibility.
Overview
The DatabaseAgent will be a self-contained service with the following responsibilities:
Schema Introspection: Fetch current table and column metadata from Supabase to understand and mirror the database structure.
Dynamic Model Generation: Create or update Pydantic models at runtime to reflect table schemas for type-safe validation.
CRUD Operations:
Insert/Upsert: Validate payloads, classify categories with an LLM (given the list of existing categories), conditionally adapt schema or create tables when explicitly requested, and write records.
Fetch/List: Retrieve rows from specified tables, with optional filtering, and return them for display.
Schema Evolution (On Demand): Only execute ALTER TABLE ADD COLUMN or CREATE TABLE commands upon explicit user instruction.
Freeform Category Classification: Prompt an LLM to generate a concise category label, providing it with the current list of category names to check against, and insert new entries if needed.
User-Friendly Responses: Send structured success or failure messages with clear details back to calling services.
Technical Stack
Language & Agent Framework: Python 3.9+ with PydanticAI for structured agent orchestration and seamless LLM integration.
Database: Self-hosted Supabase Postgres, managed via the Supabase-Py client.
ORM/Schema Layer: Dynamic Pydantic models generated from Supabase schema metadata.
LLM Providers: Any supported by PydanticAI (e.g. OpenAI, Anthropic, Ollama) for category classification.
Core Workflows
Insert/Upsert
Validation: Use PydanticAI to parse and enforce schema on the incoming payload.
Category Classification: Pass the payload plus a list of existing category names to the LLM, prompting it to suggest a freeform category.
Category Persistence: Check the categories table for the LLM’s suggestion; insert the new category if it doesn’t exist.
Schema Adaptation (Conditional): If the user has requested schema changes (e.g., new columns or tables), execute the corresponding ALTER TABLE ADD COLUMN or CREATE TABLE SQL commands via Supabase API and update Pydantic models; otherwise, omit schema modifications and return an error for unknown fields.
Database Operation: Perform an upsert using Supabase-Py in a transaction to ensure consistency between category and record.
Response: Return a JSON object with { success: bool, message: str, data: record | null, error: {...} | null }.
Fetch/List
Request Parsing: Determine target table and any requested filters from the payload.
Query Execution: Call Supabase .select() with filters applied.
Delivery: Serialize results into JSON and return, or a user-friendly message if no data is found.
Schema Evolution (On Demand)
Column Addition: Upon explicit user command (e.g., “add column X of type Y to table Z”), issue ALTER TABLE ... ADD COLUMN via Supabase SQL API and refresh the Pydantic model.
Table Creation: Upon explicit user command (e.g., “create table Z with columns A, B, C”), issue CREATE TABLE via Supabase SQL API, then generate the corresponding Pydantic model.
Freeform Category Classification
Prompt Design: Construct a system prompt that feeds the LLM both the payload and a list of existing category names, asking it to pick or suggest a new concise category.
Matching: Compare the LLM’s output against the provided list; if not present, persist the new category in categories.
Agent Interface & Messaging
Methods:
handle_insert(data: dict, schema_changes: bool = False) → dict
handle_fetch(table: str, filters: dict = None) → dict
handle_schema_command(command: SchemaCommand) → dict
(for CREATE TABLE or ADD COLUMN requests)
Response Schema:
{
  "success": true/false,
  "message": "Clear user-facing description of outcome",
  "data": { ... } | [ ... ] | null,
  "error": { "code": "string", "detail": "string" } | null
}

Reasoning & Design Considerations
Single Responsibility: Focus exclusively on the DatabaseAgent, decoupled from orchestration logic.
Explicit Control: Schema modifications occur only when explicitly requested by the user, preventing unintended changes.
Extensibility: Dynamic model generation and on-demand schema evolution enable support for evolving data needs.
Reliability: Use transactions to maintain consistency between category persistence and record operations.
Performance: Cache schema metadata, refreshing only when schema commands are executed or explicitly invalidated.
UX: Return clear, structured responses for seamless integration with calling services.
Next Steps
Define Initial Schema: Draft base tables (records, categories, etc.) and core column definitions.
Prototype Schema Introspector: Implement logic to fetch Supabase metadata and generate Pydantic models.
LLM Prompt Testing: Design and iterate system prompts supplying category lists to the LLM.
Implement DatabaseAgent Skeleton: Build action handlers for insert/upsert (with conditional schema), fetch/list, and explicit schema commands.
Integration Testing: Validate end-to-end flows, including schema commands, against a test Supabase instance.
Prepared on April 24, 2025
