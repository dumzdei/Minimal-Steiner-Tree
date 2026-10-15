#include <vector>
#include <string>
#include "json.hpp"

/************************************************************************************
 *  @file   Configuration.hpp
 *  @brief  ���� �������� �������� ��������, ���������� ���������� �� json.
 ***********************************************************************************/

struct Layer {
    std::string id,
                name,
                direction;

    double      cost_multiplier = 0;
};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Layer, id, name, direction, cost_multiplier)


struct Design
{
    int                grid_width   = 0,
                       grid_height  = 0,
                       grid_unit    = 0;

    std::vector<Layer> layers       = {};
    double via_cost = 0;
};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Design, grid_width, grid_height, grid_unit, layers, via_cost)


struct Obstacle
{
    std::string id,
                layer;

    int     x_start = 0,
            y_start = 0,
            x_end   = 0,
            y_end   = 0;
};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Obstacle, id, layer, x_start, y_start, x_end, y_end)

struct Terminal
{
    std::string id,
                layer;

    int         x = 0,
                y = 0;
};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Terminal, id, layer, x, y)


struct Net
{
    std::string net_id;
    double weight = 0;
    std::vector<Terminal> terminals = {};
};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Net, net_id, weight, terminals)


struct SteinerParams
{
    std::string algorithm,
                point_generation,
                routing_model,
                mst_method;

    bool        hanan_grid_enabled              = false,
                obstacle_aware                  = false,
                multi_layer                     = false,
                mst_baseline                    = false,
                allow_diagonal                  = false,
                preferred_direction_enforcement = false,
                post_optimization               = false;

    int         improvement_iterations          = 0,
                max_steiner_points              = 0;

    double      convergence_tol                 = 0,
                bend_penalty                    = 0,
                min_improvement_percent         = 0;
    std::vector<std::string> post_opt_methods   = {};
};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(SteinerParams, algorithm, point_generation, routing_model,
    mst_method, hanan_grid_enabled, obstacle_aware, multi_layer, mst_baseline, allow_diagonal,
    preferred_direction_enforcement, post_optimization, improvement_iterations, max_steiner_points,
    convergence_tol, bend_penalty, min_improvement_percent, post_opt_methods)

struct Library
{
    Design                  design          = {};
    std::vector<Obstacle>   obstacles       = {};
    std::vector<Net>        nets            = {};
    SteinerParams           steiner_params  = {};
};
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Library, design, obstacles, nets, steiner_params)