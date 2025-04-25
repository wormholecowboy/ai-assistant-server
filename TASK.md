# Tasks for AI Coding Agent: DatabaseAgent Implementation

This document outlines the tasks required to implement the DatabaseAgent as described in the plan. Each task is a specific coding task.

## I. Project Setup and Core Components

* **Task 1: Set up Project Structure**
    * [x]  Create the following directories:
        * `database_agent/` (for the main agent code)
        * `models/` (for Pydantic models)
        * `utils/` (for utility functions)
        * `tests/` (for unit and integration tests)

* **Task 2: Install Dependencies**
    * [x]  Add the following packages to `requirements.txt`:
        * `pydantic`
        * `pydantic_ai`
        * `supabase`
        * `python-dotenv`
        * `any LLM library (e.g., openai, anthropic)`
    * [x]  Install the dependencies using `pip install -r requirements.txt`.

* **Task 3: Register DatabaseAgent with Orchestrator**
    * [x]  Add DatabaseAgent as a tool/subagent to the orchestrator so it can be called from the main orchestration agent.
    * [ ]  Ensure the orchestrator can route relevant tasks to DatabaseAgent.

* **Task 5: Requirements Review**
    * [ ]  Review and remove any unused dependencies from `requirements.txt`.

## II. Database Interaction and Model Generation

* **Task 5: Implement Supabase Client Initialization**
    * [x]  Create a module in `database_agent/supabase_client.py`.
    * [x]  Implement a function to initialize the Supabase client using the `supabase-py` library and the environment variables.
    * [x]  Ensure the client is a singleton or globally accessible.

* **Task 6: Implement Schema Introspection**
    * [x]  Create a module in `database_agent/schema_inspector.py`.
    * [ ]  Implement functions to:
        * [ ]  Fetch the list of tables in the Supabase database.
        * [ ]  Fetch the columns and their data types for a given table.
        * [ ]  Store the schema in an appropriate data structure (e.g., a dictionary).

* **Task 7: Implement Dynamic Pydantic Model Generation & Caching**
    * [x]  Create a module in `models/model_generator.py`.
    * [x]  Implement a function `get_or_create_model(table: str, columns: dict) -> Type[BaseModel]`:
        * [x]  Takes a table name and a dictionary of column names and their data types.
        * [x]  Dynamically creates a Pydantic model class with fields corresponding to the columns.
        * [ ]  Handles mapping Supabase data types to Pydantic field types.
        * [x]  Adds a `Config` class to allow population by alias, if needed.
    * [x]  Implement a caching mechanism for generated models.
    * [ ]  Implement cache clearing on schema change.

## III. Core Workflows: Insert/Upsert and Fetch/List

* **Task 8: Implement Category Classification**
    * [x]  Create a module in `database_agent/category_classifier.py`.
    * [x]  Implement a function `classify_category(data: dict, existing_categories: List[str]) -> str`:
        * [x]  Takes the input data and a list of existing category names.
        * [x]  Uses PydanticAI to interact with the LLM.
        * [x]  Constructs a prompt (see "LLM Prompt Testing" below).
        * [ ]  Parses the LLM response to extract the category.
        * [ ]  Returns the suggested category.

* **Task 9: Implement Category Persistence**
    * [ ]  In `database_agent/database_operations.py`, implement functions to:
        * [ ]  Check if a category exists in the `categories` table.
        * [ ]  Insert a new category into the `categories` table if it doesn't exist.

