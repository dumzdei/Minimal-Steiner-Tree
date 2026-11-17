#include <json.hpp>
#include <GraphStruct.hpp>
using json = nlohmann::json;

Node::Node(int x, int y) {
	this->x = x;
	this->y = y;
}

Node::~Node() 
{

}

Edge::~Edge() 
{

}

Graph::Graph(Process* work, const Net& net) {
	this->net_id = net.net_id;
	for (int i = 0; i < net.terminals.size(); i++)
	{
		const auto& term1 = net.terminals[i];
		Node* node = new Node(term1);
		this->nodes.push_back(node);

	}

	for (size_t from = 0; from < this->nodes.size(); from++)
	{
		unsigned to = from;

		while (to != this->nodes.size())
		{
			Edge* edge = new Edge(this->nodes[from], this->nodes[to]);
			if (work->isEdgeCrossObstacles(edge)) 
				delete edge;
			else
				this->edges.push_back(edge);
			
			to++;
		}
	}
}

Graph::~Graph() {
	for (Edge* edge : this->edges) 
	{
		delete edge;
	}
	for (Node* node : this->nodes)
	{
		delete node;
	}
	for (Node* node : this->CandidateNodesToSteiner) 
	{
		delete node;
	}
}

Edge::Edge(Node* from, Node* to) {
	this->from = from;
	this->to = to;
	if (from == to) this->distance = 0;
	else this->distance = std::abs(from->x - to->x) + std::abs(from->y - to->y);
}

Node::Node(const Terminal& term) {
	this->x = term.x;
	this->y = term.y;
	this->layer = term.layer;
	this->id = term.id;
}

bool Process::isEdgeCrossObstacles(const Edge* _edge)
{
	int minX = std::min(_edge->from->x, _edge->to->x);
	int maxX = std::max(_edge->from->x, _edge->to->x);
	int minY = std::min(_edge->from->y, _edge->to->y);
	int maxY = std::max(_edge->from->y, _edge->to->y);

	for (const auto& obs : lib.obstacles)
	{
		//if (obs.layer != _edge->from->layer || obs.layer != _edge->to->layer) continue;

		if (minX <= obs.x_end && maxX >= obs.x_start && minY <= obs.y_end && maxY >= obs.y_start)
		{
			return true;
		}
	}
	return false;
}

void Process::parseGraphs()
{
	for (const auto& net : lib.nets)
	{
		Graph* graph = new Graph(this, net);
		
		graphs.push_back(graph);
	}

	for (Graph* graph : graphs) 
	{
		for ( Edge* edge : graph->edges) 
		{
			graph->adj[edge->from->id].push_back(edge);
			graph->adj[edge->to->id].push_back(edge);

		}
	}
	for (Graph* graph : graphs)
	{
		for (auto node : graph->nodes)
		{
			graph->parent[node->id] = node->id;
		}
	}

}

void Process::writeGraphsToFile(std::ostream& out) {
	json root;
	root["nets"] = json::array(); 

	for (const auto& graph : graphs) {
		json net_json;
		net_json["net_id"] = graph->net_id;
		net_json["edges"] = json::array();

		for (const auto& edge : graph->mst) {
			json edge_json;

			edge_json["from"] = {
				{ "x", edge->from->x },
				{ "y", edge->from->y }
			};

			edge_json["to"] = {
				{ "x", edge->to->x },
				{ "y", edge->to->y }
			};

			net_json["edges"].push_back(edge_json);
		}
		root["nets"].push_back(net_json);

	}

	out << root.dump(2) << std::endl;
}

Process::~Process() {
	for (Graph* graph : graphs)
	{
		delete(graph);
	}
}



