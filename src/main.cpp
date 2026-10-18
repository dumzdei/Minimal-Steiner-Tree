#include "Configuration.hpp"
#include "GraphStruct.hpp"
#include <iostream>
#include <fstream>


int main(int argc, char* argv[])
{
    Process* work = new Process;

    std::string output_path = argv[2];
    std::ofstream out(output_path);

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
    //case 0:
    //    work->parseGraph();
    //    work->printGraph(out);
    //    break;
    //case 1:
    //    work->parseGraph();
    //    work->printGraph(out);
    //    
    //    break;
    }
    work->parseGraph();
    work->graphs[0].primma();
    work->printGraph(out);
    delete work;
    return 0;
}