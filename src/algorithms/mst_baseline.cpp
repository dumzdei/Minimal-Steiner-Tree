#include "GraphStruct.hpp"

#include <algorithm>
#include <unordered_set>

bool compare(const Edge& _edge1, const Edge& _edge2)
{
	return _edge1.distance < _edge2.distance;
}

void Graph::kruskal()
{
	std::sort(edges.begin(), edges.end(), compare);
	std::unordered_set <std::string> usedNodes = {};
	for (auto const& edge : edges)
	{
		auto n1 = edge.from;
		auto n2 = edge.to;
		if (!(usedNodes.find(n1.id) != usedNodes.end()) || !(usedNodes.find(n2.id) != usedNodes.end()) )
		{
			mst.push_back(edge);
			usedNodes.insert(n1.id);
			usedNodes.insert(n2.id);
		}
		else continue;
	}
	usedNodes.clear();
}

void Graph::primma()
{
}
;