#include "Configuration.hpp"
#include "GraphStruct.hpp"
#include <iostream>
#include <fstream>


int main(int argc, char* argv[])
{
    Proccess* work = new Proccess;

    if (argc == 1) { return 0; }
    std::string input_path = argv[1];

    try {
        std::ifstream in(input_path);
        if (!in.is_open()) {
            return 1;
        }
        nlohmann::json j = nlohmann::json::parse(in);
        Library lib = j.get<Library>();
        std::cout << "Data from " << input_path << " successfully loaded" << std::endl;
        work->lib = lib;
        std::cout << "Data from " << input_path << "successfully loaded" << std::endl;
    }
    catch (const nlohmann::json::exception& e) {
        std::cerr << "Failed to parse JSON (ID: " << e.id << "): " << e.what() << std::endl;
        return 1;
    }

    switch (work->lib.steiner_params.hanan_grid_enabled)
    {
    case 0:
        work->parseGraph();
        break;
    case 1:
        work->parseGraph();
        break;
    }
    work->graphs[0].kruskal();

    Edge zalupa = { Node{ 0,0 },Node{ 5,5 } };
    bool flag = work->isEdgeCrossObstacles(zalupa);
    delete work;
    return 0;
}