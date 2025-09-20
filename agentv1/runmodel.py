from graph import graph


with open("graph.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())
print("Saved as graph.png")

inputs = {"messages": [("system", "You are a helpful assistant that helps with creating note sheets and answering questions using tools.")], "number_of_steps": 0}

for state in graph.stream(inputs, stream_mode="values"):
    last_message = state["messages"][-1]
    last_message.pretty_print()

state["messages"].append(("human", "create a note sheet about the bahsoun equation"))

for state in graph.stream(state, stream_mode="values"):
    last_message = state["messages"][-1]
    last_message.pretty_print()


