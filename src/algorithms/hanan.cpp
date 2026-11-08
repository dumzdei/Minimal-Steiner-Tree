#include "hanan.hpp"
#include<set>

void createCandidateNodesToSteiner(Graph* graph, std::string& GenerateType)
{
	if (GenerateType == "hanan")
	{
		std::set<int> xSet = {};
		std::set<int> ySet = {};
		//createHanan;
		for (Node* node : graph->nodes)
		{
			xSet.insert(node->x);
			ySet.insert(node->y);
		}
		std::vector<int> xValues(xSet.begin(), xSet.end());
		std::vector<int> yValues(ySet.begin(), ySet.end());
		for (const auto& x_ : xValues) {
			for (const auto& y_ : yValues) {
				bool have = false;
				Node* point = new Node( x_, y_ );
				for (Node* _node : graph->nodes) {
					if (_node == point) {
						have = true;
						break;
					}
				}
				if (!have)
					graph->CandidateNodesToSteiner.push_back(point);
			}
		}
		xSet.clear();
		ySet.clear();
		xValues.clear();
		yValues.clear();
	}
	else if (GenerateType == "hanan_extended")
	{//create hanan + 1/2 mst
		for (const Edge* _edge : graph->mst)
		{
			Node* point = new Node( (_edge->from->x + _edge->to->x) / 2 , 
						(_edge->from->x + _edge->to->x) / 2);
			graph->CandidateNodesToSteiner.push_back(point);
		}
	}
	else if (GenerateType == "grid_all")
	{
		//create all nodes:
	}
}