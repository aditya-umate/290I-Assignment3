from fastapi import FastAPI, File, UploadFile
from typing_extensions import Annotated
import uvicorn
from utils import *
from dijkstra import dijkstra

# create FastAPI app
app = FastAPI()

# global variable for active graph
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}


@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile):
    global active_graph
    if not file.filename.endswith('.json'):
        active_graph = None
        return {"Upload Error": "Invalid file type"}
    try:
        active_graph = create_graph_from_json(file)
        return {"Upload Success": file.filename}
    except Exception as e:
        return {"Upload Error": str(e)}


@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    global active_graph
    if active_graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."}
    if start_node_id not in active_graph.nodes or end_node_id not in active_graph.nodes:
        return {"Solver Error": "Invalid start or end node ID."}
    # Dijkstra's algorithm on the uploaded graph
    graph_result = dijkstra(active_graph, active_graph.nodes[start_node_id])
    path_nodes = []
    current = graph_result.nodes[end_node_id]
    # Backtrack to find shortest path
    while current is not None:
        path_nodes.append(current.id)
        current = current.prev
    path_nodes.reverse()
    # If unreachable, check for infinite distance
    if graph_result.nodes[end_node_id].dist == float('inf'):
        return {"shortestpath": None, "totaldistance": None}
    return {"shortestpath": path_nodes, "totaldistance": graph_result.nodes[end_node_id].dist}

if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
    