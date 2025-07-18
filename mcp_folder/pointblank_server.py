import json
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Annotated,
    Any,
    AsyncIterator,
    Dict,
    Optional,
    Union,
)

import pandas as pd
from fastmcp import Context, FastMCP
from fastmcp.prompts.prompt import Message
from pydantic import Field

import pointblank as pb


# --- Lifespan Context: manage DataFrames and Validators ---
@dataclass
class AppContext:
    # Stores loaded DataFrames: {df_id: DataFrame}
    loaded_dataframes: Dict[str, pd.DataFrame] = field(default_factory=dict)
    # Stores active Pointblank Validators: {validator_id: Validate}
    active_validators: Dict[str, pb.Validate] = field(default_factory=dict)


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    context = AppContext()
    yield context
    context.loaded_dataframes.clear()
    context.active_validators.clear()


mcp = FastMCP(
    "FlexiblePointblankMCP",
    lifespan=app_lifespan,
    dependencies=["pandas", "pointblank", "openpyxl", "polars"],
)


def _load_dataframe_from_path(input_path: str) -> pd.DataFrame:
    p_path = Path(input_path)
    if not p_path.exists():
        raise FileNotFoundError(f"Input file '{input_path}' not found.")
    if p_path.suffix.lower() == ".csv":
        return pd.read_csv(p_path)
    elif p_path.suffix.lower() in [".xls", ".xlsx"]:
        return pd.read_excel(p_path, engine="openpyxl")
    elif p_path.suffix.lower() == ".parquet":
        return pd.read_parquet(p_path)
    else:
        raise ValueError(f"Unsupported file type: {p_path.suffix}. Please use CSV or Excel.")


@dataclass
class DataFrameInfo:
    df_id: str
    shape: tuple
    columns: list


