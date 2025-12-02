
# pour lancer ./bench_final.sh platforme.xml nom_sortie_csv.csv


echo BENCHMARKING THE METHODS
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
# you can modify these values


p=4
q=2
P=$((p*q))
#generate_hostfile $P



# proper benchmark <--- this could be a TODO for students ? (as in, show weak scaling and/or strong scaling)
#mpi_options="-hostfile hostfiles/hostfile.$P.txt"
b=256
iter=1
traces="bench_traces"
out="bench_outputs"
csv=$2
echo m,n,k,b,p,q,algo,lookahead,gflops > $csv


for p in 1 2 3 4 5 12 16 
do
for q in 1 2 4 5 6 12 16 
do
P=$((p*q))
mpi_options="--cfg=smpi/host-speed:5Gf -platform platforms/$1 -hostfile hostfiles/cluster_hostfile.txt -np $P"

for i in 1 2 4 6 8 12
do
  n=$((i*b))
  m=$n
  k=$n
  la=0
  options="-c"

  for algo in p2p bcast
  do
    output=$(smpirun $mpi_options ./build/bin/main -p $p -q $q -n $n -b $b --algorithm $algo --niter $iter $options)
    result=$(echo "$output" | grep "^result:" | cut -d' ' -f2-)
    echo "$result" >> "$csv"
  done

  for la in $(seq 1 $((k/b)))
  do 
    algo="p2p-i-la"
    options="-c -l $la"
    output=$(smpirun $mpi_options ./build/bin/main -p $p -q $q -n $n -b $b --algorithm $algo --niter $iter $options)
    result=$(echo "$output" | grep "^result:" | cut -d' ' -f2-)
    echo "$result" >> "$csv"
  done
done
done
done