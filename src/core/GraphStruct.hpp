#include "Configuration.hpp"
#include <map>
#include <string>
#include <vector>
/************************************************************************************
 *  @file   GraphStruct.hpp
 *  @brief  Description of data structures for working with graphs.
 ***********************************************************************************/

struct Node
{
	int			x = 0,
				y = 0;
	std::string layer,
				id;
};

struct Edge
{
	Node	from		= {},
			to			= {};

	int		distance	= 0; //can be manh and evkl
	
	bool operator>(const Edge& other) {
		return distance > other.distance;
	}
};

class Graph
{
public:
	std::string			net_id;
	std::vector<Node>	nodes = {};

	std::vector<Edge>	edges	= {}, //input 
						mst		= {}; //mst

	double				weight	= {};

	std::unordered_map<std::string, std::vector<Edge>> adj;
	std::unordered_map<std::string, std::string> parent;
public:
	std::string find_set(std::string i);
	void union_set(std::string u, std::string v);
	void kruskal();
	void primma();
};

class Process
{
public:
	Library				lib;
	std::vector<Graph>	graphs;
public:
	bool isEdgeCrossObstacles(const Edge& _edge);
	void parseGraphs(); //create graph and adding it to vector graphs
	void parseGraphsHanan();
public:
	void readGraphsFromFile(std::istream& in);
	void writeGraphsToFile(std::ostream& out);
};

