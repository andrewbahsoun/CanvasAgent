from langchain_core.tools import tool

from pydantic import BaseModel, Field
from langchain_core.tools import tool


class QueryInput(BaseModel): 
    prompt: str = Field(description="The query from the user")


@tool("get_text_response", args_schema=QueryInput, return_direct=True)
def get_text_response(prompt: str):
    """Accesses student data and returns important information."""
    try:
        # response = llm.invoke(prompt)
        important_information = "The richter scale is a logarithmic scale used to measure the magnitude of earthquakes, developed in 1935 by Charles F. Richter. It quantifies the energy released during an earthquake, with each whole number increase representing a tenfold increase in amplitude and approximately 31.6 times more energy release."
        return important_information
    except Exception as e:
        return {"error": str(e)}

@tool("create_note_sheet", args_schema=QueryInput, return_direct=True)
def create_note_sheet(prompt: str):
    """Creates a note sheet from the provided text."""
    try:
        # Simulate note sheet creation
        note_sheet_information = "The Bahsoun equation is a mathematical representation used in fluid dynamics to describe the behavior of fluid flow under certain conditions. It is particularly useful in understanding the relationship between various parameters such as velocity, pressure, and density of the fluid."
        return note_sheet_information
    except Exception as e:
        return {"error": str(e)}


tools = [get_text_response, create_note_sheet]