@mcp.tool(
    name="load_dataframe",
    description="Load a DataFrame from a CSV, Excel or Parquet file into the server's context.",
    tags={"Data Management"},
)
async def load_dataframe(
    ctx: Context,
    input_path: Annotated[str, Field(description="Path to the input CSV, Excel or Parquet file.")],
    df_id: Optional[
        Annotated[
            str,
            Field(
                description="Optional ID for the DataFrame. If not provided, a new ID will be generated."
            ),
        ]
    ] = None,
) -> DataFrameInfo:
    """
    Loads a DataFrame from the specified CSV or Excel file into the server's context.
    Assigns a unique ID to the DataFrame for later reference.
    If df_id is not provided, a new one will be generated.
    Returns the DataFrame ID and basic information (shape, columns).
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context
    df = _load_dataframe_from_path(input_path)

    effective_df_id = df_id if df_id else f"df_{uuid.uuid4().hex[:8]}"

    if effective_df_id in app_ctx.loaded_dataframes:
        raise ValueError(
            f"DataFrame ID '{effective_df_id}' already exists. Choose a different ID or omit to generate a new one."
        )

    app_ctx.loaded_dataframes[effective_df_id] = df

    return DataFrameInfo(
        df_id=effective_df_id,
        shape=df.shape,
        columns=list(df.columns),
    )


@dataclass
class ValidatorInfo:
    validator_id: str


@mcp.tool(
    name="create_validator",
    description="Create a Pointblank Validator for a previously loaded DataFrame.",
    tags={"Validation"},
)
def create_validator(
    ctx: Context,
    df_id: Annotated[str, Field(description="ID of the DataFrame to validate.")],
    validator_id: Annotated[
        Optional[str],
        Field(
            description="Optional ID for the Validator. If not provided, a new ID will be generated."
        ),
    ] = None,
    table_name: Annotated[
        Optional[str],
        Field(
            description="Optional name for the table within Pointblank reports. If not provided, a default name will be used."
        ),
    ] = None,
    validator_label: Annotated[
        Optional[str],
        Field(
            description="Optional descriptive label for the Validator. If not provided, a default label will be used."
        ),
    ] = None,  # Corresponds to 'label' in pb.Validate
    thresholds_dict: Annotated[
        Optional[Dict[str, Union[int, float]]],
        Field(
            description="Optional thresholds for validation failures. Example: {'warning': 0.1, 'error': 5, 'critical': 0.10}. "
            "If not provided, no thresholds will be set."
        ),
    ] = None,  # Corresponds to 'thresholds' in pb.Validate, e.g. {"warning": 1, "error": 20, "critical": 0.10}
    actions_dict: Optional[Dict[str, Any]] = None,  # Simplified, for pb.Actions
    final_actions_dict: Optional[Dict[str, Any]] = None,  # Simplified, for pb.FinalActions
    brief: Optional[bool] = None,
    lang: Optional[str] = None,
    locale: Optional[str] = None,
) -> ValidatorInfo:
    """
    Creates a Pointblank Validator for a previously loaded DataFrame.
    Assigns a unique ID to the Validator for adding validation steps.
    If validator_id is not provided, a new one will be generated.
    'df_id' must refer to a DataFrame loaded via 'load_dataframe'.
    'table_name' is an optional name for the table within Pointblank reports.
    'validator_label' is an optional descriptive label for the validator.
    'thresholds_dict' can be like {"warning": 0.1, "error": 5} to set failure thresholds.
    Returns the Validator ID.
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context

    if df_id not in app_ctx.loaded_dataframes:
        raise ValueError(
            f"DataFrame ID '{df_id}' not found. Please load it first using 'load_dataframe'."
        )

    df = app_ctx.loaded_dataframes[df_id]

    effective_validator_id = validator_id if validator_id else f"validator_{uuid.uuid4().hex[:8]}"

    if effective_validator_id in app_ctx.active_validators:
        raise ValueError(
            f"Validator ID '{effective_validator_id}' already exists. Choose a different ID or omit to generate a new one."
        )

    actual_table_name = table_name if table_name else f"table_for_{df_id}"
    actual_validator_label = (
        validator_label if validator_label else f"Validation for {actual_table_name}"
    )

    # Construct Thresholds, Actions, FinalActions if dicts are provided
    pb_thresholds = None
    if thresholds_dict:
        try:
            pb_thresholds = pb.Thresholds(**thresholds_dict)
        except Exception as e:
            raise ValueError(f"Error creating pb.Thresholds from thresholds_dict: {e}")

    # Note: pb.Actions and pb.FinalActions might require more complex construction
    # For simplicity, we're assuming direct kwarg passing or simple structures.
    # This part might need refinement based on how pb.Actions/pb.FinalActions are instantiated.
    pb_actions = None
    if actions_dict:
        try:
            # Example: if pb.Actions takes specific function handlers
            # This is a placeholder and likely needs more specific handling
            pb_actions = pb.Actions(
                **actions_dict
            )  # This assumes pb.Actions can be created this way
        except Exception as e:
            print(f"Could not create pb.Actions from actions_dict: {e}. Passing None.")

    pb_final_actions = None
    if final_actions_dict:
        try:
            pb_final_actions = pb.FinalActions(**final_actions_dict)  # Placeholder
        except Exception as e:
            print(f"Could not create pb.FinalActions from final_actions_dict: {e}. Passing None.")

    validator_instance_params = {
        "data": df,
        "tbl_name": actual_table_name,
        "label": actual_validator_label,
    }

    if pb_thresholds:
        validator_instance_params["thresholds"] = pb_thresholds
    if pb_actions:
        validator_instance_params["actions"] = pb_actions
    if pb_final_actions:
        validator_instance_params["final_actions"] = pb_final_actions
    if brief is not None:
        validator_instance_params["brief"] = brief
    if lang:
        validator_instance_params["lang"] = lang
    if locale:
        validator_instance_params["locale"] = locale

    validator_instance = pb.Validate(**validator_instance_params)
    app_ctx.active_validators[effective_validator_id] = validator_instance

    return ValidatorInfo(validator_id=effective_validator_id)


@dataclass
class ValidationStepInfo:
    validator_id: str
    status: str