* **Task 10: Implement Insert/Upsert Handler**
    * [ ]  In `database_agent/database_operations.py`, implement a function `handle_insert(table_name: str, data: dict, schema_changes: bool = False) -> dict`:
        * [ ]  Takes the table name, data payload, and a flag indicating whether schema changes are allowed.
        * [ ]  Retrieves the Pydantic model for the table from the cache (or generates it if it's not cached).
        * [ ]  Validates the data against the Pydantic model using `model_instance = model(**data)`.
        * [ ]  Calls `classify_category()` to get the category.
        * [ ]  Calls the category persistence functions to ensure the category exists.
        * [ ]  If `schema_changes` is `True` and the model validation fails due to missing fields:
            * [ ]  Return an error.  Do *not* attempt to modify the schema here.  Schema changes are handled in Task 12.
        * [ ]  Performs an upsert operation using the Supabase client.
        * [ ]  Constructs and returns a response dictionary (see "Response Schema" in the plan).
        * [ ]  Handles potential errors (e.g., database errors, validation errors).

* **Task 11: Implement Fetch/List Handler**
    * [ ]  In `database_agent/agent.py`, implement a function `handle_fetch(table: str, filters: dict = None) -> dict`:
        * [ ]  Takes the table name and optional filters.
        * [ ]  Constructs a Supabase query using `.select()` and `.filter()` (if filters are provided).
        * [ ]  Executes the query.
        * [ ]  Serializes the results into JSON.
        * [ ]  Constructs and returns a response dictionary (see "Response Schema" in the plan).
        * [ ]  Handles the case where no data is found.

## IV. Schema Evolution and Utility

* **Task 12: Implement Schema Command Handler**
    * [ ]  In `database_agent/database_operations.py`, implement a function `handle_schema_command(command: dict) -> dict`:
        * [ ]  Handles CREATE TABLE and ADD COLUMN requests.
        * [ ]  Issues the corresponding SQL via Supabase.
        * [ ]  Refreshes the model cache.
        * [ ]  Returns a structured response.

## V. Testing and Validation

* **Task 13: Write Unit and Integration Tests**
    * [ ]  Mirror the app structure under `/tests`.
    * [ ]  Add unit tests for:
        * [ ]  Supabase client
        * [ ]  Schema introspection
        * [ ]  Model generation and caching
        * [ ]  Category classification
        * [ ]  Insert/upsert handler
        * [ ]  Fetch/list handler
        * [ ]  Schema command handler

* **Task 14: Integration Testing**
    * [ ]  Validate end-to-end flows against a test Supabase instance.

## VI. Logging, Error Handling, and Documentation

* **Task 15: Logging and Exception Handling**
    * [ ]  Add robust logging throughout the agent.
    * [ ]  Ensure clear, structured error responses.

* **Task 16: Documentation**
    * [ ]  Update README with setup, usage, and details.
    * [ ]  Document environment variable requirements in `.env.example`.

## VII. LLM Prompt Testing

* **Task 17: Implement LLM Prompt Testing**
    * [ ]  Create a file `prompts.md`.
    * [ ]  Document the prompt used in the `classify_category` function.
    * [ ]  Include example inputs (data and existing categories) and expected LLM outputs.
    * [ ]  Iterate on the prompt in this file until it reliably produces the desired results.  Consider edge cases and variations in input data.
    * [ ]  Example Prompt Structure (in `prompts.md`):
        ```
        You are a helpful assistant that categorizes data.
        
        Here are some existing categories: {existing_categories}
        
        Please provide a single, concise category for the following data: {data}
        
        If the data fits an existing category, return that category.  If not, suggest a new, single-word category.
        
        Example 1:
        Existing categories: ["electronics", "clothing", "books"]
        Data: {"name": "Laptop", "price": 1200}
        Output: electronics
        
        Example 2:
        Existing categories: ["electronics", "clothing", "books"]
        Data: {"name": "T-Shirt", "size": "M"}
        Output: clothing
        
         Example 3:
        Existing categories: ["electronics", "clothing", "books"]
        Data: {"name": "Gardening Gloves", "type": "work"}
        Output: home_and_garden
    * [ ]  Update the project's `README.md` file with:
        * [ ]  A description of the DatabaseAgent.
        * [ ]  Instructions on how to set up the project (including environment variables).
        * [ ]  Instructions on how to run the agent.
        * [ ]  Examples of how to use the agent's methods.
        * [ ]  Information about the tech stack.
        * [ ]  Information about the design considerations.
