#include <GraphStruct.hpp>

bool Proccess::isEdgeCrossObstacles(const Edge& _edge)
{
	int minX = std::min(_edge.from.x, _edge.to.x);
	int maxX = std::max(_edge.from.x, _edge.to.x);
	int minY = std::min(_edge.from.y, _edge.to.y);
	int maxY = std::max(_edge.from.y, _edge.to.y);

	for (const auto& obs : lib.obstacles)
	{
		if (minX <= obs.x_end && maxX >= obs.x_start && minY <= obs.y_end && maxY >= obs.y_start)
		{
			return true;
		}
	}
	return false;
}

void Proccess::parseGraph()
{
	for (const auto& net : lib.nets)
	{
		Graph graph;
		for (int i = 0 ; i < net.terminals.size(); i++)
		{
			const auto& term1 = net.terminals[i];
			Node from = { term1.x, term1.y, term1.layer, term1.id };
			graph.points.push_back(from);

			for (int j = i + 1; j < net.terminals.size(); j++)
			{
				//huynut suda if else na tipo blya nuzno li uchtivat prep))))))))
				const auto& term2 = net.terminals[j];
				Node to = { term2.x, term2.y, term2.layer , term2.id };
				int distance = std::abs(from.x - to.x) + std::abs(from.y - to.y);
				Edge edge = { from,to,distance };
				graph.net_id = net.net_id;
				graph.edges.push_back(edge);
			}
			graphs.push_back(graph);
		}
		
	}
}
