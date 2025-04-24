# Tasks for AI Coding Agent: DatabaseAgent Implementation

This document outlines the tasks required to implement the DatabaseAgent as described in the plan. Each task is a specific coding task.

## I. Project Setup and Core Components

* **Task 1: Set up Project Structure**
    * [ ]  Create the following directories:
        * `database_agent/` (for the main agent code)
        * `models/` (for Pydantic models)
        * `utils/` (for utility functions)
        * `tests/` (for unit and integration tests)

* **Task 2: Install Dependencies**
    * [ ]  Add the following packages to `requirements.txt`:
        * `pydantic`
        * `pydantic_ai`
        * `supabase`
        * `python-dotenv`
        * `any LLM library (e.g., openai, anthropic)`
    * [ ]  Install the dependencies using `pip install -r requirements.txt`.

## II. Database Interaction and Model Generation

* **Task 4: Implement Supabase Client Initialization**
    * [ ]  Create a module in `database_agent/supabase_client.py`.
    * [ ]  Implement a function to initialize the Supabase client using the `supabase-py` library and the environment variables.
    * [ ]  Ensure the client is a singleton or globally accessible.

* **Task 5: Implement Schema Introspection**
    * [ ]  Create a module in `database_agent/schema_inspector.py`.
    * [ ]  Implement functions to:
        * [ ]  Fetch the list of tables in the Supabase database.
        * [ ]  Fetch the columns and their data types for a given table.
        * [ ]  Store the schema in an appropriate data structure (e.g., a dictionary).

* **Task 6: Implement Dynamic Pydantic Model Generation**
    * [ ]  Create a module in `models/model_generator.py`.
    * [ ]  Implement a function `create_pydantic_model(table_name: str, columns: dict) -> Type[BaseModel]`:
        * [ ]  Takes a table name and a dictionary of column names and their data types.
        * [ ]  Dynamically creates a Pydantic model class with fields corresponding to the columns.
        * [ ]  Handles mapping Supabase data types to Pydantic field types.
        * [ ]  Adds a `Config` class to allow population by alias, if needed.

* **Task 7: Implement Model Caching**
    * [ ]  In `models/model_generator.py`, implement a caching mechanism for the generated Pydantic models.
    * [ ]  Store models in a dictionary with the table name as the key.
    * [ ]  Implement functions to:
        * [ ]  Retrieve a model from the cache if it exists.
        * [ ]  Add a model to the cache.
        * [ ]  Clear the cache (to be used when the schema changes).

## III. Core Workflows: Insert/Upsert and Fetch/List

* **Task 8: Implement Category Classification**
    * [ ]  Create a module in `database_agent/category_classifier.py`.
    * [ ]  Implement a function `classify_category(data: dict, existing_categories: List[str]) -> str`:
        * [ ]  Takes the input data and a list of existing category names.
        * [ ]  Uses PydanticAI to interact with the LLM.
        * [ ]  Constructs a prompt (see "LLM Prompt Testing" below).
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
    * [ ]  In `database_agent/database_operations.py`, implement a function `handle_fetch(table_name: str, filters: dict = None) -> dict`:
        * [ ]  Takes the table name and optional filters.
        * [ ]  Constructs a Supabase query using `.select()` and `.filter()` (if filters are provided).
        * [ ]  Executes the query.
        * [ ]  Serializes the results into JSON.
        * [ ]  Constructs and returns a response dictionary (see "Response Schema" in the plan).
        * [ ]  Handles the case where no data is found.

## IV. Schema Evolution

* **Task 12: Implement Schema Evolution Handler**
    * [ ]  Create a module in `database_agent/schema_evolution.py`.
    * [ ]  Implement a function `handle_schema_command(command: dict) -> dict`:
        * [ ]  Takes a dictionary representing the schema command (e.g., `{ "type": "add_column", "table": "my_table", "column": "new_column", "data_type": "text" }`).
        * [ ]  Validates the command structure.
        * [ ]  If the command type is "add_column":
            * [ ]  Executes the `ALTER TABLE ... ADD COLUMN` SQL command using the Supabase client's `.rpc()` or `.sql.execute()` method.
            * [ ]  Clears the Pydantic model cache for the table.
            * [ ]  Returns a success/failure message.
        * [ ]  If the command type is "create_table":
            * [ ]  Executes the `CREATE TABLE ...` SQL command using the Supabase client's `.rpc()` or `.sql.execute()` method.
             * [ ]  Clears the Pydantic model cache.
            * [ ]  Returns a success/failure message.
        * [ ]  Handles errors (e.g., invalid command, database errors).

## V. Agent Interface and Testing

* **Task 13: Implement Agent Interface**
    * [ ]  Create a module in `database_agent/agent.py`.
    * [ ]  Create a class `DatabaseAgent` with the following methods:
        * [ ]  `handle_insert(data: dict, schema_changes: bool = False) -> dict`: Calls the `handle_insert` function from `database_operations.py`.
        * [ ]  `handle_fetch(table: str, filters: dict = None) -> dict`: Calls the `handle_fetch` function from `database_operations.py`.
        * [ ]  `handle_schema_command(command: dict) -> dict`: Calls the `handle_schema_command` function from `schema_evolution.py`.

* **Task 14: Implement LLM Prompt Testing**
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
        ```

* **Task 15: Implement Integration Tests**
    * [ ]  Create test files in the `tests/` directory.
    * [ ]  Write integration tests to validate the end-to-end workflows:
        * [ ]  Test inserting data with and without schema changes.
        * [ ]  Test fetching data with and without filters.
        * [ ]  Test adding columns and creating tables.
        * [ ]  Test the category classification with various inputs.
    * [ ]  Use a test Supabase instance for the tests.
    * [ ]  Use a testing framework like `pytest`.
    * [ ]  Ensure tests cover success and failure scenarios.

## VI. Documentation

* **Task 16: Update README.md**
    * [ ]  Update the project's `README.md` file with:
        * [ ]  A description of the DatabaseAgent.
        * [ ]  Instructions on how to set up the project (including environment variables).
        * [ ]  Instructions on how to run the agent.
        * [ ]  Examples of how to use the agent's methods.
        * [ ]  Information about the tech stack.
        * [ ]  Information about the design considerations.