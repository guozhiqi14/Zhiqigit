mkdir py_env
cd py_env/
virtualenv py_env
cd py_env
source bin/activate
pip install pytorch


scp -r yz1349@prince.hpc.nyu.edu:/scratch/yz1349/DiscSentEmbed zg475@prince.hpc.nyu.edu:/scratch/zg475 
sbatch train_joint.sh 
squeue -u zg475

transit server name: prince.hpc.nyu.edu