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

include(CTest)
if(BUILD_TESTING)
    add_executable(GraphStructTests
        tests/cpp/graph_struct_tests.cpp
        src/core/GraphStruct.cpp
    )
    target_include_directories(GraphStructTests PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
        ${CMAKE_CURRENT_SOURCE_DIR}/src/core
    )
    add_test(NAME GraphStructTests COMMAND GraphStructTests)
endif()


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

if(WIN32 AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/.venv/Scripts/python.exe")
    set(STEINER_GUI_PYTHON "${CMAKE_CURRENT_SOURCE_DIR}/.venv/Scripts/python.exe")
else()
    find_package(Python3 REQUIRED COMPONENTS Interpreter)
    set(STEINER_GUI_PYTHON "${Python3_EXECUTABLE}")
endif()

add_custom_target(SteinerTreeGUI
    COMMAND "${STEINER_GUI_PYTHON}" -m PyInstaller
        --noconfirm
        --clean
        --onedir
        --windowed
        --name SteinerTreeGUI
        --distpath "${CMAKE_CURRENT_SOURCE_DIR}"
        --workpath "${CMAKE_CURRENT_BINARY_DIR}/gui-build"
        --specpath "${CMAKE_CURRENT_BINARY_DIR}/gui-spec"
        "--add-data=${CMAKE_CURRENT_SOURCE_DIR}/input$<SEMICOLON>input"
        "--add-binary=$<TARGET_FILE:SteinerTree>$<SEMICOLON>."
        "${CMAKE_CURRENT_SOURCE_DIR}/gui/gui.py"
    DEPENDS SteinerTree
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    COMMENT "Создание GUI-приложения SteinerTreeGUI.exe"
    VERBATIM
)

