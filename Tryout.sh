
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=3
#SBATCH --time=25:00:00
#SBATCH --mem=80GB
#SBATCH --job-name=Disc_Model_Train
#SBATCH --mail-type=END
#SBATCH --mail-user=zg475@nyu.edu
#SBATCH --output=discsent_train_%j.out
#SBATCH --gres=gpu:1

module purge
module load pytorch/intel/20170724
time python Train.py -nm model_stripped  -data $SCRATCH/nlp-project/nlp-project-data/DiscSentEmbed/Data/GutenWiki -o $SCRATCH/nlp-project/nlp-project-data/DiscSentEmbed/Data/Logs -voc $SCRATCH/nlp-project/nlp-project-data/DiscSentEmbed/SortedVocab_stripped.pk -in_dim 300 -order -next -conj -bs 10000 -epochs 1 -n_batches 100