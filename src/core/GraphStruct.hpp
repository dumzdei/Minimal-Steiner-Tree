#include "Configuration.hpp"
#include <map>
#include <string>
#include <vector>
#include <set>
#include <unordered_map>

/**
 * @file GraphStruct.hpp
 * @brief Модели графа и операции для построения маршрутов.
 */

class Process;

/** @brief Вершина графа с координатами и метаданными терминала. */
struct Node
{
public:
	int			x = 0,
				y = 0;
	std::string layer,
				id;

	/**
	 * @brief Сравнивает координаты двух вершин.
	 * @param other Вершина для сравнения.
	 * @return `true`, если координаты совпадают.
	 */
	bool operator==(Node& other){
		if (x == other.x && y == other.y)
			return true;
		return false;
	}
public:
	/** @brief Создаёт вершину из терминала входной конфигурации. */
	Node(const Terminal& term);

	/**
	 * @brief Создаёт точку Штейнера по координатам.
	 * @param x Горизонтальная координата.
	 * @param y Вертикальная координата.
	 */
	Node(int x, int y);
	~Node();
};

/** @brief Ребро между двумя вершинами с манхэттенской длиной. */
struct Edge
{
public:
	Node	*from,
			*to;

	int		distance	= 0;

	/**
	 * @brief Сравнивает рёбра по длине.
	 * @param other Ребро для сравнения.
	 * @return `true`, если текущее ребро длиннее.
	 */
	bool operator>(const Edge& other) {
		return distance > other.distance;
	}
public:
	/**
	 * @brief Создаёт ребро и вычисляет его манхэттенскую длину.
	 * @param from Начальная вершина.
	 * @param to Конечная вершина.
	 */
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
	Graph(Process* work, const Net& net);
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

