#include "Configuration.hpp"
/************************************************************************************
 *  @file   GraphStruct.hpp
 *  @brief  File 
 ***********************************************************************************/

struct Node
{
	int			x = 0,
				y = 0;

	std::string layer;

};

struct Edges
{
	Node	from		= {},
			to			= {};

	int		distance	= 0; //can be manh and evkl

};

struct Graph
{
	std::string			net_id;
	std::vector<Node>	points	= {};
	std::vector<Edges>	edges	= {};
	double				weight	= {};
};

//proccess:
class proccess
{
	Library				lib;
	std::vector<Graph>	graphs;


};
Graph parseGraph()
{

}