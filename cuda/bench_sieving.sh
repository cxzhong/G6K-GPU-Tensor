DEFINES="-Xcompiler -DMAX_SIEVING_DIM=160 -Xcompiler -DGPUVECNUM=131072 -Xcompiler -DHAVE_CUDA -I../parallel-hashmap" #-Xcompiler -DDEBUG_BENCHMARK"

# Allow overriding target SMs via environment, e.g., SMS="86 89"
SMS_LIST=${SMS_LIST:-"75"}
GENCODE_FLAGS=""
for sm in $SMS_LIST; do
  GENCODE_FLAGS="$GENCODE_FLAGS -gencode arch=compute_${sm},code=sm_${sm}"
done
HIGHEST_SM=$(echo $SMS_LIST | awk '{print $NF}')
if [ -n "$HIGHEST_SM" ]; then
  GENCODE_FLAGS="$GENCODE_FLAGS -gencode arch=compute_${HIGHEST_SM},code=compute_${HIGHEST_SM}"
fi

if [ -z "$1" ]
then
    /usr/local/cuda/bin/nvcc -ccbin g++ -Xcompiler -fPIC -Xcompiler -Ofast -Xcompiler -march=native -Xcompiler -pthread -Xcompiler -Wall -Xcompiler -Wextra $DEFINES -std=c++14 -O3 --use_fast_math -Xptxas=-O3,-dlcm=ca $GENCODE_FLAGS -lineinfo -I/usr/local/cuda/include -c ../cuda/GPUStreamGeneral.cu -o GPUStreamGeneral.o
fi

/usr/local/cuda/bin/nvcc -ccbin g++ -Xcompiler -fPIC -Xcompiler -Ofast -Xcompiler -march=native -Xcompiler -pthread -Xcompiler -Wall -Xcompiler -Wextra $DEFINES -std=c++14 -O3 --use_fast_math -Xptxas=-O3,-dlcm=ca $GENCODE_FLAGS -lineinfo -I/usr/local/cuda/include -lcublas -lcurand --resource-usage bench_sieving.cpp -o bench_sieving GPUStreamGeneral.o

/usr/local/cuda/bin/nvcc -ccbin g++ -Xcompiler -fPIC -Xcompiler -Ofast -Xcompiler -march=native -Xcompiler -pthread -Xcompiler -Wall -Xcompiler -Wextra $DEFINES -std=c++14 -O3 --use_fast_math -Xptxas=-O3,-dlcm=ca $GENCODE_FLAGS -lineinfo -I/usr/local/cuda/include -lcublas -lcurand --resource-usage bench_quality.cpp -o bench_quality GPUStreamGeneral.o
