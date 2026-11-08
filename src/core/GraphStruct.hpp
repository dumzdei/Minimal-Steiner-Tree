#include "Configuration.hpp"
#include <map>
#include <string>
#include <vector>
#include <set>

/************************************************************************************
 *  @file   GraphStruct.hpp
 *  @brief  Description of data structures for working with graphs.
 ***********************************************************************************/

struct Node
{
public:
	int			x = 0,
				y = 0;
	std::string layer,
				id;
	bool operator==(Node& other){
		if (x == other.x && y == other.y)
			return true;
		return false;
	}
public:
	Node(const Terminal& term); //add new nodes from json
	Node(int x, int y); //add new steiner points. need to add 'layer' and 'id'
	~Node();
};

struct Edge
{
public:
	Node	*from,
			*to;

	int		distance	= 0; //can be manh and evkl
	
	bool operator>(const Edge& other) {
		return distance > other.distance;
	}
public:
	Edge(Node* from, Node* to);
	~Edge();
};

class Graph
{
public:
	std::string			net_id;
	std::vector<Node*>	nodes = {}; //all nodes stores here. dont use 'delete' to any containers

	std::vector<Edge*>	edges	= {}, //input.  all edges stores here. dont use 'delete' to any containers
						mst		= {}; //mst. stores edges from 'edges'. dont delete from here

	double				weight	= {};
	std::vector<Node*>		CandidateNodesToSteiner; // stores steiner nodes. dont have elements from 'nodes'. there are can be deleted.


	std::unordered_map<std::string, std::vector<Edge*>> adj;
	std::unordered_map<std::string, std::string> parent;
public:
	Graph(const Net& net);
	~Graph();

	std::string& find_set(std::string& i);
	void union_set(std::string u, std::string v); // <--- what is it? 
	void kruskal();
	void primma();
};

class Process
{
public:
	Library				lib;
	std::vector<Graph*>	graphs;	
public:
	~Process();
	
	bool isEdgeCrossObstacles(const Edge* _edge);
	void parseGraphs(); //create graph and adding it to vector graphs
	void parseGraphsHanan();
	void readGraphsFromFile(std::istream& in);
	void writeGraphsToFile(std::ostream& out);
};

