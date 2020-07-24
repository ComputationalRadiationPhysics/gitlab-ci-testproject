#!/usr/bin/env python3

from allpairspy import AllPairs
import argparse
import sys



parser = argparse.ArgumentParser(description='Generate tesing pairs')
parser.add_argument('-n', dest='n_pairs', default=1, action="store",
                    help='number of tuple elments')
parser.add_argument('--compact', dest='compact', action="store_true",
                    help='print compact')
args = parser.parse_args()
n_pairs = int(args.n_pairs)

examples = []
for i in sys.stdin:
    examples.append(i.rstrip())

def get_compiler_version(str):
    if str == "":
        return 0
    s = str.split("-")
    if len(s) == 2:
        return float(s[1])
    return 0

def get_cuda_version(str):
    if str == "":
        return 0
    return get_compiler_version(str)

def is_valid_combination(row):
    """
    This is a filtering function. Filtering functions should return True
    if combination is valid and False otherwise.

    Test row that is passed here can be incomplete.
    To prevent search for unnecessary items filtering function
    is executed with found subset of data to validate it.
    """
    n = len(row)

    if n >= 2:
        v_compiler = get_compiler_version(row[0])
        v_cuda = get_compiler_version(row[1])
        is_clang_cuda = False
        if row[0].split("-")[0].startswith("cuda.clang"):
            is_clang_cuda = True
        is_clang = False
        if row[0].split("-")[0].startswith("clang") or is_clang_cuda:
            is_clang = True
        is_gnu = False
        if row[0].split("-")[0] == "g++":
            is_gnu = True

        is_nvcc = False
        if row[0].split("-")[0].startswith("nvcc"):
            is_nvcc = True

        is_cuda = False
        if v_cuda != 0:
            is_cuda = True

        if not is_nvcc and not is_clang_cuda and is_cuda:
            return False

        if is_clang_cuda:
            if not is_cuda:
                return False
            if v_cuda == 9.2 and v_compiler >= 7:
                return True
            if v_cuda == 10.0 and v_compiler >= 8:
                return True
            if v_cuda == 10.1 and v_compiler >= 9:
                return True

            return False

        if is_cuda and is_nvcc:
            if v_cuda <= 10.1 and is_gnu and v_compiler <= 7:
                return True
            if v_cuda <= 10.2 and is_gnu and v_compiler <= 8:
                return True
            if v_cuda <= 11.0 and is_gnu and v_compiler <= 9:
                return True

            if v_cuda == 9.2 and is_clang and v_compiler <= 5:
                return True
            if v_cuda <= 10.2 and is_clang and v_compiler <= 8:
                return True
            if v_cuda <= 11.0 and is_clang:
                return False
            return False

    return True

clang_compiers = ["clang++-5.0", "clang++-6.0", "clang++-7", "clang++-8", "clang++-9", "clang++-10"]
gnu_compilers = ["g++-5", "g++-6", "g++-7", "g++-8", "g++-9"]
compilers = [
    clang_compiers,
    gnu_compilers
]

#generate clang cuda compiler
cuda_clang_compilers = []
for i in clang_compiers:
    cuda_clang_compilers.append("cuda."+i)
compilers.append(cuda_clang_compilers)

# nvcc compiler
cuda_nvcc_compilers = []
for i in clang_compiers:
    cuda_nvcc_compilers.append("nvcc."+i)
for i in gnu_compilers:
    cuda_nvcc_compilers.append("nvcc."+i)
compilers.append(cuda_nvcc_compilers)

backends = [  ("cuda",9.2), ("cuda",10.0), ("cuda",10.1), "cuda-10.2", "omp2b", "single"]
boost_libs = [ "1.65.1", "1.66.0", "1.67.0", "1.68.0", "1.69.0", "1.70.0", "1.71.0", "1.72.0", "1.73.0"]

rounds = 1
if n_pairs == 1:
    rounds = len(compilers)

for i in range(rounds):
    used_compilers = []
    if n_pairs == 1:
        used_compilers = compilers[i]
    else:
        for c in compilers:
            used_compilers += c

    parameters = [
        used_compilers,
        backends,
        boost_libs,
        examples
    ]

    for i, pairs in enumerate(AllPairs(parameters, filter_func=is_valid_combination, n=n_pairs)):
        if args.compact:
            print("{:2d}: {}".format(i, pairs))
        else:
            compiler=pairs[0]
            backend=pairs[1].split("-")[0]
            boost_version=pairs[2]
            folder=pairs[3]
            job_name=compiler+"_"+backend+"_"+boost_version+"_"+folder.replace("/",".")
            print(job_name+":")
            print("  variables:")
            print("    PIC_TEST_CASE_FOLDER: '" + folder + "'")
            print("    PIC_BACKEND: '" + backend + "'")
            print("    BOOST_VERSION: '" + boost_version + "'")
            print("    CXX_VERSION: '" + compiler + "'")
            print("")

