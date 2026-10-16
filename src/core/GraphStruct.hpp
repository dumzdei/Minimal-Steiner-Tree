#include "Configuration.hpp"
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

};

class Graph
{
public:
	std::string			net_id;
	std::vector<Node>	points	= {};

	std::vector<Edge>	edges	= {}, //input 
						mst		= {}; //mst

	double				weight	= {};
public:
	void kruskal();
	void primma();
};

class Proccess
{
public:
	Library				lib;
	std::vector<Graph>	graphs;
public:

	void parseGraph(); //create graph and adding it to vector graphs
};
