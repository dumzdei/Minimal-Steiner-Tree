#include "Configuration.hpp"
#include <iostream>
#include <fstream>


int main(int argc, char* argv[])
{
    if (argc == 1) { return 0; }
    std::string input_path = argv[1];

    try {
        std::ifstream in(input_path);
        if (!in.is_open()) {
            throw std::runtime_error("Can't open file.\n");
        }
        nlohmann::json j = nlohmann::json::parse(in);
        Library task = j.get<Library>();
        std::cout << "Data from " << input_path << "successfully loaded" << std::endl;
    }
    catch (const nlohmann::json::exception& e) {
        std::cerr << "Failed to parse JSON (ID: " << e.id << "): " << e.what() << std::endl;
        return 1;
    }

    return 0;
}