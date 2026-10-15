cmake_minimum_required(VERSION 3.15)
project(SteinerRouting CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set_property(GLOBAL PROPERTY USE_FOLDERS ON)

set_property(GLOBAL PROPERTY PREDEFINED_TARGETS_FOLDER "CMakePredefinedTargets")

file(GLOB_RECURSE CPP_FILES "src/*.cpp")
file(GLOB_RECURSE HPP_FILES "src/*.hpp" "src/*.h")

set(ALL_PROJECT_FILES ${CPP_FILES} ${HPP_FILES})

if(NOT ALL_PROJECT_FILES)
    message(FATAL_ERROR "False cant find source files/!")
endif()

add_executable(SteinerTree ${ALL_PROJECT_FILES})


set_target_properties(SteinerTree PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY         "${CMAKE_CURRENT_SOURCE_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_CURRENT_SOURCE_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG   "${CMAKE_CURRENT_SOURCE_DIR}"
)

target_include_directories(SteinerTree PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/src/core
    ${CMAKE_CURRENT_SOURCE_DIR}/src/algorithms
)

source_group(TREE "${CMAKE_CURRENT_SOURCE_DIR}" PREFIX "Source Files" FILES ${CPP_FILES})
source_group(TREE "${CMAKE_CURRENT_SOURCE_DIR}" PREFIX "Header Files" FILES ${HPP_FILES})

