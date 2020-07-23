#!/bin/bash

# the default build type is Release
# if neccesary, you can rerun the pipeline with another build type-> https://docs.gitlab.com/ee/ci/pipelines.html#manually-executing-pipelines
# to change the build type, you must set the environment variable PIC_BUILD_TYPE
if [[ ! -v PIC_BUILD_TYPE ]] ; then
    PIC_BUILD_TYPE=Release ;
fi

###################################################
# cmake config builder
###################################################

PIC_CONST_ARGS=""
PIC_CONST_ARGS="${PIC_CONST_ARGS} -DCMAKE_BUILD_TYPE=${PIC_BUILD_TYPE}"
CMAKE_ARGS="${PIC_CONST_ARGS} ${PIC_CMAKE_ARGS} -DCMAKE_CXX_COMPILER=${CXX_VERSION} -DBOOST_ROOT=/opt/boost/${BOOST_VERSION}"

###################################################
# build an run tests
###################################################

# use one build directory for all build configurations
cd $HOME
mkdir buildCI
cd buildCI

export picongpu_DIR=$CI_PROJECT_DIR
export PATH=$picongpu_DIR/bin:$PATH

PIC_PARALLEL_BUILDS=$(nproc)
# limit to 8 parallel builds to avoid out of memory errors
if [ $PIC_PARALLEL_BUILDS -gt 8 ] ; then
    PIC_PARALLEL_BUILDS=8
fi
echo -e "\033[0;32m///////////////////////////////////////////////////"
echo "number of processor threads -> $(nproc)"
echo "number of parallel builds -> $PIC_PARALLEL_BUILDS"
echo "cmake version   -> $(cmake --version | head -n 1)"
echo "build directory -> $(pwd)"
echo "CMAKE_ARGS      -> ${CMAKE_ARGS}"
echo "accelerator     -> ${PIC_BACKEND}"
echo "input set       -> ${PIC_TEST_CASE_FOLDER}"
echo -e "/////////////////////////////////////////////////// \033[0m \n\n"

sleep 20
