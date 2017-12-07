#!/bin/bash
#
#SBATCH --nodes=1
#SBATCH --cpus-per-task=3
#SBATCH --time=25:00:00
#SBATCH --mem=80GB
#SBATCH --job-name=tunemodel3
#SBATCH --mail-type=END
#SBATCH --mail-user=lx557@nyu.edu
#SBATCH --output=slurm_%j.out
module purge
module load spacy/intel/1.8.2
module load pytorch/intel/20170724
module load nltk/3.2.2

time python Turning_model3.py --hidden_dim '25 50 75' --learning_rate '0.01 0.005 0.001' --window_size '2 3 4 5'







module spider pytorch #check module path



#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=2:00:00
#SBATCH --mem=20GB
#SBATCH --job-name=DiscSent_evaluation
#SBATCH --mail-type=END
#SBATCH --mail-user=wz1070@nyu.edu
#SBATCH --output=discsent_evaluation_%j.out
#SBATCH --gres=gpu:1

#module purge
#module load pytorch/python3.6/0.2.0_3
source $SCRATCH/nlp-project/nlp-project-data/py2.7/bin/activate
RUNDIR=$SCRATCH/nlp-project/nlp-project-data/sentence-representation
#module load python/intel/2.7.12 pytorch/0.2.0_1 protobuf/intel/3.1.0
#PYTHONPATH=$PYTHONPATH:. python $RUNDIR/DiscSent/Train.py -nm model_stripped  -data $SCRATCH/nlp-project/nlp-project-data/DiscSentEmbed/Data/GutenWiki -o $SCRATCH/nlp-project/nlp-project-data/DiscSentEmbed/Data/Logs -voc $SCRATCH/nlp-project/nlp-project-data/DiscSentEmbed/SortedVocab_stripped.pk -in_dim 300 -order -next -conj -bs 10000 -epochs 1 -n_batches 100
python $RUNDIR/DiscSent/Evaluate.py -data $SCRATCH/nlp-project/nlp-project-data/DiscSentEmbed/Data/GutenWiki -model $SCRATCH/nlp-project/nlp-project-data/DiscSentEmbed/Data/Logs/model_2017-11-30_122947_077902 -sf _99