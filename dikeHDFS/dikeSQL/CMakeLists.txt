cmake_minimum_required(VERSION 3.0.0)
project(dikeSQL VERSION 0.1.0)


add_library(libdikeSQL STATIC 
#            sqlite3.c 
            dikeSQLite3.c    
            sqlite3ext.h sqlite3.h
            StreamReader.cpp StreamReader.hpp
            DikeSQL.cpp DikeSQL.hpp
            )

include_directories(
        . 
        ../src
        ${CMAKE_SOURCE_DIR}/external/poco/Foundation/include 
        ${CMAKE_SOURCE_DIR}/external/poco/Util/include
        ${CMAKE_SOURCE_DIR}/external/poco/Net/include
        )

target_compile_options(libdikeSQL PRIVATE 
#        -DSQLITE_THREADSAFE=1 
        -DSQLITE_THREADSAFE=0
        -DSQLITE_ENABLE_MEMSYS5 
#        -DSQLITE_ENABLE_JSON1 
#        -DSQLITE_ENABLE_RTREE 
#        -DSQLITE_ENABLE_EXPLAIN_COMMENTS 
        -DHAVE_USLEEP -DSQLITE_CORE -DSQLITE_OMIT_LOAD_EXTENSION=1 
        -fmax-errors=1)


#add_executable(testDikeSQL testDikeSQL.cpp)
#target_link_libraries(testDikeSQL PUBLIC  libdikeSQL "-lpthread -lm" )

