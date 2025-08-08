cmake_minimum_required(VERSION 3.10)
project(RedstarCppClient VERSION 1.0.0)

# Set C++ standard
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Platform-specific settings
if(WIN32)
    # Windows-specific settings
    add_definitions(-D_WIN32_WINNT=0x0601)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /EHsc")
else()
    # Unix-like systems (Linux, macOS)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -O2")
endif()

# Create the library
add_library(redstar_client STATIC
    RedstarClient.cpp
    RedstarClient.h
)

# Create the shared library as well
add_library(redstar_client_shared SHARED
    RedstarClient.cpp
    RedstarClient.h
)

# Set the output name for shared library
set_target_properties(redstar_client_shared PROPERTIES OUTPUT_NAME redstar_client)

# Include directories
target_include_directories(redstar_client PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_include_directories(redstar_client_shared PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# Platform-specific linking
if(WIN32)
    target_link_libraries(redstar_client ws2_32)
    target_link_libraries(redstar_client_shared ws2_32)
else()
    # Unix-like systems
    find_package(Threads REQUIRED)
    target_link_libraries(redstar_client ${CMAKE_THREAD_LIBS_INIT})
    target_link_libraries(redstar_client_shared ${CMAKE_THREAD_LIBS_INIT})
endif()

# Create example executable
add_executable(redstar_example example.cpp)
target_link_libraries(redstar_example redstar_client)

# Create test executable
add_executable(redstar_test test.cpp)
target_link_libraries(redstar_test redstar_client)

# Install targets
install(TARGETS redstar_client redstar_client_shared
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin)

install(FILES RedstarClient.h
        DESTINATION include)

# Package configuration
include(CMakePackageConfigHelpers)

configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/RedstarClientConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/RedstarClientConfig.cmake"
    INSTALL_DESTINATION lib/cmake/RedstarClient
)

write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/RedstarClientConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY AnyNewerVersion
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/RedstarClientConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/RedstarClientConfigVersion.cmake"
    DESTINATION lib/cmake/RedstarClient
)

# CPack configuration
set(CPACK_PACKAGE_NAME "RedstarCppClient")
set(CPACK_PACKAGE_VERSION "${PROJECT_VERSION}")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "C++ client library for Redstar Redis-compatible server")
set(CPACK_PACKAGE_VENDOR "Redstar Project")
set(CPACK_PACKAGE_CONTACT "team@redstar.project")
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE")

if(WIN32)
    set(CPACK_GENERATOR "ZIP;NSIS")
else()
    set(CPACK_GENERATOR "TGZ;DEB;RPM")
endif()

include(CPack)