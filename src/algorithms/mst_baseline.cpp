#include "GraphStruct.hpp"

#include <algorithm>
#include <unordered_set>
#include <queue>

bool compare(const Edge& _edge1, const Edge& _edge2)
{
	return _edge1.distance < _edge2.distance;
}

struct CompareEdges {
	bool operator()(const Edge& e1, const Edge& e2) {
		return e1.distance > e2.distance;
	}
};

std::string Graph::find_set(std::string i) {
	if (i == parent[i])
		return i;
	else
		return find_set(parent[i]);
}
void Graph::union_set(std::string u, std::string v) {
	parent[u] = v;
}
void Graph::kruskal()
{
	std::sort(edges.begin(), edges.end(), compare);
	
	for (auto const& edge : edges)
	{
		std::string uRep = find_set(edge.from.id);
		std::string vRep = find_set(edge.to.id);
		if (uRep != vRep) {
			mst.push_back(edge);
			union_set(uRep, vRep);
		}
		else continue;
	}
}

void Graph::primma()
{

	std::unordered_set<std::string> visited;
	std::priority_queue<Edge, std::vector<Edge>, CompareEdges> pq;
	pq.push({this->nodes[0], this->nodes[0], 0});

	weight = 0;

	while (!pq.empty()) {
		Edge current = pq.top();
		pq.pop();

		Node u = current.to;
		
		if (visited.count(u.id)) continue;

		visited.insert(u.id);
		weight += current.distance;

		if (current.from.id != current.to.id) {
			mst.push_back(current);
		}

		auto it = adj.find(u.id);
		if (it != adj.end()) {
			for (const Edge& edge : it->second) {
				if (visited.count(edge.to.id) == 0) {
					pq.push(edge);

				}
			}
		}
	}
	visited.clear();
};