@mcp.tool(
    name="add_validation_step",
    description="Add a validation step to an existing Pointblank Validator.",
    tags={"Validation"},
)
def add_validation_step(
    ctx: Context,
    validator_id: Annotated[str, Field(description="ID of the Validator to add a step to.")],
    validation_type: Annotated[
        str,
        Field(
            description="Type of validation to perform. Supported types include: 'col_vals_lt', 'col_vals_gt', 'col_vals_between', 'col_exists', 'rows_distinct', etc."
        ),
    ],
    params: Annotated[
        Dict[str, Any],
        Field(
            description="Parameters for the validation function. This should match the expected parameters for the Pointblank validation method."
        ),
    ],
    actions_config: Optional[Dict[str, Any]] = None,  # Placeholder for simplified action definition
) -> ValidationStepInfo:
    """
    Adds a validation step to an existing Pointblank Validator.
    'validator_id' must refer to a validator created via 'create_validator'.
    'validation_type' specifies the Pointblank validation function to call
      (e.g., 'col_vals_lt', 'col_vals_between', 'col_vals_in_set', 'col_exists', 'rows_distinct').
    'params' is a dictionary of parameters for that validation function.
    'actions_config' (optional) can be used to define simple actions (currently basic support).
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context

    if validator_id not in app_ctx.active_validators:
        raise ValueError(
            f"Validator ID '{validator_id}' not found. Please create it first using 'create_validator'."
        )

    validator = app_ctx.active_validators[validator_id]

    # --- Define supported validation types and their methods from pb.Validate ---
    # This mapping allows dynamic dispatch and can be extended
    # Methods are called on the 'validator' (pb.Validate instance)
    supported_validations = {
        # Column value validations
        "col_vals_lt": validator.col_vals_lt,  # less than a value
        "col_vals_gt": validator.col_vals_gt,  # greater than a value
        "col_vals_lte": validator.col_vals_le,  # less or equal
        "col_vals_gte": validator.col_vals_ge,  # greater or equal
        "col_vals_equal": validator.col_vals_eq,  # equal to a value
        "col_vals_not_equal": validator.col_vals_ne,  # not equal to a value
        "col_vals_between": validator.col_vals_between,  # data lies between two values left=val, right=val
        "col_vals_not_between": validator.col_vals_outside,  # data is outside two values
        "col_vals_in_set": validator.col_vals_in_set,  # values in a set e.g. [1,2,3]
        "col_vals_not_in_set": validator.col_vals_not_in_set,  # values not in a set
        "col_vals_null": validator.col_vals_null,  # null values
        "col_vals_not_null": validator.col_vals_not_null,  # not null values
        "col_vals_regex": validator.col_vals_regex,  # values match a regular expresion
        "col_vals_expr": validator.col_vals_expr,  # Validate column values using a custom expression
        "col_count_match": validator.col_count_match,  # Validate whether the column count of the table matches a specified count.
        # Check existence of a column
        "col_exists": validator.col_exists,
        # Row validations
        "rows_distinct": validator.rows_distinct,  # distinc rows in a table
        "rows_complete": validator.rows_complete,  # Check for no NAs in specified columns
        "row_count_match": validator.row_count_match,  # Check if number of rows in the table matches a fixed value
        # Other specialized validations
        "conjointly": validator.conjointly,  # For multiple column conditions
        "col_schema_match": validator.col_schema_match,  # Do columns in the table (and their types) match a predefined schema? columns=[("a", "String"), ("b", "Int64"), ("c", "Float64")]
    }

    if validation_type not in supported_validations:
        raise ValueError(
            f"Unsupported validation_type: '{validation_type}'. Supported types include: {list(supported_validations.keys())}"
        )

    validation_method = supported_validations[validation_type]

    # Simplified actions handling (can be expanded)
    # pb.Validate methods expect an 'actions' parameter which is an instance of pb.Actions
    # This is a placeholder for how one might construct it.
    # A more robust solution would deserialize a dict into pb.Actions object.
    current_params = {**params}
    if actions_config:
        # Example: actions_config = {"warn": 0.1} might translate to
        # actions = pb.Actions(warn_fraction=0.1)
        # For now, if a method expects 'actions', it should be in params directly
        # or handled here explicitly if simple shorthands are desired.
        # This is a complex area to generalize perfectly via JSON.
        # Let's assume 'actions' if needed is part of 'params' and is a pb.Actions object
        # or the LLM constructs the params for methods that take thresholds directly.
        # For now, we'll pass 'params' as is.
        # If 'actions' is a direct parameter of the validation_method, it should be in 'params'.
        pass  # No special action processing here yet, assuming 'params' has all needed args
    try:
        validation_method(**current_params)
    except TypeError as e:
        raise ValueError(
            f"Error calling validation method '{validation_type}' with params {current_params}. Original error: {e}. Check parameter names and types against Pointblank's API for the '{validation_type}' method of the 'Validate' class."
        )
    except Exception as e:
        raise RuntimeError(
            f"An unexpected error occurred while adding validation step '{validation_type}': {e}"
        )

    return ValidationStepInfo(
        validator_id=validator_id,
        status=f"Validation step '{validation_type}' added successfully.",
    )


@dataclass
class ValidationOutput:
    status: str
    message: str
    output_file: Optional[str] = None


@mcp.tool(
    name="get_validation_step_output",
    description="Retrieve output for a validation step and save it to a CSV file.",
    tags={"Validation"},
)
async def get_validation_step_output(
    ctx: Context,
    validator_id: Annotated[str, Field(description="ID of the Validator to retrieve output from.")],
    output_path: Annotated[
        str,
        Field(description="Path to save the output file. Must end with .csv."),
    ],
    sundered_type: Annotated[
        str,
        Field(
            description="Mode 2: Retrieve all 'pass' or 'fail' rows for the *entire* validation run. Only used if 'step_index' is not provided."
        ),
    ] = "fail",
    step_index: Annotated[
        Optional[int],
        Field(
            description="Mode 1: Retrieve data for a *specific* step by its index (starting from 0). If used, 'sundered_type' is ignored."
        ),
    ] = None,
) -> ValidationOutput:
    """
    Retrieves validation output and saves it to a CSV file. This function has two modes:
    1.  Specific Step Extract: Provide a 'step_index' to get the data extract (e.g., failing rows) for that specific step.
    2.  Overall Sundered Data: Omit 'step_index' and use 'sundered_type' ('pass' or 'fail') to get all rows that met that condition across all validation steps.
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context

    if validator_id not in app_ctx.active_validators:
        raise ValueError(f"Validator ID '{validator_id}' not found.")
    validator = app_ctx.active_validators[validator_id]

    p_output_path = Path(output_path)
    if p_output_path.suffix.lower() != ".csv":
        raise ValueError(f"Unsupported file format '{p_output_path.suffix}'. Please use '.csv'.")

    if step_index is not None and step_index < 0:
        raise ValueError("The 'step_index' cannot be a negative number.")

    try:
        if not getattr(validator, "time_processed", None):
            await ctx.warning(
                f"Validator '{validator_id}' has not been interrogated. Interrogating now."
            )

        p_output_path.parent.mkdir(parents=True, exist_ok=True)
        message = ""
        data_extract_df = None

        # Pathway 1: Get data for a single, specific validation step.
        if step_index is not None:
            data_extract_df = validator.get_data_extracts(i=step_index, frame=True)
            if data_extract_df is None or data_extract_df.empty:
                message = f"No data extract available for step {step_index}. This may mean all rows passed this validation step."
                data_extract_df = None  # Ensure it's None if empty
            else:
                message = f"Data extract for step {step_index} retrieved."

        # Pathway 2: Get all 'fail' or 'pass' data from the entire validation run.
        else:
            data_extract_df = validator.get_sundered_data(type=sundered_type)
            if data_extract_df is None or data_extract_df.empty:
                message = f"No sundered data available for type '{sundered_type}'."
                data_extract_df = None  # Ensure it's None if empty
            else:
                message = f"Sundered data for type '{sundered_type}' retrieved."

        if data_extract_df is None:
            return ValidationOutput(
                status="success",
                message=message,
                output_file=None,
            )

        if isinstance(data_extract_df, pd.DataFrame):
            data_extract_df.to_csv(p_output_path, index=False)
            message = f"Data extract saved to {p_output_path.resolve()}"
        else:
            raise TypeError(
                f"Unsupported DataFrame type '{type(data_extract_df).__name__}' for CSV export."
            )

        await ctx.report_progress(100, 100, message)

        return ValidationOutput(
            status="success",
            message=message,
            output_file=str(p_output_path.resolve()),
        )

    except Exception as e:
        raise RuntimeError(f"Error getting output for validator '{validator_id}': {e}")


