#include "core/GraphStruct.hpp"

#include <cassert>
#include <iostream>

int main() {
    Node start(1, 2);
    Node same_coordinates(1, 2);
    Node finish(4, 6);
    Edge route(&start, &finish);

    assert(route.distance == 7);
    assert(start == same_coordinates);
    assert(!(start == finish));

    Edge short_route(&start, &start);
    assert(route > short_route);

    std::cout << "GraphStructTests passed\n";
    return 0;
}
