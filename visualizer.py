import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import plot_bar_chart, plot_line_chart, plot_pie_chart, plot_scatter_chart, init_df_for_tools
from llm_factory import create_llm
from pathlib import Path
from prompts import VISUALIZER_PROMPT

file_path = "./data.csv"

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system", VISUALIZER_PROMPT
        ),
        (
            "human",
            """Dataset Information

Dataset Name:
{dataset_name}

Number of Rows:
{row_count}

Number of Columns:
{column_count}

Column Metadata:

{metadata}

Analyze the dataset and generate the most useful visualizations.

Focus on:

- trends over time
- comparisons between categories
- relationships between variables
- distributions of important numerical variables

Avoid:

- identifier columns
- low-value visualizations
- redundant visualizations
- invalid chart-column combinations"""
        )
    ]
)


llm = create_llm()

llm_with_tools = llm.bind_tools(
    [
        plot_line_chart,
        plot_scatter_chart,
        plot_bar_chart,
        plot_pie_chart
    ]
)

parser = StrOutputParser()

chain = prompt | llm_with_tools


def visualize(file_path):
    df = pd.read_csv(file_path)
    init_df_for_tools(file_path)

    metadata : list[dict] = []

    for col in df:
        metadata.append(
            {
                "column_name" : col,
                "column_type" : str(df[col].dtype),
                "unique_values" : df[col].nunique()
            }
        )


    response = chain.invoke({
            "dataset_name": Path(file_path).name,
            "row_count": len(df),
            "column_count": len(df.columns),
            "metadata": metadata
        })


    tool_map = {
        "plot_line_chart": plot_line_chart,
        "plot_scatter_chart": plot_scatter_chart,
        "plot_bar_chart": plot_bar_chart,
        "plot_pie_chart": plot_pie_chart
    }

    
    results = []

    used_signatures = set() #to avoid duplicate plots
    print("++++++++++++ TOOL CALLS ++++++++++++++")
    for tool_call in response.tool_calls:

        tool_name = tool_call["name"]
        args = tool_call["args"]

        print("Tool:", tool_name)
        print("Args:", args)

        tool_fn = tool_map.get(tool_name)

        if tool_fn is None:
            continue

        columns = []

        for value in args.values():
            if isinstance(value, str):
                columns.append(value)

        signature = (
            tool_name,
            tuple(sorted(columns))
        )

        if signature in used_signatures:

            print("\nDuplicate Visualization Skipped")
            print("Tool:", tool_name)
            print("Args:", args)

            continue

        used_signatures.add(signature)
        try : 
            result = tool_fn.invoke(args)

            if "error" in result:

                print("\nTool Validation Failed")
                print("Tool:", tool_name)
                print("Args:", args)
                print("Reason:", result["error"])

                continue

            results.append({
                "tool": tool_name,
                "args": args,
                "result": result
            })
        
        except Exception as e:

            print("\n\n!!!!!!!!!!!!!\n\nTool Execution Failed")
            print("Tool:", tool_name)
            print("Args:", args)
            print("Error:", str(e))

            continue
    print("+++++++++++ TOOL EXECUTION COMPLETED +++++++++++++")