@mcp.tool(
    name="interrogate_validator",
    description="Run validations and return a JSON summary. Optionally save the report to a CSV file.",
    tags={"Validation"},
)
async def interrogate_validator(
    ctx: Context,
    validator_id: Annotated[str, Field(description="ID of the Validator to interrogate.")],
    report_file_path: Annotated[
        Optional[str],
        Field(
            description="Optional path to save the validation report. If provided, must end with .csv."
        ),
    ] = None,
) -> Dict[str, Any]:
    """
    Runs validations and returns a JSON summary.
    Optionally saves the report to 'report_file_path' as a CSV file.
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context

    if validator_id not in app_ctx.active_validators:
        raise ValueError(f"Validator ID '{validator_id}' not found.")

    validator = app_ctx.active_validators[validator_id]

    try:
        validator.interrogate()
        json_report_str = validator.get_json_report()
    except Exception as e:
        raise RuntimeError(f"Error during validator interrogation: {e}")

    output_dict = {"validation_summary": json.loads(json_report_str)}

    if report_file_path:
        p_report_file_path = Path(report_file_path)

        if not report_file_path.lower().endswith(".csv"):
            err_msg = "Unsupported report file extension. Use .csv."
            print(err_msg)
            output_dict["report_save_error"] = err_msg
            return output_dict

        p_report_file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            report_data = json.loads(json_report_str)
            df_report = pd.DataFrame(report_data)
            df_report.to_csv(p_report_file_path, index=False)
            file_saved_path = str(p_report_file_path.resolve())
            output_dict["csv_report_saved_to"] = file_saved_path
            await ctx.report_progress(100, 100, f"Report saved to {file_saved_path}")

        except Exception as e:
            error_msg = f"Failed to save report to {report_file_path}: {e}"
            print(error_msg)
            output_dict["report_save_error"] = error_msg

    return output_dict


@mcp.prompt(
    name="prompt_load_dataframe",
    description="Prompt to load a DataFrame from a file into the server's context for validation.",
    tags={"Data Management"},
)
def prompt_load_dataframe(
    input_path: str = Field(description="Path to the input CSV, Excel or Parquet file."),
    df_id: Optional[str] = Field(
        default=None,
        description="Optional ID for the DataFrame. If not provided, a new ID will be generated.",
    ),
) -> tuple:
    return (
        Message(
            "I can load your data from a file into my context for validation.",
            role="assistant",
        ),
        Message(
            f"Please call `load_dataframe` with input_path='{input_path}'. "
            f"You can optionally provide a `df_id` (e.g., '{df_id}') to name this dataset, "
            "or I will generate one for you. Make a note of the returned `df_id` for subsequent steps.",
            role="user",
        ),
    )


@mcp.prompt(
    name="prompt_create_validator",
    description="Prompt to create a Pointblank Validator for a loaded DataFrame.",
    tags={"Validation"},
)
def prompt_create_validator(
    df_id: Annotated[str, Field(description="ID of the DataFrame to validate.")] = "df_default",
    validator_id: Annotated[
        Optional[str],
        Field(
            description="Optional ID for the Validator. If not provided, a new ID will be generated."
        ),
    ] = "validator_default",
    table_name: Annotated[
        Optional[str],
        Field(
            description="Optional name for the table within Pointblank reports. If not provided, a default name will be used."
        ),
    ] = "data_table",
    validator_label: Annotated[
        Optional[str],
        Field(
            description="Optional descriptive label for the Validator. If not provided, a default label will be used."
        ),
    ] = "Validator",
    thresholds_dict_example: Annotated[
        Optional[Dict[str, Union[int, float]]],
        Field(
            description="Example thresholds for validation failures. If not provided, a default example will be used."
        ),
    ] = None,
) -> tuple:
    """
    Prompt guiding the LLM to create a Pointblank Validator object.
    Includes an example for thresholds_dict.
    """
    thresholds_msg_example = (
        thresholds_dict_example if thresholds_dict_example else {"warning": 0.05, "error": 10}
    )

    return (
        Message(
            "Once your data is loaded (using its `df_id`), I can create a 'Validator' object to define data quality checks.",
            role="assistant",
        ),
        Message(
            f"Please call `create_validator` using the `df_id` of your loaded data (e.g., '{df_id}').\n"
            f"You can optionally provide:\n"
            f"- `validator_id` (e.g., '{validator_id}') to name this validator instance.\n"
            f"- `table_name` (e.g., '{table_name}') as a reference name for the data table in reports.\n"
            f"- `validator_label` (e.g., '{validator_label}') for a descriptive label.\n"
            f"- `thresholds_dict` (e.g., {thresholds_msg_example}) to set global failure thresholds for validation steps.\n"
            f"- Other optional parameters like `actions_dict`, `final_actions_dict`, `brief`, `lang`, `locale` can also be specified if needed.\n"
            "Make a note of the returned `validator_id` to use when adding validation steps.",
            role="user",
        ),
    )


@mcp.prompt(
    name="prompt_add_validation_step_example",
    description="Prompt to add a validation step to a Pointblank Validator.",
    tags={"Validation"},
)
def prompt_add_validation_step_example() -> tuple:
    return (
        Message(
            "I can add various validation steps to your validator. "
            "You'll need to specify the 'validator_id', 'validation_type', and 'params' for the step. "
            "For example, to check if values in column 'age' are less than 100 for validator 'validator_123':",
            role="assistant",
        ),
        Message(
            "Please call `add_validation_step` with validator_id='validator_123', "
            "validation_type='col_vals_lt', and params={'columns': 'age', 'value': 100}. "
            "Note: Parameter names within 'params' (like 'columns', 'value', 'left', 'right', 'set_', etc.) must exactly match what the specific Pointblank validation function expects.\n"
            "Other examples:\n"
            "- For 'col_vals_between': params={'columns': 'score', 'left': 0, 'right': 100, 'inclusive': [True, True]}\n"
            "- For 'col_vals_in_set': params={'columns': 'grade', 'set_': ['A', 'B', 'C']} (Note: Pointblank uses 'set_' for this method's list of values)\n"
            "- For 'col_exists': params={'columns': 'user_id'}\n"
            "Refer to the Pointblank Python API for the 'Validate' class for available `validation_type` (method names) and their specific `params`.",
            role="user",
        ),
    )


@mcp.prompt(
    name="prompt_get_validation_step_output",
    description="Prompt to get validation output by specifying either a step index or a sundered type.",
    tags={"Validation"},
)
def prompt_get_validation_step_output(
    validator_id: Annotated[
        str, Field(description="Example ID of the Validator.")
    ] = "validator_123",
    step_index: Annotated[
        Optional[int],
        Field(description="Example step index for the first mode of operation."),
    ] = 0,
    sundered_type: Annotated[
        Optional[str],
        Field(
            description="Example sundered type ('pass' or 'fail') for the second mode of operation."
        ),
    ] = "fail",
) -> tuple:
    """
    Guides the LLM to get a validation output CSV by choosing one of two modes:
    1.  By a specific step index.
    2.  By the overall sundered data type ('pass' or 'fail').
    """
    return (
        Message(
            "I can extract validation data in two different ways. You must choose one: "
            "either get data for a *specific step* by its index, or get *all passed or failed rows* from the entire validation run.",
            role="assistant",
        ),
        Message(
            f"Please call the `get_validation_step_output` tool using only **one** of the following mutually exclusive options:\n\n"
            f"**OPTION 1: Get data for a specific step**\n"
            f"To get the data extract for step number {step_index}, use the `step_index` parameter. For example:\n"
            f"`get_validation_step_output(validator_id='{validator_id}', step_index={step_index}, output_path='step_{step_index}_data.csv')`\n\n"
            f"**OPTION 2: Get all passed or failed data**\n"
            f"To get all rows that '{sundered_type}' across all validation steps, use the `sundered_type` parameter. For example:\n"
            f"`get_validation_step_output(validator_id='{validator_id}', sundered_type='{sundered_type}', output_path='all_{sundered_type}_rows.csv')`",
            role="user",
        ),
    )


@mcp.prompt(
    name="prompt_interrogate_validator",
    description="Prompt to run validations and optionally save the report.",
    tags={"Validation"},
)
def prompt_interrogate_validator(
    validator_id: Annotated[str, Field(description="ID of the Validator to interrogate.")],
    report_file_path: Annotated[
        Optional[str],
        Field(description="Optional path to save the validation report as a CSV file."),
    ] = "optional_report.csv",
) -> tuple:
    """
    Prompt guiding the LLM to run validations and optionally save the report as a CSV file.
    """
    return (
        Message(
            "After all desired validation steps have been added to a validator, I can run the interrogation process. This will execute all checks.",
            role="assistant",
        ),
        Message(
            f"Please call `interrogate_validator` with the `validator_id` (e.g., '{validator_id}').\n"
            f"The main result will be a JSON object summarizing all validation steps.\n"
            f"Optionally, you can specify `report_file_path` to save the report to a CSV file. "
            f"For example, to save as a CSV file: `report_file_path='{report_file_path}'`\n"
            f"If `report_file_path` is not provided, the report will not be saved to a file.",
            role="user",
        ),
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
